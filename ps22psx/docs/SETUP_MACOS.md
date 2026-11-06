# Setup macOS (Apple Silicon / Intel)

PS22PSX runs natively on macOS. The Sony/Orbis packaging binaries (`orbis-pub-cmd.exe`, `gengp4.exe`, `replhex.exe`) are still Windows PE files, so **Wine** is required only for the final PKG compile step.

## 1. Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## 2. ImageMagick (native)

```bash
brew install imagemagick
```

## 3. Wine

```bash
brew install --cask wine-stable
# or: brew install wine-crossover / wine@staging depending on your Mac
wine64 --version
```

On first run, Wine may create a prefix (`~/.wine`). Accept the defaults.

## 4. Packaging tools (`bin/tools`)

Place the PS4 Fake PKG tools (same set used by the legacy GUI) in:

```text
bin/tools/
  orbis-pub-cmd.exe
  gengp4.exe
  replhex.exe
```

You can override the path:

```bash
export PS22PSX_TOOLS=/absolute/path/to/tools
ps22psx doctor
```

## 5. Emulator base PKG

Put at least one decrypted/base **PS2 Classics emulator `.pkg`** in a folder of your choice, then pass it with `--emulator`.

## 6. Verify

```bash
ps22psx doctor
ps22psx config --list
ps22psx --help
```

## GUI

```bash
ps22psx gui
```
