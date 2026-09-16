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
