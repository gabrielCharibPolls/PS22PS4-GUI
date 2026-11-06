from pathlib import Path

from ps22psx.bin_patch import convert_bin_to_disc_iso, crc32_file, limg_trailer


def test_limg_trailer_length():
    trailer = limg_trailer(0xDEADBEEF)
    assert len(trailer) == 16
    assert trailer[:4] == b"LIMG"
    assert trailer[8:12] == bytes.fromhex("DEADBEEF")


def test_convert_bin(tmp_path: Path):
    src = tmp_path / "game.bin"
    src.write_bytes(b"PS2DATA" * 100)
    dest = tmp_path / "disc01.iso"
    convert_bin_to_disc_iso(src, dest)
    assert dest.stat().st_size == src.stat().st_size + 16
    crc = crc32_file(Path(str(dest)) )  # full file includes trailer — not used for assert
    assert dest.read_bytes()[-16:-12] == b"LIMG"
    # CRC in trailer is of the pre-trailer copy; recompute from src only
    from ps22psx.bin_patch import crc32_file as c

    expected = c(src)
    # After copy, CRC of dest without last 16 bytes equals src CRC
    body = dest.read_bytes()[:-16]
    import zlib

    assert (zlib.crc32(body) & 0xFFFFFFFF) == expected
