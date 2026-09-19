import json

from bioir.fusion_intervention import verdict_artifact, write_verdict_artifact


def test_frozen_verdict_artifact_preserves_negative_result_and_seed_identities(tmp_path):
    artifact = verdict_artifact()
    verdict = artifact["verdict"]

    assert artifact["schema"] == "bioir/fusion-verdict/v1"
    assert artifact["claim_state"] == "REJECTED"
    assert artifact["experiment"]["seed_start"] == 0
    assert artifact["experiment"]["seed_stop_exclusive"] == 1000
    assert verdict["baseline_converged"] == 963
    assert verdict["fusion_converged"] == 876
    assert verdict["baseline_unsupported"] == 0
    assert verdict["fusion_unsupported"] == 0
    assert verdict["regressed_seeds"]
    assert set(verdict["regressed_seeds"]).isdisjoint(verdict["recovered_seeds"])

    path = write_verdict_artifact(tmp_path / "verdict.json")
    persisted = json.loads(path.read_text(encoding="utf-8"))
    assert persisted == artifact


def test_verdict_artifact_is_byte_deterministic(tmp_path):
    first = write_verdict_artifact(tmp_path / "first.json").read_bytes()
    second = write_verdict_artifact(tmp_path / "second.json").read_bytes()
    assert first == second
