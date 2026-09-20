from __future__ import annotations

import duckdb
import numpy as np
import pandas as pd
import pytest
from pandera.errors import SchemaError

from betscerveja.models.sarimax import TARGET, fit_sarimax, run_forecast
from betscerveja.schemas.ml import FctCervejaPrevisao, MlCoeficientes, MlMetricas


def _synthetic_dataset(end: str = "2024-12-01") -> pd.DataFrame:
    dates = pd.date_range("2012-01-01", end, freq="MS")
    t = np.arange(len(dates), dtype=float)
    seasonal = 5 * np.sin(2 * np.pi * t / 12)
    ipca = 100 + 0.2 * t
    rend = 2800 + 2 * t
    y = 90 + 0.05 * t + seasonal + 0.02 * ipca + 0.001 * rend
    return pd.DataFrame(
        {
            "data_inicio": dates,
            "producao_bebidas_alcoolicas_indice": y,
            "ipca_cerveja": ipca,
            "rendimento_real": rend,
        }
    )


def test_previsao_unique_em_data_inicio() -> None:
    frame = pd.DataFrame(
        {
            "data_inicio": pd.to_datetime(["2023-01-01", "2023-01-01"]),
            "realizado": [1.0, 2.0],
            "previsto": [1.0, 2.0],
            "ic_inf": [0.0, 0.0],
            "ic_sup": [3.0, 3.0],
            "dentro_do_intervalo": [True, True],
        }
    )
    with pytest.raises(SchemaError):
        FctCervejaPrevisao.validate(frame)


def test_metricas_unique_em_execucao_id() -> None:
    row = {
        "execucao_id": "a",
        "timestamp": pd.Timestamp("2026-01-01"),
        "ordem": "(1, 1, 1)",
        "ordem_sazonal": "(1, 0, 0, 12)",
        "aic": 1.0,
        "bic": 2.0,
        "n_train": 10,
        "n_forecast": 2,
        "alvo": TARGET,
        "exogenas": "ipca_cerveja,rendimento_real",
    }
    with pytest.raises(SchemaError):
        MlMetricas.validate(pd.DataFrame([row, row]))


def test_coeficientes_unique_em_execucao_e_regressor() -> None:
    row = {
        "execucao_id": "a",
        "regressor": "ipca_cerveja",
        "coeficiente": 0.1,
        "erro_padrao": 0.01,
        "p_valor": 0.5,
        "ic_inf": 0.0,
        "ic_sup": 0.2,
    }
    with pytest.raises(SchemaError):
        MlCoeficientes.validate(pd.DataFrame([row, row]))


def test_fit_sarimax_grain_e_exogenas() -> None:
    previsao, metricas, coeficientes = fit_sarimax(_synthetic_dataset())
    FctCervejaPrevisao.validate(previsao)
    MlMetricas.validate(metricas)
    MlCoeficientes.validate(coeficientes)
    assert previsao["data_inicio"].is_unique
    assert metricas["execucao_id"].is_unique
    assert not coeficientes.duplicated(["execucao_id", "regressor"]).any()
    assert metricas["n_train"].iloc[0] == 132
    assert metricas["n_forecast"].iloc[0] == 24
    nomes = set(coeficientes["regressor"])
    assert {"ipca_cerveja", "rendimento_real"} <= nomes
    assert previsao["data_inicio"].min() == pd.Timestamp("2023-01-01")
    assert previsao["ic_inf"].le(previsao["ic_sup"]).all()
    assert metricas["alvo"].iloc[0] == TARGET
    assert "producao_industrial_geral_indice" not in coeficientes["regressor"].to_numpy()


def test_run_forecast_escreve_marts_ml(tmp_path) -> None:
    db = tmp_path / "betscerveja.duckdb"
    frame = _synthetic_dataset()
    con = duckdb.connect(str(db))
    con.execute("create schema marts_ml")
    con.register("_ds", frame)
    con.execute("create table marts_ml.ml_dataset_cerveja_mensal as select * from _ds")
    con.close()

    summary = run_forecast(db)
    con = duckdb.connect(str(db), read_only=True)
    previsao = con.execute("select * from marts_ml.fct_cerveja_previsao").fetchdf()
    metricas = con.execute("select * from marts_ml.ml_metricas").fetchdf()
    coefs = con.execute("select * from marts_ml.ml_coeficientes").fetchdf()
    cols = [
        row[0]
        for row in con.execute(
            "select column_name from information_schema.columns "
            "where table_name = 'ml_dataset_cerveja_mensal'"
        ).fetchall()
    ]
    con.close()

    assert "producao_industrial_geral_indice" not in cols
    assert len(metricas) == 1
    assert summary["execucao_id"] == metricas["execucao_id"].iloc[0]
    assert previsao["data_inicio"].is_unique
    assert {"realizado", "previsto", "ic_inf", "ic_sup", "dentro_do_intervalo"} <= set(
        previsao.columns
    )
    assert {"ipca_cerveja", "rendimento_real"} <= set(coefs["regressor"])
