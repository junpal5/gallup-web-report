from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List


DEFAULT_COLORS = [
    "#0e4d8c",
    "#2d82d4",
    "#00a86b",
    "#e85d04",
    "#7c3aed",
    "#dc2626",
    "#0891b2",
    "#d97706",
    "#be185d",
    "#374151",
]

META_PREFIXES = ("report:", "portal:")


class ReportHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: Dict[str, str] = {}
        self._in_title = False
        self._title_parts: List[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        attr_map = dict(attrs)
        if tag.lower() == "meta":
            raw_name = (attr_map.get("name") or attr_map.get("property") or "").strip().lower()
            content = (attr_map.get("content") or "").strip()
            if raw_name and content:
                for prefix in META_PREFIXES:
                    if raw_name.startswith(prefix):
                        self.meta[raw_name[len(prefix) :]] = content
                        break
        elif tag.lower() == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_parts.append(data)

    @property
    def title(self) -> str:
        return "".join(self._title_parts).strip()


def slug_to_title(stem: str) -> str:
    cleaned = re.sub(r"[_\-]+", " ", stem).strip()
    return cleaned or stem


def normalize_year(raw: str) -> int | None:
    if not raw:
        return None
    match = re.search(r"\d{4}", raw)
    return int(match.group(0)) if match else None


def parse_report(html_path: Path, reports_dir: Path, index: int) -> dict:
    parser = ReportHtmlParser()
    parser.feed(html_path.read_text(encoding="utf-8"))
    meta = parser.meta

    rel_path = html_path.relative_to(reports_dir.parent).as_posix()
    stem = html_path.stem
    year = normalize_year(meta.get("year", ""))

    return {
        "id": index,
        "slug": meta.get("slug", stem),
        "title": meta.get("title") or parser.title or slug_to_title(stem),
        "client": meta.get("client", "Uncategorized"),
        "year": year if year is not None else "",
        "type": meta.get("type", "Other"),
        "sample": meta.get("sample", ""),
        "desc": meta.get("desc", ""),
        "color": meta.get("color", DEFAULT_COLORS[(index - 1) % len(DEFAULT_COLORS)]),
        "path": meta.get("path", rel_path),
    }


def build_manifest(base_dir: Path) -> List[dict]:
    reports_dir = base_dir / "reports"
    if not reports_dir.exists():
        return []

    html_files = sorted(
        path for path in reports_dir.rglob("*.html") if path.is_file() and path.name.lower() != "index.html"
    )
    return [parse_report(path, reports_dir, index + 1) for index, path in enumerate(html_files)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build reports-manifest.json from reports HTML files.")
    parser.add_argument("--base-dir", default=".", help="Repository root containing reports/ and reports-manifest.json")
    parser.add_argument("--output", default="reports-manifest.json", help="Manifest output path relative to base-dir")
    args = parser.parse_args()

    base_dir = Path(args.base_dir).resolve()
    manifest = build_manifest(base_dir)

    output_path = (base_dir / args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {len(manifest)} report entries to {output_path}")


if __name__ == "__main__":
    main()
