from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd
import pytest

from betscerveja.demo import SAMPLE_EXTRACTS, SAMPLE_ROOT, missing_sample_extracts, validate_sample
from betscerveja.figures import REQUIRED_ARTIFACTS
from betscerveja.registry import REPO_ROOT
from betscerveja.zenodo import ZENODO_MARTS, pack_zenodo


def _seed_warehouse(path: Path) -> None:
    panorama = pd.DataFrame(
        {
            "data_inicio": pd.date_range("2023-01-01", periods=2, freq="MS"),
            "producao_bebidas_alcoolicas_indice": [100.0, 101.0],
        }
    )
    anual = pd.DataFrame({"ano_referencia": [2023], "valor": [1.5e10]})
    previsao = pd.DataFrame(
        {
            "data_inicio": pd.date_range("2023-01-01", periods=2, freq="MS"),
            "realizado": [100.0, 101.0],
            "previsto": [100.2, 100.8],
            "ic_inf": [98.0, 98.5],
            "ic_sup": [102.5, 103.0],
        }
    )
    substituicao = pd.DataFrame({"categoria_id": ["bares_restaurantes_delivery"], "valor": [48.0]})
    estrutura = pd.DataFrame({"metrica_id": ["empregos_setor_apostas"], "valor": [1144.0]})
    divergencias = pd.DataFrame(
        {"metrica_id": ["empregos_setor_apostas"], "nota": ["duas definições"]}
    )
    proveniencia = pd.DataFrame(
        {"source_id": ["strategy_impacto_apostas_consumo_2024"], "valor": [48.0]}
    )
    metricas = pd.DataFrame({"execucao_id": ["a"], "aic": [1.0]})
    coeficientes = pd.DataFrame(
        {"execucao_id": ["a"], "regressor": ["ipca_cerveja"], "coeficiente": [0.1]}
    )

    con = duckdb.connect(str(path))
    con.execute("create schema marts_analytics")
    con.execute("create schema marts_core")
    con.execute("create schema marts_ml")
    for name, frame, schema in (
        ("agg_panorama_mensal", panorama, "marts_analytics"),
        ("fct_mercado_cerveja_anual", anual, "marts_core"),
        ("fct_cerveja_previsao", previsao, "marts_ml"),
        ("agg_de_onde_saiu_o_dinheiro", substituicao, "marts_analytics"),
        ("agg_estrutura_setorial", estrutura, "marts_analytics"),
        ("qa_divergencias", divergencias, "marts_analytics"),
        ("agg_indicadores_declarados", proveniencia, "marts_analytics"),
        ("ml_metricas", metricas, "marts_ml"),
        ("ml_coeficientes", coeficientes, "marts_ml"),
    ):
        con.register(f"_{name}", frame)
        con.execute(f'create table {schema}."{name}" as select * from "_{name}"')
    con.close()


def test_sample_tem_sete_extracts() -> None:
    assert missing_sample_extracts() == []
    for rel in SAMPLE_EXTRACTS:
        assert (SAMPLE_ROOT / rel).is_file()


def test_sample_series_tem_meses_antes_de_2023() -> None:
    sidra = pd.read_parquet(SAMPLE_ROOT / "cerveja/sidra_8885_pim_bebidas/extract.parquet")
    assert str(sidra["periodo"].min()) < "202301"
    bcb = pd.read_parquet(SAMPLE_ROOT / "macro/bcb_sgs_rendimento_real/extract.parquet")
    parsed = pd.to_datetime(bcb["periodo"], dayfirst=True)
    assert parsed.min() < pd.Timestamp("2023-01-01")


def test_sample_nao_tem_landing() -> None:
    forbidden = list(SAMPLE_ROOT.rglob("*.pdf")) + list(SAMPLE_ROOT.rglob("*.html"))
    assert forbidden == []


def test_validate_sample_aponta_readme(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="sample/README"):
        validate_sample(tmp_path)


def test_pack_zenodo_escreve_manifesto(tmp_path: Path) -> None:
    db = tmp_path / "betscerveja.duckdb"
    figures = tmp_path / "figures"
    out = tmp_path / "zenodo"
    _seed_warehouse(db)
    figures.mkdir()
    for name in REQUIRED_ARTIFACTS:
        (figures / name).write_text("x", encoding="utf-8")

    summary = pack_zenodo(duckdb_file=db, figures_dir=figures, output_dir=out)

    manifest = Path(summary["manifest"])
    assert manifest.is_file()
    text = manifest.read_text(encoding="utf-8")
    for mart in ZENODO_MARTS:
        assert f"{mart}.parquet" in text
        assert (out / "marts" / f"{mart}.parquet").is_file()
    for name in REQUIRED_ARTIFACTS:
        assert f"figures/{name}" in text.replace("\\", "/")
    assert (out / "LICENSE-DATA").is_file()
    assert (out / "README.md").is_file()
    assert (out / "CITATION.cff").is_file()
    assert (out / ".zenodo.json").is_file()
    readme = (out / "README.md").read_text(encoding="utf-8")
    assert "48%" in readme
    assert "survey" in readme.lower()
    assert "zenodo.XXXX" in readme
    assert list(out.rglob("*.duckdb")) == []
    assert list(out.rglob(".env")) == []


def test_makefile_demo_nao_entra_em_ci() -> None:
    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "demo" in makefile
    for line in makefile.splitlines():
        if line.startswith("ci:"):
            assert "demo" not in line
            assert "figures" not in line
        if line.startswith(".PHONY:"):
            assert "demo" in line
