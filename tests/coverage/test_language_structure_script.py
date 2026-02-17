import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

from scripts.check_language_structure import main  # noqa: E402


def test_check_language_structure_script() -> None:
    assert main() == 0
