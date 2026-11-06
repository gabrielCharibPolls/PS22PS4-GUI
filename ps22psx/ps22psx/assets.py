"""Cover / background image preparation."""

from __future__ import annotations

from pathlib import Path

from PIL import Image


def prepare_icon(src: Path, dest_png: Path, size: tuple[int, int] = (512, 512)) -> Path:
    dest_png.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im = im.convert("RGBA")
        im = im.resize(size, Image.Resampling.LANCZOS)
        im.save(dest_png, format="PNG")
    return dest_png


def prepare_background(src: Path, dest_png: Path, size: tuple[int, int] = (1920, 1080)) -> Path:
    dest_png.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im = im.convert("RGB")
        im = im.resize(size, Image.Resampling.LANCZOS)
        # PS4 Classics often uses pic1.png
        im.save(dest_png, format="PNG")
    return dest_png


def prepare_save_data_icon(icon_png: Path, dest_png: Path, size: tuple[int, int] = (228, 128)) -> Path:
    dest_png.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(icon_png) as im:
        im = im.convert("RGBA")
        im = im.resize(size, Image.Resampling.LANCZOS)
        im.save(dest_png, format="PNG")
    return dest_png
