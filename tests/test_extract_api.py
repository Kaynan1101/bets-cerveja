from pathlib import Path

import pandas as pd

from betscerveja.extract.runner import extract_bcb, extract_sidra, extract_source
from betscerveja.registry import load_registry
from betscerveja.schemas.raw import RawApiSeries

FIXTURES = Path(__file__).parent / "fixtures"


def test_extract_sidra_achata_serie_e_nulos() -> None:
    source = load_registry().get("sidra_8885_pim_bebidas")
    frame = extract_sidra(source, FIXTURES / "sidra_nested.json")
    validated = RawApiSeries.validate(frame)
    assert set(validated["categoria_id"]) == {"129192", "129193"}
    alcool = validated[validated["categoria_id"] == "129192"]
    assert alcool.loc[alcool["periodo"] == "202201", "valor"].iloc[0] == 100.0
    assert pd.isna(alcool.loc[alcool["periodo"] == "202202", "valor"].iloc[0])
    assert pd.isna(alcool.loc[alcool["periodo"] == "202203", "valor"].iloc[0])
    assert validated["metodo"].eq("api_sidra").all()
    assert validated["variavel_id"].eq("12606").all()


def test_extract_bcb_classificacao_nula() -> None:
    source = load_registry().get("bcb_sgs_rendimento_real")
    frame = extract_bcb(source, FIXTURES / "bcb_sgs.json")
    validated = RawApiSeries.validate(frame)
    assert len(validated) == 2
    assert validated.loc[0, "periodo"] == "01/01/2023"
    assert validated.loc[0, "valor"] == 2890.12
    assert pd.isna(validated.loc[1, "valor"])
    assert validated["classificacao_id"].isna().all()
    assert validated["categoria_id"].isna().all()
    assert validated["metodo"].eq("api_bcb").all()


def test_extract_source_api_escreve_parquet(tmp_path: Path, monkeypatch) -> None:
    from betscerveja.extract import runner as runner_mod
    from betscerveja.ingest import manifest as manifest_mod

    landing = tmp_path / "landing"
    raw = tmp_path / "raw"
    dest_folder = landing / "sidra_8885_pim_bebidas" / "20260101T000000Z"
    dest_folder.mkdir(parents=True)
    dest_folder.joinpath("payload.json").write_bytes((FIXTURES / "sidra_nested.json").read_bytes())
    monkeypatch.setattr(manifest_mod, "LANDING_ROOT", landing)
    monkeypatch.setattr(runner_mod, "LANDING_ROOT", landing)
    monkeypatch.setattr(runner_mod, "RAW_ROOT", raw)

    source = load_registry().get("sidra_8885_pim_bebidas")
    dest = extract_source(source)
    assert dest == raw / "cerveja" / "sidra_8885_pim_bebidas" / "extract.parquet"
    assert dest.exists()
