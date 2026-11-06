from ps22psx.cli import build_parser


def test_parser_has_todo_commands():
    parser = build_parser()
    # ensure TODOs are exposed as CLI
    help_txt = parser.format_help()
    assert "config" in help_txt
    assert "lua" in help_txt
    assert "create" in help_txt


def test_config_list(capsys):
    from ps22psx.cli import main
    import pytest

    with pytest.raises(SystemExit) as ei:
        main(["config", "--list"])
    assert ei.value.code == 0
    out = capsys.readouterr().out
    assert "--gs-upscale" in out
