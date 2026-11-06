"""Normalize gengp4 output so orbis-pub-cmd accepts it under Wine on macOS."""

from __future__ import annotations

import re
from pathlib import Path

from .sfo_patch import make_content_id
from .tools import to_wine_path


def fix_gp4(gp4_path: Path, image0: Path, title_id: str, game_name: str) -> Path:
    text = gp4_path.read_text(encoding="utf-8", errors="ignore")
    text = text.replace("\x00", "")
    text = text.replace('<?xml version="1.1"', '<?xml version="1.0"')
    text = text.replace('<scenarios default_id="1">', '<scenarios default_id="0">')

    win_root = to_wine_path(image0.resolve())
    lines: list[str] = []
    for line in text.splitlines():
        if 'orig_path="' not in line:
            lines.append(line)
            continue
        pre, rest = line.split('orig_path="', 1)
        orig, post = rest.split('"', 1)
        orig_norm = orig.replace("/", "\\")
        marker = "image0\\"
        if marker in orig_norm:
            orig_norm = orig_norm[orig_norm.index(marker) + len(marker) :]
        abs_win = f"{win_root}\\{orig_norm}"
        lines.append(f'{pre}orig_path="{abs_win}"{post}')

    text = "\n".join(lines) + "\n"
    content_id = make_content_id(title_id, game_name)
    text = re.sub(r'content_id="[^"]*"', f'content_id="{content_id}"', text)
    gp4_path.write_text(text, encoding="utf-8")
    return gp4_path
