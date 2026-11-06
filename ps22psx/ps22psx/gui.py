"""Minimal cross-platform Tk GUI for PS22PSX."""

from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .pkg_builder import BuildRequest, build_pkg


class App(ttk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=12)
        self.master.title("PS22PSX — PS2 → PS4/PS5 fPKG")
        self.grid(sticky="nsew")
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)

        self.images = tk.StringVar()
        self.emulator = tk.StringVar()
        self.icon = tk.StringVar()
        self.background = tk.StringVar()
        self.output = tk.StringVar(value=str(Path.cwd() / "out"))
        self.name = tk.StringVar()
        self.target = tk.StringVar(value="ps4")
        self.config = tk.StringVar()
        self.lua = tk.StringVar()

        r = 0
        for label, var, cmd in (
            ("ISO/BIN (multi ok)", self.images, self._pick_images),
            ("Emulator PKG", self.emulator, lambda: self._pick_file(self.emulator, [("PKG", "*.pkg")])),
            ("Icon / cover", self.icon, lambda: self._pick_file(self.icon, [("Images", "*.png *.jpg *.jpeg")])),
            ("Background", self.background, lambda: self._pick_file(self.background, [("Images", "*.png *.jpg *.jpeg")])),
            ("Output folder", self.output, self._pick_dir),
            ("Config (optional)", self.config, lambda: self._pick_file(self.config, [("Config", "*.txt *.conf")])),
            ("LUA (optional)", self.lua, lambda: self._pick_file(self.lua, [("LUA", "*.lua")])),
        ):
            ttk.Label(self, text=label).grid(row=r, column=0, sticky="w")
            ttk.Entry(self, textvariable=var, width=64).grid(row=r, column=1, sticky="ew", padx=6)
            ttk.Button(self, text="…", width=3, command=cmd).grid(row=r, column=2)
            r += 1

        ttk.Label(self, text="Game name").grid(row=r, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.name).grid(row=r, column=1, sticky="ew", padx=6)
        r += 1

        ttk.Label(self, text="Target").grid(row=r, column=0, sticky="w")
        ttk.Combobox(self, textvariable=self.target, values=("ps4", "ps5"), state="readonly", width=10).grid(
            row=r, column=1, sticky="w", padx=6
        )
        r += 1

        self.log = tk.Text(self, height=14, width=80)
        self.log.grid(row=r, column=0, columnspan=3, sticky="nsew", pady=8)
        self.rowconfigure(r, weight=1)
        self.columnconfigure(1, weight=1)
        r += 1

        self.btn = ttk.Button(self, text="Create PKG", command=self._start)
        self.btn.grid(row=r, column=0, columnspan=3, sticky="ew")

    def _pick_images(self) -> None:
        paths = filedialog.askopenfilenames(filetypes=[("PS2 images", "*.iso *.bin *.ISO *.BIN")])
        if paths:
            self.images.set("\n".join(paths))

    def _pick_file(self, var: tk.StringVar, types: list) -> None:
        path = filedialog.askopenfilename(filetypes=types)
        if path:
            var.set(path)

    def _pick_dir(self) -> None:
        path = filedialog.askdirectory()
        if path:
            self.output.set(path)

    def _append(self, msg: str) -> None:
        self.log.insert("end", msg + "\n")
        self.log.see("end")

    def _start(self) -> None:
        imgs = [Path(p.strip()) for p in self.images.get().splitlines() if p.strip()]
        if not imgs:
            messagebox.showerror("PS22PSX", "Select at least one ISO/BIN")
            return
        self.btn.configure(state="disabled")
        self.log.delete("1.0", "end")

        req = BuildRequest(
            images=imgs,
            emulator_pkg=Path(self.emulator.get()),
            icon=Path(self.icon.get()),
            background=Path(self.background.get()),
            output_dir=Path(self.output.get()),
            game_name=self.name.get() or None,
            config_file=Path(self.config.get()) if self.config.get() else None,
            lua_file=Path(self.lua.get()) if self.lua.get() else None,
            target=self.target.get(),
        )

        def worker() -> None:
            try:
                result = build_pkg(req, log=lambda m: self.after(0, self._append, m))
                self.after(0, self._append, f"Done: {result.pkg_path}")
                self.after(0, messagebox.showinfo, "PS22PSX", f"PKG ready:\n{result.pkg_path}")
            except Exception as exc:  # noqa: BLE001
                self.after(0, self._append, f"ERROR: {exc}")
                self.after(0, messagebox.showerror, "PS22PSX", str(exc))
            finally:
                self.after(0, self.btn.configure, {"state": "normal"})

        threading.Thread(target=worker, daemon=True).start()


def run_gui() -> None:
    root = tk.Tk()
    root.minsize(720, 480)
    App(root)
    root.mainloop()
