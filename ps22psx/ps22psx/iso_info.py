"""Extract PS2 game metadata from ISO/BIN images."""

from __future__ import annotations

import io
import re
from dataclasses import dataclass
from pathlib import Path

import pycdlib


SYSTEM_CNF_RE = re.compile(
    r"BOOT2\s*=\s*cdrom0:\\([^;]+);1.*?VER\s*=\s*([0-9.]+)",
    re.IGNORECASE | re.DOTALL,
)
TITLE_ID_RE = re.compile(r"([A-Z]{4})[_-]?(\d{3})\.?(\d{2})", re.IGNORECASE)


@dataclass
class GameInfo:
    path: Path
    title_id: str
    raw_boot: str
    version: str
    region: str
    name_hint: str

    @property
    def content_id_suffix(self) -> str:
        return self.title_id.replace("-", "")


REGION_MAP = {
    "SLUS": "NTSC-U",
    "SCUS": "NTSC-U",
    "SLES": "PAL",
    "SCES": "PAL",
    "SLPS": "NTSC-J",
    "SCPS": "NTSC-J",
    "SLPM": "NTSC-J",
    "SCED": "PAL",
    "SLED": "PAL",
}


def _normalize_title_id(boot_name: str) -> str:
    m = TITLE_ID_RE.search(boot_name.replace("\\", "/"))
    if not m:
        return "UNKNOWN-00000"
    return f"{m.group(1).upper()}-{m.group(2)}{m.group(3)}"


def _read_system_cnf(iso_path: Path) -> str:
    iso = pycdlib.PyCdlib()
    try:
        iso.open(str(iso_path))
        for candidate in ("/SYSTEM.CNF;1", "/system.cnf;1"):
            try:
                buf = io.BytesIO()
                iso.get_file_from_iso_fp(buf, iso_path=candidate)
                return buf.getvalue().decode("ascii", errors="ignore")
            except Exception:
                continue
        raise FileNotFoundError("SYSTEM.CNF not found in image")
    finally:
        try:
            iso.close()
        except Exception:
            pass


def inspect_image(path: str | Path) -> GameInfo:
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        raise FileNotFoundError(p)

    cnf = _read_system_cnf(p)
    m = SYSTEM_CNF_RE.search(cnf)
    if m:
        boot = m.group(1).strip()
        version = m.group(2).strip()
    else:
        boot = "UNKNOWN"
        version = "1.00"
        # Fallback: search raw CNF for a title id pattern
        tid_m = TITLE_ID_RE.search(cnf)
        if tid_m:
            boot = f"{tid_m.group(1)}_{tid_m.group(2)}.{tid_m.group(3)}"

    title_id = _normalize_title_id(boot)
    prefix = title_id.split("-")[0]
    region = REGION_MAP.get(prefix, "UNK")
    name_hint = p.stem.replace("_", " ").replace(".", " ").strip()

    return GameInfo(
        path=p,
        title_id=title_id,
        raw_boot=boot,
        version=version,
        region=region,
        name_hint=name_hint,
    )
