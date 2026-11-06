"""Patch PS4 param.sfo title fields for PS2 Classics."""

from __future__ import annotations

import re
from pathlib import Path


def _write_c_string(buf: bytearray, offset: int, text: str, max_len: int) -> None:
    data = text.encode("ascii", errors="ignore")[: max_len - 1]
    for i in range(offset, min(offset + max_len, len(buf))):
        buf[i] = 0
    buf[offset : offset + len(data)] = data


def make_content_id(title_id: str, game_name: str) -> str:
    tid9 = title_id.replace("-", "")[:9].ljust(9, "0")
    suffix = re.sub(r"[^A-Z0-9]", "", game_name.upper())[:16].ljust(16, "0")
    return f"UP9000-{tid9}_00-{suffix}"


def patch_param_sfo(path: Path, title_id: str, game_name: str) -> None:
    raw = bytearray(path.read_bytes())
    tid = title_id.replace("-", "")[:9]
    name = game_name[:31]
    cid = make_content_id(title_id, game_name)

    _write_c_string(raw, 0x31F, tid, 10)
    _write_c_string(raw, 0x670, tid, 10)
    _write_c_string(raw, 0x5F0, name, 32)

    # Replace existing CONTENT_ID ASCII blob if found
    for marker in (b"UP9000-", b"EP9000-", b"JP9000-"):
        idx = raw.find(marker)
        if idx != -1:
            blob = cid.encode("ascii")
            if len(blob) == 36:
                raw[idx : idx + 36] = blob
            break

    path.write_bytes(raw)
