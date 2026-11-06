from ps22psx.emu_commands import default_config, format_command, merge_flags


def test_default_config_contains_title():
    text = default_config("Ridge Racer V", "SLUS-20001", 1)
    assert "--ps2-title-id=SLUS-20001" in text
    assert "--max-disc-num=1" in text


def test_merge_flags_replaces():
    base = "--ps2-title-id=OLD\n--host-vsync=0\n"
    out = merge_flags(base, ["--ps2-title-id=SLUS-20001", "--gs-upscale=smooth"])
    assert "--ps2-title-id=SLUS-20001" in out
    assert "OLD" not in out
    assert "--gs-upscale=smooth" in out
    assert "--host-vsync=0" in out


def test_format_command():
    assert format_command("--host-vsync", "1") == "--host-vsync=1"
    assert format_command("--record-audio") == "--record-audio"
