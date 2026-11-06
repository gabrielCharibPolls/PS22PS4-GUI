"""Command-line interface for PS22PSX."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .emu_commands import COMMANDS, by_category, default_config, format_command
from .iso_info import inspect_image
from .lua_maker import write_lua
from .pkg_builder import BuildRequest, build_pkg
from .tools import check_toolchain, default_tools_dir, load_toolchain


def _cmd_info(args: argparse.Namespace) -> int:
    info = inspect_image(args.image)
    print(f"Path     : {info.path}")
    print(f"Title ID : {info.title_id}")
    print(f"Boot     : {info.raw_boot}")
    print(f"Version  : {info.version}")
    print(f"Region   : {info.region}")
    print(f"Name hint: {info.name_hint}")
    return 0


def _cmd_doctor(args: argparse.Namespace) -> int:
    tc = load_toolchain(Path(args.tools) if args.tools else None)
    print(f"Tools dir : {tc.root}")
    print(f"Wine      : {tc.wine or '(native Windows / missing)'}")
    print(f"Magick    : {tc.magick or '(missing)'}")
    problems = check_toolchain(tc)
    if not problems:
        print("Status    : OK")
        return 0
    print("Status    : NOT READY")
    for p in problems:
        print(f" - {p}")
    print("\nSee docs/SETUP_MACOS.md and docs/TESTING_CONSOLES.md")
    return 1


def _cmd_config(args: argparse.Namespace) -> int:
    if args.list:
        cats = by_category()
        for cat, cmds in sorted(cats.items()):
            print(f"[{cat}]")
            for c in cmds:
                vals = f" {{{', '.join(c.values)}}}" if c.values else ""
                ex = f" e.g. {c.example}" if c.example else ""
                print(f"  {c.flag}{vals} — {c.description}{ex}")
            print()
        return 0

    if not args.title_id:
        print("--title-id is required to generate a config", file=sys.stderr)
        return 2

    text = default_config(args.name or args.title_id, args.title_id, args.discs)
    if args.add:
        for item in args.add:
            if "=" in item:
                flag, value = item.split("=", 1)
            else:
                flag, value = item, None
            # validate known flags softly
            known = {c.flag for c in COMMANDS}
            if flag not in known:
                print(f"warning: unknown flag {flag}", file=sys.stderr)
            text = text.rstrip() + "\n" + format_command(flag, value) + "\n"

    out = Path(args.output) if args.output else Path(f"{args.title_id}.conf")
    out.write_text(text, encoding="utf-8")
    print(f"Wrote {out}")
    return 0


def _cmd_lua(args: argparse.Namespace) -> int:
    out = Path(args.output) if args.output else Path(f"{args.title_id}_config.lua")
    write_lua(out, args.title_id, args.name or args.title_id, include_upscale_hint=args.upscale_hint)
    print(f"Wrote {out}")
    return 0


def _cmd_create(args: argparse.Namespace) -> int:
    images = [Path(p) for p in args.images]
    req = BuildRequest(
        images=images,
        emulator_pkg=Path(args.emulator),
        icon=Path(args.icon),
        background=Path(args.background),
        output_dir=Path(args.output),
        game_name=args.name,
        title_id=args.title_id,
        config_file=Path(args.config) if args.config else None,
        lua_file=Path(args.lua) if args.lua else None,
        extra_flags=args.flag or [],
        tools_dir=Path(args.tools) if args.tools else None,
        target=args.target,
    )

    def log(msg: str) -> None:
        print(msg, flush=True)

    result = build_pkg(req, log=log)
    print(f"\nDone → {result.pkg_path}")
    print(f"Title : {result.game_name} ({result.title_id})")
    print(f"Target: {result.target}")
    if result.target == "ps5":
        print("Install on exploited PS5 with PS4 FPKG Enabler / kstuff enabled.")
    else:
        print("Install on jailbroken PS4 (or PS5 HEN + FPKG Enabler).")
    return 0


def _cmd_gui(_args: argparse.Namespace) -> int:
    from .gui import run_gui

    run_gui()
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ps22psx",
        description="PS2 ISO/BIN → PS4/PS5 Classics fPKG (macOS / Windows / Linux)",
    )
    p.add_argument("--version", action="version", version=f"ps22psx {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    info = sub.add_parser("info", help="Read SYSTEM.CNF / title id from an ISO or BIN")
    info.add_argument("image", help="Path to .iso or .bin")
    info.set_defaults(func=_cmd_info)

    doctor = sub.add_parser("doctor", help="Check Wine + packaging tools")
    doctor.add_argument("--tools", help=f"Tools directory (default: {default_tools_dir()})")
    doctor.set_defaults(func=_cmd_doctor)

    cfg = sub.add_parser("config", help="Proper config maker")
    cfg.add_argument("--list", action="store_true", help="List emulator flags")
    cfg.add_argument("--title-id", help="Game title id e.g. SLUS-20091")
    cfg.add_argument("--name", help="Game display name")
    cfg.add_argument("--discs", type=int, default=1)
    cfg.add_argument("--add", action="append", help="Add flag e.g. --gs-upscale=smooth")
    cfg.add_argument("--output", "-o", help="Output .conf path")
    cfg.set_defaults(func=_cmd_config)

    lua = sub.add_parser("lua", help="Proper LUA maker")
    lua.add_argument("--title-id", required=True)
    lua.add_argument("--name", default="")
    lua.add_argument("--upscale-hint", action="store_true")
    lua.add_argument("--output", "-o")
    lua.set_defaults(func=_cmd_lua)

    create = sub.add_parser("create", help="Build fPKG")
    create.add_argument("images", nargs="+", help="One or more .iso/.bin (max 5)")
    create.add_argument("--emulator", required=True, help="Base PS2 Classics emulator .pkg")
    create.add_argument("--icon", required=True, help="Cover / icon image")
    create.add_argument("--background", required=True, help="Background image")
    create.add_argument("--output", "-o", default="out", help="Output directory")
    create.add_argument("--name", help="Game name override")
    create.add_argument("--title-id", help="Title id override")
    create.add_argument("--config", help="Custom config-emu file")
    create.add_argument("--lua", help="Custom LUA patch")
    create.add_argument("--flag", action="append", help="Extra emu flag")
    create.add_argument("--tools", help="bin/tools directory")
    create.add_argument(
        "--target",
        choices=("ps4", "ps5"),
        default="ps4",
        help="ps4 jailbreak, or ps5 HEN (PS4 FPKG Enabler)",
    )
    create.set_defaults(func=_cmd_create)

    gui = sub.add_parser("gui", help="Launch simple Tk GUI")
    gui.set_defaults(func=_cmd_gui)

    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        code = args.func(args)
    except Exception as exc:  # noqa: BLE001 — CLI surface
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    raise SystemExit(code)


if __name__ == "__main__":
    main()
