import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

from scripts.check_language_structure import (  # noqa: E402
    _unexpected_python_modules,
    main,
)


def test_check_language_structure_script() -> None:
    assert main() == 0


def test_unexpected_python_modules_detects_extra(tmp_path: Path) -> None:
    language_dir = tmp_path / "python"
    language_dir.mkdir()
    for name in [
        "__init__.py",
        "analyzer.py",
        "detectors.py",
        "mapping.py",
        "rules.py",
    ]:
        (language_dir / name).write_text("", encoding="utf-8")
    (language_dir / "extra.py").write_text("", encoding="utf-8")

    assert _unexpected_python_modules(language_dir) == ["extra.py"]


def test_unexpected_python_modules_ignores_non_python(tmp_path: Path) -> None:
    language_dir = tmp_path / "python"
    language_dir.mkdir()
    for name in [
        "__init__.py",
        "analyzer.py",
        "detectors.py",
        "mapping.py",
        "rules.py",
    ]:
        (language_dir / name).write_text("", encoding="utf-8")
    (language_dir / "README.md").write_text("", encoding="utf-8")
    (language_dir / "notes").mkdir()

    assert _unexpected_python_modules(language_dir) == []
