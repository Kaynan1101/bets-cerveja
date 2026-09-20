"""SARIMAX contrafactual da produção de bebidas alcoólicas (etapa 8)."""

from __future__ import annotations

import os
import uuid
import warnings
from datetime import UTC, datetime
from pathlib import Path

import duckdb
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

from betscerveja.registry import REPO_ROOT
from betscerveja.schemas.ml import FctCervejaPrevisao, MlCoeficientes, MlMetricas

TARGET = "producao_bebidas_alcoolicas_indice"
EXOGS = ("ipca_cerveja", "rendimento_real")
TRAIN_START_FORECAST = pd.Timestamp("2023-01-01")
FORECAST_END = pd.Timestamp("2026-12-01")
DATASET_TABLE = "ml_dataset_cerveja_mensal"
DEFAULT_DUCKDB = REPO_ROOT / "warehouse" / "betscerveja.duckdb"

# Grid pequeno: uma execução no fim, a ordem vencedora por AIC.
ORDER_GRID: tuple[tuple[tuple[int, int, int], tuple[int, int, int, int]], ...] = (
    ((0, 1, 1), (0, 1, 1, 12)),
    ((1, 1, 0), (1, 1, 0, 12)),
    ((1, 1, 1), (0, 1, 1, 12)),
    ((1, 1, 1), (1, 0, 0, 12)),
    ((0, 1, 1), (1, 1, 0, 12)),
    ((1, 0, 1), (0, 1, 1, 12)),
)


def duckdb_path(path: Path | str | None = None) -> Path:
    if path is not None:
        return Path(path)
    env = os.environ.get("BETSCERVEJA_DUCKDB_PATH")
    if env:
        return Path(env)
    return DEFAULT_DUCKDB


def run_forecast(path: Path | str | None = None) -> dict[str, object]:
    """Lê `ml_dataset_cerveja_mensal`, treina um SARIMAX e grava as três saídas."""
    db_path = duckdb_path(path)
    if not db_path.exists():
        raise FileNotFoundError(f"DuckDB não encontrado: {db_path}")

    con = duckdb.connect(str(db_path), read_only=False)
    try:
        schema = _ml_schema(con)
        dataset = con.execute(
            f'select * from "{schema}"."{DATASET_TABLE}" order by data_inicio'
        ).fetchdf()
        previsao, metricas, coeficientes = fit_sarimax(dataset)
        FctCervejaPrevisao.validate(previsao)
        MlMetricas.validate(metricas)
        MlCoeficientes.validate(coeficientes)
        _write_table(con, schema, "fct_cerveja_previsao", previsao)
        _write_table(con, schema, "ml_metricas", metricas)
        _write_table(con, schema, "ml_coeficientes", coeficientes)
    finally:
        con.close()

    return {
        "duckdb": str(db_path),
        "schema": schema,
        "n_forecast": int(metricas["n_forecast"].iloc[0]),
        "ordem": metricas["ordem"].iloc[0],
        "ordem_sazonal": metricas["ordem_sazonal"].iloc[0],
        "aic": float(metricas["aic"].iloc[0]),
        "execucao_id": metricas["execucao_id"].iloc[0],
    }


def fit_sarimax(
    dataset: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    frame = dataset.copy()
    frame["data_inicio"] = pd.to_datetime(frame["data_inicio"])
    frame = frame.sort_values("data_inicio").drop_duplicates("data_inicio")
    missing = {TARGET, *EXOGS} - set(frame.columns)
    if missing:
        raise ValueError(f"dataset sem colunas {sorted(missing)}")

    train = frame.loc[frame["data_inicio"] < TRAIN_START_FORECAST].copy()
    horizon = frame.loc[
        (frame["data_inicio"] >= TRAIN_START_FORECAST) & (frame["data_inicio"] <= FORECAST_END)
    ].copy()
    if train.empty:
        raise ValueError("treino vazio: precisa de meses com data_inicio < 2023-01-01")
    if horizon.empty:
        raise ValueError("horizonte vazio: precisa de meses com exógenas a partir de 2023-01-01")

    train_idx = train.set_index("data_inicio")
    horizon_idx = horizon.set_index("data_inicio")
    endog = train_idx[TARGET].astype(float)
    exog_train = train_idx[list(EXOGS)].astype(float)
    exog_forecast = horizon_idx[list(EXOGS)].astype(float)

    best = _select_by_aic(endog, exog_train)
    result = best["result"]
    order = best["order"]
    seasonal = best["seasonal_order"]

    forecast = result.get_forecast(steps=len(horizon_idx), exog=exog_forecast)
    mean = pd.Series(forecast.predicted_mean.values, index=horizon_idx.index)
    ci = forecast.conf_int(alpha=0.05)
    ci.index = horizon_idx.index
    ic_inf = ci.iloc[:, 0]
    ic_sup = ci.iloc[:, 1]
    realizado = horizon_idx[TARGET].astype("float64")
    dentro = pd.Series(pd.NA, index=horizon_idx.index, dtype="boolean")
    observed = realizado.notna()
    dentro.loc[observed] = (realizado.loc[observed] >= ic_inf.loc[observed]) & (
        realizado.loc[observed] <= ic_sup.loc[observed]
    )

    previsao = pd.DataFrame(
        {
            "data_inicio": horizon_idx.index,
            "realizado": realizado.astype("Float64").to_numpy(),
            "previsto": mean.astype(float).to_numpy(),
            "ic_inf": ic_inf.astype(float).to_numpy(),
            "ic_sup": ic_sup.astype(float).to_numpy(),
            "dentro_do_intervalo": dentro.to_numpy(),
        }
    )

    execucao_id = str(uuid.uuid4())
    metricas = pd.DataFrame(
        [
            {
                "execucao_id": execucao_id,
                "timestamp": pd.Timestamp(datetime.now(UTC)).tz_localize(None),
                "ordem": str(order),
                "ordem_sazonal": str(seasonal),
                "aic": float(result.aic),
                "bic": float(result.bic),
                "n_train": int(len(train)),
                "n_forecast": int(len(horizon)),
                "alvo": TARGET,
                "exogenas": ",".join(EXOGS),
            }
        ]
    )
    coeficientes = _coeficientes(result, execucao_id)
    return previsao, metricas, coeficientes


def _select_by_aic(endog: pd.Series, exog: pd.DataFrame) -> dict:
    ranked: list[dict] = []
    for order, seasonal_order in ORDER_GRID:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = SARIMAX(
                    endog,
                    exog=exog,
                    order=order,
                    seasonal_order=seasonal_order,
                    enforce_stationarity=False,
                    enforce_invertibility=False,
                )
                result = model.fit(disp=False, maxiter=200)
            if result.aic is None or pd.isna(result.aic):
                continue
            ranked.append(
                {
                    "order": order,
                    "seasonal_order": seasonal_order,
                    "aic": float(result.aic),
                    "result": result,
                }
            )
        except Exception as exc:
            if isinstance(exc, KeyboardInterrupt):
                raise
            continue
    if not ranked:
        raise RuntimeError("nenhum candidato SARIMAX convergiu no grid")
    ranked.sort(key=lambda item: item["aic"])
    return ranked[0]


def _coeficientes(result, execucao_id: str) -> pd.DataFrame:
    conf = result.conf_int()
    rows = []
    for name in result.params.index:
        ic_row = conf.loc[name] if name in conf.index else (pd.NA, pd.NA)
        bse = result.bse.get(name) if hasattr(result.bse, "get") else result.bse[name]
        pval = result.pvalues.get(name) if hasattr(result.pvalues, "get") else result.pvalues[name]
        rows.append(
            {
                "execucao_id": execucao_id,
                "regressor": str(name),
                "coeficiente": float(result.params[name]),
                "erro_padrao": None if pd.isna(bse) else float(bse),
                "p_valor": None if pd.isna(pval) else float(pval),
                "ic_inf": None if pd.isna(ic_row[0]) else float(ic_row[0]),
                "ic_sup": None if pd.isna(ic_row[1]) else float(ic_row[1]),
            }
        )
    return pd.DataFrame(rows)


def _ml_schema(con: duckdb.DuckDBPyConnection) -> str:
    found = con.execute(
        """
        select table_schema
        from information_schema.tables
        where lower(table_name) = 'ml_dataset_cerveja_mensal'
        order by case when table_schema like '%marts_ml%' then 0 else 1 end
        limit 1
        """
    ).fetchone()
    if found:
        return found[0]
    con.execute("create schema if not exists marts_ml")
    return "marts_ml"


def _write_table(
    con: duckdb.DuckDBPyConnection,
    schema: str,
    name: str,
    frame: pd.DataFrame,
) -> None:
    con.execute(f'create schema if not exists "{schema}"')
    con.register("_betscerveja_ml_frame", frame)
    qualified = f'"{schema}"."{name}"'
    con.execute(f"create or replace table {qualified} as select * from _betscerveja_ml_frame")
    con.unregister("_betscerveja_ml_frame")
