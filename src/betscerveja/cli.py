"""CLI: registro de fontes, ingestão e extração."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from betscerveja.extract.runner import extract_source
from betscerveja.ingest.runner import ingest_source
from betscerveja.registry import StatusAcervo, load_registry

app = typer.Typer(no_args_is_help=True, help="Pipeline bets-cerveja.")
sources_app = typer.Typer(no_args_is_help=True, help="Registro declarativo de fontes.")
app.add_typer(sources_app, name="sources")
console = Console()


@sources_app.command("list")
def sources_list(
    dominio: Annotated[str | None, typer.Option(help="Filtrar por dominio")] = None,
) -> None:
    registry = load_registry()
    table = Table(title="Fontes")
    table.add_column("id")
    table.add_column("dominio")
    table.add_column("tipo")
    table.add_column("tier")
    table.add_column("status")
    table.add_column("publicador")
    for source in registry.sources:
        if dominio and source.dominio != dominio:
            continue
        table.add_row(
            source.id,
            source.dominio,
            source.tipo,
            source.tier_confiabilidade,
            source.status_acervo,
            source.publicador,
        )
    console.print(table)


@sources_app.command("show")
def sources_show(source_id: str) -> None:
    registry = load_registry()
    try:
        source = registry.get(source_id)
    except KeyError as exc:
        raise typer.BadParameter(f"fonte não encontrada: {source_id}") from exc
    console.print(source.model_dump(mode="json"))


@sources_app.command("validate")
def sources_validate() -> None:
    registry = load_registry()
    no_lake = len(registry.by_status(StatusAcervo.NO_LAKE))
    pendente = len(registry.by_status(StatusAcervo.PENDENTE))
    planejada = len(registry.by_status(StatusAcervo.PLANEJADA))
    fora = len(registry.by_status(StatusAcervo.FORA_DE_ESCOPO))
    console.print(
        f"{len(registry.sources)} fontes válidas "
        f"({no_lake} no lake, {pendente} pendentes, {planejada} planejadas, "
        f"{fora} fora de escopo)."
    )


@app.command("ingest")
def ingest(
    source: Annotated[str, typer.Option(help="id em conf/sources.yml")],
) -> None:
    registry = load_registry()
    try:
        item = registry.get(source)
    except KeyError as exc:
        raise typer.BadParameter(f"fonte não encontrada: {source}") from exc
    record = ingest_source(item)
    console.print(record)


@app.command("extract")
def extract(
    source: Annotated[str, typer.Option(help="id em conf/sources.yml")],
) -> None:
    registry = load_registry()
    try:
        item = registry.get(source)
    except KeyError as exc:
        raise typer.BadParameter(f"fonte não encontrada: {source}") from exc
    dest = extract_source(item)
    console.print(f"escreveu {dest}")
