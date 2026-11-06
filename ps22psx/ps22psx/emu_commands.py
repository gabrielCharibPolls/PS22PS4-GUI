"""PS2 Classics emulator config flags (config-emu-ps4.txt).

Catalog derived from the original CreateConfig UI and psdevwiki docs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class EmuCommand:
    flag: str
    category: str
    description: str
    example: str = ""
    values: tuple[str, ...] = ()


COMMANDS: tuple[EmuCommand, ...] = (
    EmuCommand("--ps2-title-id", "ps2", "Force PS2 title id", "SLUS-20091"),
    EmuCommand("--ps2-lang", "ps2", "Language override", "1", ("0", "1", "2", "3", "4", "5")),
    EmuCommand("--max-disc-num", "misc", "Number of discs", "1"),
    EmuCommand("--boot-disc-id", "misc", "Boot disc index", "1"),
    EmuCommand("--switch-disc-reset", "misc", "Reset on disc switch", "1", ("0", "1")),
    EmuCommand("--config-local-lua", "misc", "Enable local lua patches", "1", ("0", "1")),
    EmuCommand("--load-tooling-lua", "misc", "Load tooling lua", "1", ("0", "1")),
    EmuCommand("--gs-uprender", "gs", "GS uprender mode", "none", ("none", "gpu", "edgesmooth", "motionvec")),
    EmuCommand("--gs-upscale", "gs", "GS upscale mode", "none", ("none", "point", "motionvector", "smooth", "motion")),
    EmuCommand("--framelimiter", "host", "Enable framelimiter", "1", ("0", "1")),
    EmuCommand("--framelimit-fps", "host", "Target FPS", "60"),
    EmuCommand("--framelimit-mode", "host", "Framelimit mode", "normal", ("slowest", "slower", "slow", "normal", "fast", "fastest", "turbo")),
    EmuCommand("--host-vsync", "host", "VSync", "1", ("0", "1")),
    EmuCommand("--host-display-mode", "host", "Display mode", "normal", ("normal", "full")),
    EmuCommand("--host-osd", "host", "On-screen display", "minimal", ("none", "minimal", "fps", "verbose")),
    EmuCommand("--host-audio", "audio", "Host audio", "1", ("0", "1")),
    EmuCommand("--host-audio-latency", "audio", "Audio latency ms", "80"),
    EmuCommand("--mute-audio", "audio", "Mute audio buses", "none", ("none", "main", "bgm", "all")),
    EmuCommand("--mute-streaming-audio", "audio", "Mute streaming audio", "none", ("none", "main", "bgm", "all")),
    EmuCommand("--cdvd-sector-read-cycles", "cdvd", "CDVD sector read cycles", "50000"),
    EmuCommand("--cdvd-sector-seek-cycles", "cdvd", "CDVD sector seek cycles", "50000"),
    EmuCommand("--verbose-cdvd-reads", "cdvd", "Verbose CDVD reads", "0", ("0", "1")),
    EmuCommand("--host-gamepads", "controllers", "Enable gamepads", "1", ("0", "1")),
    EmuCommand("--pad-analog-to-digital", "controllers", "Map analog to digital", "0", ("0", "1")),
    EmuCommand("--ds4-deadzone-adjust", "controllers", "DS4 deadzone", "0.0"),
    EmuCommand("--ds4-diagonal-adjust", "controllers", "DS4 diagonal adjust", "0.0"),
    EmuCommand("--mtap1", "controllers", "Multitap port 1", "disabled", ("disabled", "always", "byhost")),
    EmuCommand("--mtap2", "controllers", "Multitap port 2", "disabled", ("disabled", "always", "byhost")),
    EmuCommand("--path-patches", "path", "Patches directory", "./patches"),
    EmuCommand("--path-memcards", "path", "Memory cards path", "./memcards"),
    EmuCommand("--path-vmc", "path", "VMC path", "./vmc"),
    EmuCommand("--path-snaps", "path", "Snapshots path", "./snaps"),
    EmuCommand("--host-trophy-support", "host", "Trophy support", "0", ("0", "1")),
)


def by_category() -> dict[str, list[EmuCommand]]:
    out: dict[str, list[EmuCommand]] = {}
    for cmd in COMMANDS:
        out.setdefault(cmd.category, []).append(cmd)
    return out


def default_config(game_name: str, game_id: str, max_discs: int = 1) -> str:
    lines = [
        f"# {game_name}",
        f"--ps2-title-id={game_id}",
        f"--max-disc-num={max_discs}",
        "--config-local-lua=1",
        "",
        "# Add compatibility flags below (see `ps22psx config --list`)",
        "",
    ]
    return "\n".join(lines)


def format_command(flag: str, value: str | None = None) -> str:
    if value is None or value == "":
        return flag
    return f"{flag}={value}"


def merge_flags(existing: str, flags: Iterable[str]) -> str:
    lines = [ln.rstrip() for ln in existing.splitlines()]
    present = {ln.split("=", 1)[0].strip() for ln in lines if ln.strip().startswith("--")}
    for flag in flags:
        key = flag.split("=", 1)[0].strip()
        if key in present:
            lines = [flag if ln.split("=", 1)[0].strip() == key else ln for ln in lines]
        else:
            lines.append(flag)
            present.add(key)
    return "\n".join(lines).rstrip() + "\n"
