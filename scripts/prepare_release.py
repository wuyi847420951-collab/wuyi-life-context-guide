#!/usr/bin/env python3
"""Build a clean, validation-ready copy outside an Obsidian vault."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


IGNORED_NAMES = {".DS_Store", ".git", "__pycache__"}


def strip_skill_runtime_fields(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md 缺少 YAML frontmatter")

    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("SKILL.md frontmatter 未闭合")

    frontmatter = text[4:end].splitlines()
    cleaned = [
        line
        for line in frontmatter
        if not line.startswith("created:") and not line.startswith("updated:")
    ]
    path.write_text(
        "---\n" + "\n".join(cleaned) + "\n---\n" + text[end + 5 :],
        encoding="utf-8",
    )


def strip_document_frontmatter(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return

    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError(f"{path.name} frontmatter 未闭合")
    path.write_text(text[end + 5 :].lstrip("\n"), encoding="utf-8")


def build_release(source: Path, target: Path) -> None:
    if target.exists():
        raise FileExistsError(f"目标已存在，未覆盖：{target}")

    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns(*IGNORED_NAMES, "*.pyc"),
    )
    strip_skill_runtime_fields(target / "SKILL.md")
    strip_document_frontmatter(target / "README.md")
    strip_document_frontmatter(target / "CHANGELOG.md")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="生成不含 Obsidian 自动字段的公开 Skill 副本。"
    )
    parser.add_argument("target", type=Path, help="必须尚不存在的输出目录")
    args = parser.parse_args()

    source = Path(__file__).resolve().parent.parent
    target = args.target.expanduser().resolve()
    build_release(source, target)
    print(target)


if __name__ == "__main__":
    main()

