# PS22PSX

Cross-platform revival of [PS22PS4-GUI](https://github.com/Nazky/PS22PS4-GUI): build **PS2 → PS4 Classics fPKG** on **macOS**, Windows and Linux.  
Works on **jailbroken PS4** and **exploited PS5** (HEN + PS4 FPKG Enabler / kstuff).

## Why a rewrite?

The original app is VB.NET WinForms + Windows-only `.exe` tools. This package:

- Runs on **macOS** (Wine only for Orbis publish tools)
- Completes the old TODOs: **proper config maker**, **LUA maker**, **CLI**
- Adds explicit `--target ps4|ps5` and console test docs

Legacy VB sources stay in `../PS22PS4-GUI/` for reference.

## Quick start (macOS)

```bash
cd ps22psx
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
brew install imagemagick
brew install --cask wine-stable   # for orbis-pub-cmd.exe
ps22psx doctor
```

See [docs/SETUP_MACOS.md](docs/SETUP_MACOS.md).

## CLI (TODOs done)

```bash
# Inspect ISO/BIN
ps22psx info game.iso

# Config maker
ps22psx config --list
ps22psx config --title-id SLUS-20001 --name "Ridge Racer V" -o game.conf

# LUA maker
ps22psx lua --title-id SLUS-20001 -o SLUS-20001_config.lua

# Build PKG
ps22psx create game.iso \
  --emulator path/to/emulator.pkg \
  --icon cover.png --background back.jpg \
  --config game.conf --lua SLUS-20001_config.lua \
  --output out --target ps5

# GUI
ps22psx gui
```

## Console testing

[docs/TESTING_CONSOLES.md](docs/TESTING_CONSOLES.md)

## Tests

```bash
pytest -q
```

## Credits

- Original GUI: [Nazky/PS22PS4-GUI](https://github.com/Nazky/PS22PS4-GUI)
- Tools lineage: CyB1K PS4 Fake PKG Tools, Markus95 PS22PS4/PS22PS5
