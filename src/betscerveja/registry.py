"""Registro declarativo de fontes em conf/sources.yml."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCES_PATH = REPO_ROOT / "conf" / "sources.yml"


class Dominio(StrEnum):
    CERVEJA = "cerveja"
    APOSTAS = "apostas"
    MACRO = "macro"


class TipoFonte(StrEnum):
    PDF = "pdf"
    HTML = "html"
    API = "api"


class Adapter(StrEnum):
    API_SIDRA = "api_sidra"
    API_BCB = "api_bcb"
    HTTP_FILE = "http_file"
    HTTP_PAGE = "http_page"
    MANUAL = "manual"


class TierConfiabilidade(StrEnum):
    A = "A"  # dado oficial primário
    B = "B"  # pesquisa, think tank ou preprint sem conflito material
    C = "C"  # jornalismo, indústria, amostra de fornecedor ou conflito de interesse


class StatusAcervo(StrEnum):
    NO_LAKE = "no_lake"
    PENDENTE = "pendente"
    PLANEJADA = "planejada"
    FORA_DE_ESCOPO = "fora_de_escopo"


class Source(BaseModel):
    id: str
    titulo: str
    publicador: str
    dominio: Dominio
    tipo: TipoFonte
    adapter: Adapter
    url: HttpUrl | None = None
    licenca: str
    ano_referencia: int | None = None
    vintage_publicacao: int | None = None
    e_oficial: bool
    tier_confiabilidade: TierConfiabilidade
    status_acervo: StatusAcervo = StatusAcervo.NO_LAKE
    conflito_de_interesse: str | None = None
    landing_filename: str | None = None
    api_path: str | None = None
    notas: str | None = None

    @field_validator("id")
    @classmethod
    def id_slug(cls, value: str) -> str:
        if not value.replace("_", "").replace("-", "").isalnum():
            raise ValueError("id deve ser slug ASCII (letras, números, _ ou -)")
        return value

    @model_validator(mode="after")
    def pdfs_precisam_de_vintage(self) -> Source:
        if self.tipo == TipoFonte.PDF and self.vintage_publicacao is None:
            raise ValueError(f"{self.id}: PDF precisa de vintage_publicacao")
        if (
            self.tipo == TipoFonte.PDF
            and self.status_acervo == StatusAcervo.NO_LAKE
            and not self.landing_filename
        ):
            raise ValueError(f"{self.id}: PDF no lake precisa de landing_filename")
        return self


class SourceRegistry(BaseModel):
    sources: list[Source] = Field(min_length=1)

    @model_validator(mode="after")
    def ids_unicos(self) -> SourceRegistry:
        ids = [source.id for source in self.sources]
        duplicados = sorted({item for item in ids if ids.count(item) > 1})
        if duplicados:
            raise ValueError(f"ids duplicados em sources.yml: {duplicados}")
        return self

    def get(self, source_id: str) -> Source:
        for source in self.sources:
            if source.id == source_id:
                return source
        raise KeyError(source_id)

    def by_status(self, status: StatusAcervo) -> list[Source]:
        return [source for source in self.sources if source.status_acervo == status]


def load_registry(path: Path | None = None) -> SourceRegistry:
    target = path or SOURCES_PATH
    raw = yaml.safe_load(target.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "sources" in raw:
        payload = raw
    elif isinstance(raw, list):
        payload = {"sources": raw}
    else:
        raise ValueError("sources.yml deve ser uma lista ou um mapa com a chave sources")
    return SourceRegistry.model_validate(payload)
