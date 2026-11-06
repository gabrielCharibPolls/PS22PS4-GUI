<p align="center"><img src="PS22PS4-GUI/Ressource/ps2_icon_by_natstrodamus_deqcdvd.ico" width="100px" /></p>
<h1 align="center">PS22PS4-GUI → PS22PSX</h1>
<h2 align="center">PS2 ISO/BIN → PS4 / PS5 Classics fPKG</h2>

---

### Status 2026 revival

This repository now includes **PS22PSX**, a cross-platform Python rewrite that runs on **macOS**, Windows and Linux.

| Path | What |
|------|------|
| [`ps22psx/`](ps22psx/) | **Active** — CLI, GUI, config/LUA makers, Mac support |
| [`PS22PS4-GUI/`](PS22PS4-GUI/) | Legacy VB.NET WinForms (Windows only, kept for reference) |

### TODOs

- [x] Add bin support
- [x] Add proper config maker → `ps22psx config`
- [x] Add proper LUA maker → `ps22psx lua`
- [x] Add CLI support → `ps22psx create`
- [x] Add cfgbin support (legacy)
- [x] Add others emulators (legacy + `--emulator`)
- [x] Add multi-disc support
- [x] macOS support (Wine for Orbis tools)
- [x] PS5 HEN target docs (`--target ps5`)

### Quick start (macOS)

```bash
cd ps22psx
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
ps22psx doctor
ps22psx gui
```

Full guides:

- [ps22psx/docs/SETUP_MACOS.md](ps22psx/docs/SETUP_MACOS.md)
- [ps22psx/docs/TESTING_CONSOLES.md](ps22psx/docs/TESTING_CONSOLES.md) — PS4 jailbreak & PS5 exploited

### F.A.Q

#### What is this?

Build a PS2 ISO/BIN into a PS4 Classics **fake PKG** so you can play on a **jailbroken PS4**, or an **exploited PS5** with PS4 FPKG Enabler / kstuff.

#### Does it work on a normal PS5?

**No.** Stock PS5 cannot install these packages.

#### All games working?

No — see the [compatibility list](https://www.psdevwiki.com/ps4/PS2_Classics_Emulator_Compatibility_List).

### Credit

- [Nazky](https://github.com/Nazky/PS22PS4-GUI) — original GUI
- [CyB1K](https://github.com/CyB1K) — PS4 Fake PKG Tools
- [Markus95](https://twitter.com/Markus00095) — PS22PS4 / PS22PS5
