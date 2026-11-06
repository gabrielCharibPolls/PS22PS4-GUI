from pathlib import Path

from ps22psx.lua_maker import create_lua, write_lua


def test_create_lua_contains_hooks():
    text = create_lua("SLUS-20001", "Ridge Racer V", include_upscale_hint=True)
    assert "getEEObject" in text
    assert "AddVsyncHook" in text
    assert "gs-upscale" in text


def test_write_lua(tmp_path: Path):
    out = write_lua(tmp_path / "SLUS-20001_config.lua", "SLUS-20001")
    assert out.is_file()
    assert "SLUS-20001" in out.read_text(encoding="utf-8")
