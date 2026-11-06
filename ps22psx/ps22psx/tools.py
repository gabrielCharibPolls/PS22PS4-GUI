"""Locate packaging tools and run them (native ImageMagick + Wine for Orbis EXEs on macOS)."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


REQUIRED_EXES = ("orbis-pub-cmd.exe", "gengp4.exe")


@dataclass
class Toolchain:
    root: Path
    wine: str | None
    magick: str | None

    def resolve(self, name: str) -> Path:
        p = self.root / name
        if not p.is_file():
            raise FileNotFoundError(f"Missing tool: {p}")
        return p


def find_wine() -> str | None:
    for candidate in ("wine64", "wine"):
        path = shutil.which(candidate)
        if path:
            return path
    # Common local installs (Gcenx Wine Stable.app wrapper, Whisky shellenv)
    home = Path.home()
    extras = [
        home / "bin" / "wine64",
        home / "bin" / "wine",
        home / "wine-gcenx" / "Wine Stable.app" / "Contents" / "Resources" / "wine" / "bin" / "wine",
    ]
    for p in extras:
        if p.is_file():
            return str(p)
    return None


def find_magick() -> str | None:
    for candidate in ("magick", "convert"):
        path = shutil.which(candidate)
        if path:
            return path
    return None


def default_tools_dir() -> Path:
    env = os.environ.get("PS22PSX_TOOLS")
    if env:
        return Path(env).expanduser().resolve()
    cwd = Path.cwd()
    candidates = [
        cwd / "bin" / "tools",
        cwd / "tools",
        Path(__file__).resolve().parents[1] / "bin" / "tools",
        Path(__file__).resolve().parents[2] / "bin" / "tools",
    ]
    for c in candidates:
        if c.is_dir():
            return c
    return candidates[0]


def load_toolchain(tools_dir: Path | None = None) -> Toolchain:
    root = Path(tools_dir).expanduser().resolve() if tools_dir else default_tools_dir()
    wine = None if platform.system() == "Windows" else find_wine()
    return Toolchain(root=root, wine=wine, magick=find_magick())


def to_wine_path(path: Path | str) -> str:
    p = Path(path).resolve()
    if platform.system() == "Windows":
        return str(p)
    return "Z:" + str(p).replace("/", "\\")


def run_tool(tc: Toolchain, exe_name: str, args: list[str], *, cwd: Path | None = None) -> None:
    exe = tc.resolve(exe_name)
    if platform.system() == "Windows":
        cmd = [str(exe), *args]
    else:
        if not tc.wine:
            raise RuntimeError(
                "Wine is required on macOS to run orbis-pub-cmd.exe / gengp4.exe. "
                "See docs/SETUP_MACOS.md (Gcenx Wine)."
            )
        win_args = [
            to_wine_path(a) if a.startswith("/") and Path(a).exists() else a for a in args
        ]
        # Apple Silicon: Gcenx wine is x86_64 — wrapper scripts usually handle arch -x86_64
        cmd = [tc.wine, to_wine_path(exe), *win_args]

    env = os.environ.copy()
    env.setdefault("WINEDEBUG", "-all")
    env.setdefault("WINEDLLOVERRIDES", "mscoree=d;mshtml=d")
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        env=env,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"Tool failed ({exe_name}): rc={proc.returncode}\n"
            f"stdout: {proc.stdout[-2000:]}\nstderr: {proc.stderr[-2000:]}"
        )


def check_toolchain(tc: Toolchain) -> list[str]:
    problems: list[str] = []
    if not tc.root.is_dir():
        problems.append(f"Tools directory missing: {tc.root}")
        return problems
    for name in REQUIRED_EXES:
        if not (tc.root / name).is_file():
            problems.append(f"Missing {name} in {tc.root}")
    if platform.system() != "Windows" and not tc.wine:
        problems.append("Wine not found (required on macOS)")
    if not tc.magick and not (tc.root / "magick.exe").is_file():
        problems.append("ImageMagick not found (brew install imagemagick)")
    return problems
