"""Build PS4 Classics fPKG from PS2 ISO/BIN (also installable on exploited PS5 via FPKG Enabler)."""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .assets import prepare_background, prepare_icon, prepare_save_data_icon
from .bin_patch import convert_bin_to_disc_iso
from .emu_commands import default_config, merge_flags
from .iso_info import GameInfo, inspect_image
from .tools import Toolchain, check_toolchain, load_toolchain, run_tool


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
    # ps4: classic orbis PKG. On exploited PS5, install with PS4 FPKG Enabler / kstuff.
    target: str = "ps4"


@dataclass
class BuildResult:
    pkg_path: Path
    title_id: str
    game_name: str
    target: str
    work_dir: Path | None = None


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


def _extract_emulator(tc: Toolchain, emu_pkg: Path, temp: Path, log: LogFn | None) -> Path:
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


def _patch_sfo(tc: Toolchain, sfo: Path, title_id: str, game_name: str, log: LogFn | None) -> None:
    _log(log, "Patching param.sfo…")
    tid = title_id.replace("-", "")
    run_tool(tc, "replhex.exe", [str(sfo), "--address", "0x31F", "--text", tid])
    run_tool(tc, "replhex.exe", [str(sfo), "--address", "0x670", "--text", tid])
    run_tool(
        tc,
        "replhex.exe",
        [str(sfo), "--address", "0x5F0", "--hex", "00000000000000000000000000000000"],
    )
    run_tool(
        tc,
        "replhex.exe",
        [str(sfo), "--address", "0x600", "--hex", "00000000000000000000000000000000"],
    )
    run_tool(tc, "replhex.exe", [str(sfo), "--address", "0x5F0", "--text", game_name[:32]])


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


def build_pkg(req: BuildRequest, log: LogFn | None = None, *, keep_work: bool = False) -> BuildResult:
    if req.target not in {"ps4", "ps5"}:
        raise ValueError("target must be 'ps4' or 'ps5'")
    if not req.images:
        raise ValueError("At least one ISO/BIN is required")
    if len(req.images) > 5:
        raise ValueError("Maximum 5 discs supported")

    # PS5 target currently produces a PS4 Classics fPKG intended for
    # exploited PS5 + PS4 FPKG Enabler / kstuff (same content layout).
    if req.target == "ps5":
        _log(
            log,
            "Target PS5: building PS4 Classics fPKG for HEN + PS4 FPKG Enabler / kstuff.",
        )

    tc = load_toolchain(req.tools_dir)
    problems = check_toolchain(tc)
    if problems:
        raise RuntimeError("Toolchain not ready:\n- " + "\n- ".join(problems))

    info = inspect_image(req.images[0])
    title_id = req.title_id or info.title_id
    game_name = (req.game_name or info.name_hint).strip() or title_id
    info.title_id = title_id

    req.output_dir.mkdir(parents=True, exist_ok=True)
    temp_ctx = tempfile.TemporaryDirectory(prefix="ps22psx_")
    temp = Path(temp_ctx.name)

    try:
        image0 = _extract_emulator(tc, req.emulator_pkg, temp, log)
        disc_count = _copy_discs(req.images, image0 / "image", log)
        _write_config(image0, info, game_name, disc_count, req, log)
        _install_lua(image0, title_id, req.lua_file, log)

        sce_sys = image0 / "sce_sys"
        prepare_icon(req.icon, sce_sys / "icon0.png")
        prepare_save_data_icon(sce_sys / "icon0.png", sce_sys / "save_data.png")
        prepare_background(req.background, sce_sys / "pic1.png")
        _log(log, "Prepared icon0/pic1/save_data images")

        _patch_sfo(tc, sce_sys / "param.sfo", title_id, game_name, log)

        _log(log, "Generating GP4…")
        run_tool(tc, "gengp4.exe", [str(image0)])
        gp4 = image0.with_suffix(".gp4")
        if not gp4.is_file():
            # gengp4 may write next to image0 as image0.gp4 under parent
            alt = image0.parent / "image0.gp4"
            if alt.is_file():
                gp4 = alt
            else:
                raise RuntimeError("gengp4 did not produce a .gp4 file")
        gp4_text = gp4.read_text(encoding="utf-8", errors="ignore")
        gp4.write_text(
            gp4_text.replace('<scenarios default_id="1">', '<scenarios default_id="0">'),
            encoding="utf-8",
        )

        safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in game_name).strip()
        pkg_name = f"{safe_name}_{title_id}.pkg"
        if req.target == "ps5":
            pkg_name = f"{safe_name}_{title_id}_PS5HEN.pkg"
        pkg_path = req.output_dir / pkg_name

        _log(log, f"Compiling PKG → {pkg_path.name}")
        run_tool(tc, "orbis-pub-cmd.exe", ["img_create", str(gp4), str(pkg_path)])

        result = BuildResult(
            pkg_path=pkg_path,
            title_id=title_id,
            game_name=game_name,
            target=req.target,
            work_dir=None,
        )
        return result
    finally:
        temp_ctx.cleanup()
