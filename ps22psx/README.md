# PS22PSX

macOS-first PS2 ISO/BIN → **PS4 Classics fPKG** builder (CLI + GUI).

> PS5 support was removed: use PCSX2/PS5SX2 on exploited PS5 instead.  
> This tool targets **jailbroken PS4** only.

## Quick start (macOS)

```bash
cd ps22psx
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
brew install imagemagick
# Wine (Gcenx) + bin/tools — see docs/SETUP_MACOS.md
ps22psx doctor
```

### Native Mac UI (SwiftUI)

Python reste le moteur (CLI). L’interface Mac native est dans `macos/PS22PSX` :

```bash
cd macos/PS22PSX
swift build -c release
./.build/release/PS22PSX
```

## CLI

```bash
ps22psx info game.iso
ps22psx config --list
ps22psx config --title-id SLUS-20001 --name "Game" -o game.conf
ps22psx lua --title-id SLUS-20001 -o SLUS-20001_config.lua
ps22psx create game.iso \
  --emulator path/to/emulator.pkg \
  --icon cover.png --background back.jpg \
  --output out
ps22psx gui
```

## Docs

- [docs/SETUP_MACOS.md](docs/SETUP_MACOS.md)
- [docs/TESTING_PS4.md](docs/TESTING_PS4.md)

## Tests

```bash
pytest -q
```

## Credits

Human credits only — see [../CONTRIBUTORS.md](../CONTRIBUTORS.md).

- Maintainer: [gabrielCharibPolls](https://github.com/gabrielCharibPolls)
- Original GUI: [Nazky/PS22PS4-GUI](https://github.com/Nazky/PS22PS4-GUI)
- Tools: CyB1K Fake PKG Tools, Markus95 PS22PS4
