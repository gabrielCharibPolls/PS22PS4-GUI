#!/usr/bin/env bash
# Build portable macOS (.app) + Windows zip, with tools + JakV2 emulator.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="${VERSION:-1.1.0}"
DIST="$ROOT/dist"
MAC_OUT="$DIST/PS22PSX-${VERSION}-macOS"
WIN_OUT="$DIST/PS22PSX-${VERSION}-Windows"
TOOLS_SRC="$ROOT/ps22psx/bin/tools"
EMU_SRC="$ROOT/ps22psx/bin/emulators/JakV2.pkg"

die() { echo "error: $*" >&2; exit 1; }

[[ -x "$TOOLS_SRC/orbis-pub-cmd.exe" ]] || die "missing tools in ps22psx/bin/tools"
[[ -f "$EMU_SRC" ]] || die "missing emulator JakV2.pkg"

echo "==> Cleaning dist"
rm -rf "$DIST"
mkdir -p "$MAC_OUT" "$WIN_OUT"

echo "==> Building SwiftUI macOS binary"
cd "$ROOT/macos/PS22PSX"
swift build -c release
BIN="$ROOT/macos/PS22PSX/.build/release/PS22PSX"
[[ -x "$BIN" ]] || die "swift binary missing"

echo "==> Assembling macOS .app"
APP="$MAC_OUT/PS22PSX.app"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources" "$MAC_OUT/Support/bin/tools" "$MAC_OUT/Support/bin/emulators"

cp "$BIN" "$APP/Contents/MacOS/PS22PSX"
chmod +x "$APP/Contents/MacOS/PS22PSX"

cat > "$APP/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key><string>PS22PSX</string>
  <key>CFBundleDisplayName</key><string>PS22PSX</string>
  <key>CFBundleIdentifier</key><string>com.gabrielcharibpolls.ps22psx</string>
  <key>CFBundleVersion</key><string>${VERSION}</string>
  <key>CFBundleShortVersionString</key><string>${VERSION}</string>
  <key>CFBundleExecutable</key><string>PS22PSX</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>LSMinimumSystemVersion</key><string>13.0</string>
  <key>NSHighResolutionCapable</key><true/>
</dict>
</plist>
EOF

# Python engine + venv next to the app
echo "==> Bundling Python engine for macOS Support/"
rsync -a --exclude '.venv' --exclude 'out' --exclude '.wine-tmp' --exclude 'testdata/*.iso' \
  --exclude '__pycache__' --exclude '*.egg-info' --exclude '.pytest_cache' \
  "$ROOT/ps22psx/" "$MAC_OUT/Support/ps22psx/"

python3 -m venv "$MAC_OUT/Support/ps22psx/.venv"
"$MAC_OUT/Support/ps22psx/.venv/bin/pip" install -q -e "$MAC_OUT/Support/ps22psx"

# Tools + emulator
rsync -a "$TOOLS_SRC/" "$MAC_OUT/Support/bin/tools/"
cp "$EMU_SRC" "$MAC_OUT/Support/bin/emulators/JakV2.pkg"

cat > "$MAC_OUT/README.txt" << EOF
PS22PSX ${VERSION} — macOS
========================
1) Install Wine (Gcenx) + Rosetta if Apple Silicon — see Support/ps22psx/docs/SETUP_MACOS.md
2) Double-click PS22PSX.app
3) Emulator included: Support/bin/emulators/JakV2.pkg
4) Tools included: Support/bin/tools/

Doctor / CLI:
  cd Support/ps22psx && source .venv/bin/activate && ps22psx doctor
EOF

cat > "$MAC_OUT/Launch.command" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
open PS22PSX.app
EOF
chmod +x "$MAC_OUT/Launch.command"

echo "==> Assembling Windows portable zip contents"
rsync -a --exclude '.venv' --exclude 'out' --exclude '.wine-tmp' --exclude 'testdata/*.iso' \
  --exclude '__pycache__' --exclude '*.egg-info' --exclude '.pytest_cache' \
  "$ROOT/ps22psx/" "$WIN_OUT/ps22psx/"
mkdir -p "$WIN_OUT/bin/tools" "$WIN_OUT/bin/emulators"
rsync -a "$TOOLS_SRC/" "$WIN_OUT/bin/tools/"
cp "$EMU_SRC" "$WIN_OUT/bin/emulators/JakV2.pkg"

# Windows does not need the Swift app — Tk GUI + CLI
cat > "$WIN_OUT/run-gui.bat" << 'EOF'
@echo off
cd /d "%~dp0"
if not exist "ps22psx\.venv\Scripts\python.exe" (
  py -3 -m venv ps22psx\.venv
  ps22psx\.venv\Scripts\pip install -e ps22psx
)
set PS22PSX_TOOLS=%~dp0bin\tools
ps22psx\.venv\Scripts\ps22psx.exe gui
pause
EOF

cat > "$WIN_OUT/run-doctor.bat" << 'EOF'
@echo off
cd /d "%~dp0"
if not exist "ps22psx\.venv\Scripts\python.exe" (
  py -3 -m venv ps22psx\.venv
  ps22psx\.venv\Scripts\pip install -e ps22psx
)
set PS22PSX_TOOLS=%~dp0bin\tools
ps22psx\.venv\Scripts\ps22psx.exe doctor
pause
EOF

cat > "$WIN_OUT/README.txt" << EOF
PS22PSX ${VERSION} — Windows
==========================
Requires: Python 3.10+ (python.org)

1) Double-click run-gui.bat (creates venv on first run)
2) Emulator: bin\emulators\JakV2.pkg
3) Tools: bin\tools\

Build fPKG for jailbroken PS4 only.
EOF

echo "==> Zipping"
cd "$DIST"
ditto -c -k --sequesterRsrc --keepParent "PS22PSX-${VERSION}-macOS" "PS22PSX-${VERSION}-macOS.zip"
ditto -c -k --keepParent "PS22PSX-${VERSION}-Windows" "PS22PSX-${VERSION}-Windows.zip"

echo "==> Done"
ls -lh "$DIST"/*.zip
du -sh "$MAC_OUT" "$WIN_OUT"
