"""BIN → ISO LIMG trailer patch (CRC32), ported from the legacy VB pipeline."""

from __future__ import annotations

import shutil
import zlib
from pathlib import Path


def crc32_file(path: Path, chunk_size: int = 1024 * 1024) -> int:
    crc = 0
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(chunk_size)
            if not chunk:
                break
            crc = zlib.crc32(chunk, crc)
    return crc & 0xFFFFFFFF


def limg_trailer(crc: int) -> bytes:
    # Legacy: "4C494D4700000002FFFFFFFF00000930" with FFFFFFFF replaced by CRC hex
    prefix = bytes.fromhex("4C494D4700000002")
    suffix = bytes.fromhex("00000930")
    return prefix + crc.to_bytes(4, "big") + suffix


def convert_bin_to_disc_iso(bin_path: Path, dest_iso: Path) -> Path:
    """Copy BIN as disc01.iso and append LIMG trailer used by PS2 Classics."""
    dest_iso.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(bin_path, dest_iso)
    crc = crc32_file(dest_iso)
    with dest_iso.open("ab") as fh:
        fh.write(limg_trailer(crc))
    return dest_iso
