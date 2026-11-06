<p align="center"><img src="PS22PS4-GUI/Ressource/ps2_icon_by_natstrodamus_deqcdvd.ico" width="100px" /></p>
<h1 align="center">PS22PS4-GUI → PS22PSX</h1>
<h2 align="center">PS2 ISO/BIN → PS4 Classics fPKG (macOS-first)</h2>

---

### Status

| Path | What |
|------|------|
| [`ps22psx/`](ps22psx/) | **Active** — Python CLI/GUI for **jailbroken PS4** |
| [`PS22PS4-GUI/`](PS22PS4-GUI/) | Legacy VB.NET WinForms (Windows only, reference) |

**PS5 is out of scope.** On exploited PS5, use PCSX2 / PS5SX2 instead.

### TODOs

- [x] BIN support
- [x] Config maker → `ps22psx config`
- [x] LUA maker → `ps22psx lua`
- [x] CLI → `ps22psx create`
- [x] macOS (Wine for Orbis tools only)
- [x] Multi-disc
- [x] Dropped PS5 / HEN packaging path

### Quick start (macOS)

```bash
cd ps22psx
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
ps22psx doctor
ps22psx gui
```

- [ps22psx/docs/SETUP_MACOS.md](ps22psx/docs/SETUP_MACOS.md)
- [ps22psx/docs/TESTING_PS4.md](ps22psx/docs/TESTING_PS4.md)

### F.A.Q

#### What is this?

Build a PS2 ISO/BIN into a PS4 Classics **fake PKG** for a **jailbroken PS4**.

#### PS5?

Not supported by this tool. Use a PS2 emulator homebrew on PS5 (e.g. PCSX2/PS5SX2).

#### All games working?

No — see the [compatibility list](https://www.psdevwiki.com/ps4/PS2_Classics_Emulator_Compatibility_List).

### Credit

- [gabrielCharibPolls](https://github.com/gabrielCharibPolls) — maintainer
- [Nazky](https://github.com/Nazky/PS22PS4-GUI) — original GUI
- [CyB1K](https://github.com/CyB1K) — PS4 Fake PKG Tools
- [Markus95](https://twitter.com/Markus00095) — PS22PS4
