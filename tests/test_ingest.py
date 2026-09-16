from pathlib import Path

from betscerveja.ingest.manifest import known_hashes, write_payload
from betscerveja.registry import load_registry


def test_write_payload_idempotente(tmp_path: Path, monkeypatch) -> None:
    from betscerveja.ingest import manifest as manifest_mod

    monkeypatch.setattr(manifest_mod, "LANDING_ROOT", tmp_path)
    source = load_registry().get("sidra_8885_pim_bebidas")
    body = b'{"ok": true}'
    _, skipped_first = write_payload(source, body, ".json")
    assert skipped_first is False
    from betscerveja.ingest.manifest import append_manifest, sha256_bytes

    append_manifest(source, {"sha256": sha256_bytes(body)})
    _, skipped_second = write_payload(source, body, ".json")
    assert skipped_second is True
    assert sha256_bytes(body) in known_hashes(source)
