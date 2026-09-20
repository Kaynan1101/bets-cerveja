"""Contratos pandera das saídas SARIMAX (etapa 8)."""

from __future__ import annotations

import pandas as pd
import pandera.pandas as pa
from pandera.typing import Series


class FctCervejaPrevisao(pa.DataFrameModel):
    data_inicio: Series[pd.Timestamp]
    realizado: Series[pd.Float64Dtype] = pa.Field(nullable=True)
    previsto: Series[float]
    ic_inf: Series[float]
    ic_sup: Series[float]
    dentro_do_intervalo: Series[pd.BooleanDtype] = pa.Field(nullable=True)

    class Config:
        coerce = True
        unique = ["data_inicio"]


class MlMetricas(pa.DataFrameModel):
    execucao_id: Series[str]
    timestamp: Series[pd.Timestamp]
    ordem: Series[str]
    ordem_sazonal: Series[str]
    aic: Series[float]
    bic: Series[float]
    n_train: Series[pd.Int64Dtype]
    n_forecast: Series[pd.Int64Dtype]
    alvo: Series[str]
    exogenas: Series[str]

    class Config:
        coerce = True
        unique = ["execucao_id"]


class MlCoeficientes(pa.DataFrameModel):
    execucao_id: Series[str]
    regressor: Series[str]
    coeficiente: Series[float]
    erro_padrao: Series[pd.Float64Dtype] = pa.Field(nullable=True)
    p_valor: Series[pd.Float64Dtype] = pa.Field(nullable=True)
    ic_inf: Series[pd.Float64Dtype] = pa.Field(nullable=True)
    ic_sup: Series[pd.Float64Dtype] = pa.Field(nullable=True)

    class Config:
        coerce = True
        unique = ["execucao_id", "regressor"]
