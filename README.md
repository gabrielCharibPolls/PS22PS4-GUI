<p align="center"><img src="PS22PS4-GUI/Ressource/ps2_icon_by_natstrodamus_deqcdvd.ico" width="100px" /></p>
<h1 align="center">PS22PSX</h1>
<h2 align="center">PS2 ISO/BIN → PS4 Classics fPKG</h2>
<p align="center">macOS-first · Windows portable · jailbroken PS4 only</p>

---

### What is this?

Build a PS2 `.iso` / `.bin` into a **PS4 Classics fake PKG** for a **jailbroken PS4**.

| Path | Role |
|------|------|
| [`ps22psx/`](ps22psx/) | Active engine — Python CLI (+ Tk fallback) |
| [`macos/PS22PSX/`](macos/PS22PSX/) | Native **SwiftUI** Mac app (calls the CLI) |
| [`PS22PS4-GUI/`](PS22PS4-GUI/) | Legacy VB.NET GUI (Windows reference only) |

**PS5 is not supported.** On PS5, use PCSX2 / PS5SX2 instead.

### Downloads

Release zips (tools + **JakV2** emulator included):

- build locally: `./scripts/build-release.sh`
- artifacts: `dist/PS22PSX-*-macOS.zip` and `dist/PS22PSX-*-Windows.zip`

### Quick start — macOS

```bash
cd ps22psx
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
brew install imagemagick
# Wine (Gcenx) required for orbis-pub-cmd — see docs
ps22psx doctor
```

Native UI:

```bash
cd macos/PS22PSX
swift build -c release
./.build/release/PS22PSX
```

Docs: [SETUP_MACOS.md](ps22psx/docs/SETUP_MACOS.md) · [TESTING_PS4.md](ps22psx/docs/TESTING_PS4.md)

### Quick start — Windows

```bat
run-gui.bat
```

(from the Windows release zip; creates a venv on first launch)

### CLI

```bash
ps22psx info game.iso
ps22psx config --list
ps22psx lua --title-id SLUS-20001 -o SLUS-20001_config.lua
ps22psx create game.iso \
  --emulator bin/emulators/JakV2.pkg \
  --icon cover.png --background back.jpg \
  --output out
```

### Status

- [x] BIN / multi-disc
- [x] Config + LUA makers
- [x] CLI + Tk GUI
- [x] Native macOS SwiftUI app
- [x] Portable Mac / Windows release script
- [x] PS5 packaging removed

### Compatibility

Game list: [PS2 Classics Emulator Compatibility List](https://www.psdevwiki.com/ps4/PS2_Classics_Emulator_Compatibility_List)

### Credits

See [CONTRIBUTORS.md](CONTRIBUTORS.md).

- [gabrielCharibPolls](https://github.com/gabrielCharibPolls) — maintainer
- [Nazky](https://github.com/Nazky/PS22PS4-GUI) — original GUI
- [CyB1K](https://github.com/CyB1K) — PS4 Fake PKG Tools
- [Markus95](https://twitter.com/Markus00095) — PS22PS4
