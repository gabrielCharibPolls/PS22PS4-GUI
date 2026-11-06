from pathlib import Path

from ps22psx.gp4_fix import fix_gp4
from ps22psx.sfo_patch import make_content_id, patch_param_sfo


def test_content_id_format():
    cid = make_content_id("SLUS-20063", "Midnight Club Street Racing")
    assert len(cid) == 36
    assert cid.startswith("UP9000-SLUS20063_00-")
    assert "-" in cid and "_00-" in cid


def test_patch_sfo_roundtrip(tmp_path: Path):
    # minimal fake sfo buffer with room at known offsets + a content id marker
    buf = bytearray(0x800)
    buf[0x100:0x100 + 36] = b"UP9000-OLDTITLE0_00-OLDOLDOLDOLDOLD0"
    # place marker where finder looks from start — patch searches for UP9000-
    sfo = tmp_path / "param.sfo"
    sfo.write_bytes(buf)
    patch_param_sfo(sfo, "SLUS-20063", "Midnight Club")
    data = sfo.read_bytes()
    assert b"SLUS20063" in data


def test_fix_gp4(tmp_path: Path):
    image0 = tmp_path / "image0"
    image0.mkdir()
    gp4 = tmp_path / "image0.gp4"
    gp4.write_text(
        """<?xml version="1.1" encoding="utf-8"?>
<psproject>
  <package content_id="BAD\x00ID" passcode="0"/>
  <scenarios default_id="1"></scenarios>
  <file orig_path="out/x/image0\\sce_sys\\icon0.png"/>
</psproject>
""",
        encoding="utf-8",
    )
    fix_gp4(gp4, image0, "SLUS-20063", "Test Game")
    text = gp4.read_text(encoding="utf-8")
    assert 'version="1.0"' in text
    assert 'default_id="0"' in text
    assert "\x00" not in text
    assert "UP9000-SLUS20063_00-" in text
    assert "orig_path=\"Z:" in text or "orig_path='Z:" in text or 'orig_path="Z:' in text
