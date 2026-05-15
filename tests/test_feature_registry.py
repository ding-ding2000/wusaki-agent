from pathlib import Path

from wusaki_agent.feature_registry import FeatureRegistry


def test_feature_registry_counts() -> None:
    root = Path(__file__).resolve().parents[1]
    registry = FeatureRegistry(root / "feature_list.json")

    counts = registry.counts()

    assert counts["done"] >= 1
    assert counts["planned"] >= 1

