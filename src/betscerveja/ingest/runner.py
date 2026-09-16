"""Adapters de ingestão por tipo de fonte."""

from __future__ import annotations

from datetime import UTC, datetime

from betscerveja.ingest.http import get_bytes
from betscerveja.ingest.manifest import append_manifest, sha256_bytes, write_payload
from betscerveja.registry import Adapter, Source, StatusAcervo

SIDRA_BASE = "https://servicodados.ibge.gov.br/api/v3"
BCB_BASE = "https://api.bcb.gov.br"


def _require_path(source: Source) -> str:
    if not source.api_path:
        raise ValueError(f"{source.id}: api_path obrigatório para {source.adapter}")
    if not source.api_path.startswith("/"):
        raise ValueError(f"{source.id}: api_path deve começar com /")
    return source.api_path


def resolve_url(source: Source) -> str:
    if source.adapter == Adapter.API_SIDRA:
        return SIDRA_BASE + _require_path(source)
    if source.adapter == Adapter.API_BCB:
        return BCB_BASE + _require_path(source)
    if source.adapter in {Adapter.HTTP_FILE, Adapter.HTTP_PAGE}:
        if source.url is None:
            raise ValueError(f"{source.id}: url obrigatória")
        return str(source.url)
    raise ValueError(f"{source.id}: adapter {source.adapter} não faz ingestão de rede")


def suffix_for(source: Source) -> str:
    if source.adapter == Adapter.HTTP_FILE:
        return ".pdf"
    if source.adapter == Adapter.HTTP_PAGE:
        return ".html"
    return ".json"


def ingest_source(source: Source) -> dict:
    if source.status_acervo == StatusAcervo.FORA_DE_ESCOPO:
        raise ValueError(f"{source.id} está fora de escopo")
    if source.adapter == Adapter.MANUAL:
        raise ValueError(f"{source.id} é coleta manual; nada a baixar")
    url = resolve_url(source)
    status, payload, final_url = get_bytes(url)
    digest = sha256_bytes(payload)
    dest, skipped = write_payload(source, payload, suffix_for(source))
    record = {
        "source_id": source.id,
        "url": final_url,
        "status_http": status,
        "sha256": digest,
        "bytes": len(payload),
        "retrieved_at": datetime.now(UTC).isoformat(),
        "path": str(dest),
        "skipped": skipped,
    }
    if not skipped:
        append_manifest(source, record)
    return record
