"""Locate packaging tools and run them (Wine on macOS/Linux)."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


REQUIRED_EXES = (
    "orbis-pub-cmd.exe",
    "gengp4.exe",
    "replhex.exe",
)


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
    return None


def find_magick() -> str | None:
    # Prefer native ImageMagick on macOS/Linux
    for candidate in ("magick", "convert"):
        path = shutil.which(candidate)
        if path:
            return path
    return None


def default_tools_dir() -> Path:
    env = os.environ.get("PS22PSX_TOOLS")
    if env:
        return Path(env).expanduser().resolve()
    # Common layouts: ./bin/tools next to CWD, or sibling of package
    cwd = Path.cwd()
    candidates = [
        cwd / "bin" / "tools",
        cwd / "tools",
        Path(__file__).resolve().parents[2] / "bin" / "tools",
        Path(__file__).resolve().parents[1] / "bin" / "tools",
    ]
    for c in candidates:
        if c.is_dir():
            return c
    return candidates[0]


def load_toolchain(tools_dir: Path | None = None) -> Toolchain:
    root = Path(tools_dir) if tools_dir else default_tools_dir()
    wine = None if platform.system() == "Windows" else find_wine()
    return Toolchain(root=root, wine=wine, magick=find_magick())


def run_tool(tc: Toolchain, exe_name: str, args: list[str], *, cwd: Path | None = None) -> None:
    exe = tc.resolve(exe_name)
    if platform.system() == "Windows":
        cmd = [str(exe), *args]
    else:
        if not tc.wine:
            raise RuntimeError(
                "Wine is required on macOS/Linux to run PS4 packaging tools "
                "(orbis-pub-cmd.exe, gengp4.exe). Install with: brew install --cask wine-stable"
            )
        cmd = [tc.wine, str(exe), *args]

    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
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
        problems.append("Wine not found (required on macOS/Linux)")
    if not tc.magick and not (tc.root / "magick.exe").is_file():
        problems.append("ImageMagick not found (brew install imagemagick)")
    return problems
