"""Build a PS4 Classics fPKG from a PS2 ISO/BIN (macOS / Windows / Linux)."""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .assets import prepare_background, prepare_icon, prepare_save_data_icon
from .bin_patch import convert_bin_to_disc_iso
from .emu_commands import default_config, merge_flags
from .gp4_fix import fix_gp4
from .iso_info import GameInfo, inspect_image
from .sfo_patch import patch_param_sfo
from .tools import check_toolchain, load_toolchain, run_tool


LogFn = Callable[[str], None]


@dataclass
class BuildRequest:
    images: list[Path]
    emulator_pkg: Path
    icon: Path
    background: Path
    output_dir: Path
    game_name: str | None = None
    title_id: str | None = None
    config_text: str | None = None
    config_file: Path | None = None
    lua_file: Path | None = None
    extra_flags: list[str] = field(default_factory=list)
    tools_dir: Path | None = None


@dataclass
class BuildResult:
    pkg_path: Path
    title_id: str
    game_name: str


def _log(log: LogFn | None, msg: str) -> None:
    if log:
        log(msg)


def _copy_discs(images: list[Path], image_dir: Path, log: LogFn | None) -> int:
    image_dir.mkdir(parents=True, exist_ok=True)
    for idx, src in enumerate(images, start=1):
        dest = image_dir / f"disc0{idx}.iso"
        suffix = src.suffix.lower()
        if suffix == ".bin":
            _log(log, f"Converting BIN → disc0{idx}.iso + LIMG…")
            convert_bin_to_disc_iso(src, dest)
        elif suffix == ".iso":
            _log(log, f"Copying ISO → disc0{idx}.iso…")
            shutil.copy2(src, dest)
        else:
            raise ValueError(f"Unsupported image type: {src}")
    return len(images)


def _extract_emulator(tc, emu_pkg: Path, temp: Path, log: LogFn | None) -> Path:
    _log(log, f"Extracting emulator PKG: {emu_pkg.name}")
    extract_dir = temp / "extract"
    extract_dir.mkdir(parents=True, exist_ok=True)
    run_tool(
        tc,
        "orbis-pub-cmd.exe",
        [
            "img_extract",
            "--passcode",
            "00000000000000000000000000000000",
            str(emu_pkg),
            str(extract_dir),
        ],
    )
    sc0 = extract_dir / "Sc0"
    sce_sys = extract_dir / "sce_sys"
    if sc0.is_dir():
        sc0.rename(sce_sys)
    image0 = extract_dir / "image0"
    if not image0.is_dir():
        raise RuntimeError("Emulator extract missing image0/")
    param = sce_sys / "param.sfo"
    target_sys = image0 / "sce_sys"
    target_sys.mkdir(parents=True, exist_ok=True)
    if param.is_file():
        shutil.move(str(param), str(target_sys / "param.sfo"))
    if sce_sys.is_dir():
        shutil.rmtree(sce_sys, ignore_errors=True)
    return image0


def _write_config(
    image0: Path,
    info: GameInfo,
    game_name: str,
    disc_count: int,
    req: BuildRequest,
    log: LogFn | None,
) -> None:
    cfg_path = image0 / "config-emu-ps4.txt"
    if req.config_file and req.config_file.is_file():
        text = req.config_file.read_text(encoding="utf-8", errors="ignore")
        _log(log, f"Using config file: {req.config_file}")
    elif req.config_text:
        text = req.config_text
        _log(log, "Using provided config text")
    elif cfg_path.is_file():
        text = cfg_path.read_text(encoding="utf-8", errors="ignore")
        text = text.replace("#Markus95", f"#{game_name}")
        _log(log, "Using emulator default config")
    else:
        text = default_config(game_name, info.title_id, disc_count)
        _log(log, "Generating default config")

    flags = [f"--max-disc-num={disc_count}", f"--ps2-title-id={info.title_id}", *req.extra_flags]
    text = merge_flags(text, flags)
    cfg_path.write_text(text, encoding="utf-8")


def _install_lua(image0: Path, title_id: str, lua_file: Path | None, log: LogFn | None) -> None:
    if not lua_file:
        return
    patches = image0 / "patches"
    patches.mkdir(parents=True, exist_ok=True)
    dest = patches / f"{title_id}_config.lua"
    shutil.copy2(lua_file, dest)
    _log(log, f"Installed LUA: {dest.name}")


def build_pkg(req: BuildRequest, log: LogFn | None = None) -> BuildResult:
    if not req.images:
        raise ValueError("At least one ISO/BIN is required")
    if len(req.images) > 5:
        raise ValueError("Maximum 5 discs supported")

    tc = load_toolchain(req.tools_dir)
    problems = check_toolchain(tc)
    if problems:
        raise RuntimeError("Toolchain not ready:\n- " + "\n- ".join(problems))

    info = inspect_image(req.images[0])
    title_id = req.title_id or info.title_id
    game_name = (req.game_name or info.name_hint).strip() or title_id
    info.title_id = title_id

    req.output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="ps22psx_") as tmp:
        temp = Path(tmp)
        image0 = _extract_emulator(tc, req.emulator_pkg, temp, log)
        disc_count = _copy_discs(req.images, image0 / "image", log)
        _write_config(image0, info, game_name, disc_count, req, log)
        _install_lua(image0, title_id, req.lua_file, log)

        sce_sys = image0 / "sce_sys"
        prepare_icon(req.icon, sce_sys / "icon0.png")
        prepare_save_data_icon(sce_sys / "icon0.png", sce_sys / "save_data.png")
        prepare_background(req.background, sce_sys / "pic1.png")
        _log(log, "Prepared icon0/pic1/save_data images")

        _log(log, "Patching param.sfo…")
        patch_param_sfo(sce_sys / "param.sfo", title_id, game_name)

        _log(log, "Generating GP4…")
        run_tool(tc, "gengp4.exe", [str(image0)])
        gp4 = image0.with_suffix(".gp4")
        if not gp4.is_file():
            alt = image0.parent / "image0.gp4"
            if not alt.is_file():
                raise RuntimeError("gengp4 did not produce a .gp4 file")
            gp4 = alt
        fix_gp4(gp4, image0, title_id, game_name)
        _log(log, f"GP4 ready ({gp4.name})")

        safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in game_name).strip()
        pkg_path = req.output_dir / f"{safe_name}_{title_id}.pkg"
        _log(log, f"Compiling PKG → {pkg_path.name}")
        run_tool(tc, "orbis-pub-cmd.exe", ["img_create", str(gp4), str(pkg_path)])

        return BuildResult(pkg_path=pkg_path, title_id=title_id, game_name=game_name)
