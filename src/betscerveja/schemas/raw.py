"""Contratos da extração bruta."""

from __future__ import annotations

import pandas as pd
import pandera.pandas as pa
from pandera.typing import Series


class RawExtract(pa.DataFrameModel):
    source_id: Series[str]
    metodo: Series[str]
    pagina: Series[pd.Int64Dtype] = pa.Field(nullable=True)
    trecho: Series[str] = pa.Field(nullable=True)
    tabela_idx: Series[pd.Int64Dtype] = pa.Field(nullable=True)
    celulas_json: Series[str] = pa.Field(nullable=True)

    class Config:
        coerce = True


class RawApiSeries(pa.DataFrameModel):
    source_id: Series[str]
    metodo: Series[str]
    periodo: Series[str]
    localidade_id: Series[str] = pa.Field(nullable=True)
    localidade_nome: Series[str] = pa.Field(nullable=True)
    variavel_id: Series[str] = pa.Field(nullable=True)
    variavel_nome: Series[str] = pa.Field(nullable=True)
    classificacao_id: Series[str] = pa.Field(nullable=True)
    classificacao_nome: Series[str] = pa.Field(nullable=True)
    categoria_id: Series[str] = pa.Field(nullable=True)
    categoria_nome: Series[str] = pa.Field(nullable=True)
    valor: Series[pd.Float64Dtype] = pa.Field(nullable=True)
    unidade: Series[str] = pa.Field(nullable=True)

    class Config:
        coerce = True
