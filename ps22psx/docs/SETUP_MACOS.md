# Setup macOS

PS22PSX is **macOS-first**: Python + native ImageMagick.  
Sony Orbis tools (`orbis-pub-cmd.exe`, `gengp4.exe`) still need **Wine** (x86_64 / Rosetta).

## 1. Python

```bash
cd ps22psx
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## 2. ImageMagick (native)

```bash
brew install imagemagick
```

## 3. Wine (Gcenx)

Homebrew `wine-stable` may be disabled by Gatekeeper. Use Gcenx builds:

1. Download `wine-stable-*-osx64.tar.xz` from  
   https://github.com/Gcenx/macOS_Wine_builds/releases  
2. Extract, then either put `wine` on your `PATH`, or create `~/bin/wine64`:

```bash
mkdir -p ~/bin
cat > ~/bin/wine64 << 'EOF'
#!/bin/bash
export PATH="$HOME/wine-gcenx/Wine Stable.app/Contents/Resources/wine/bin:$PATH"
exec arch -x86_64 wine "$@"
EOF
chmod +x ~/bin/wine64
export PATH="$HOME/bin:$PATH"
```

Rosetta is required on Apple Silicon.

## 4. Packaging tools

Place CyB1K / Nazky tools in `bin/tools/`:

- `orbis-pub-cmd.exe`
- `gengp4.exe`

```bash
export PS22PSX_TOOLS=/absolute/path/to/tools   # optional override
ps22psx doctor
```

## 5. Emulator base PKG

Put a PS2 Classics emulator `.pkg` somewhere and pass `--emulator`.

## Verify

```bash
ps22psx doctor
ps22psx gui
```
