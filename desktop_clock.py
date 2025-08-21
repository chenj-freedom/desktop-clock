#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cross-platform desktop clock

Features:
- Always stays on top with focus priority
- Windows/Linux uses -topmost
- macOS uses NSFloatingWindowLevel (PyObjC)  
- Display HH:MM:SS.mmm format
- Draggable, right-click to exit

Usage:
- Install dependencies first: pip install pyobjc
- Windows: Rename to *.pyw and double-click to run
- Other platforms: python desktop_clock.py
"""

import sys
import time
from datetime import datetime
import tkinter as tk
from tkinter import font as tkfont

UPDATE_INTERVAL_MS = 16  # Refresh interval, 16≈60fps, 1=high frequency but CPU intensive


class DesktopClock:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Clock")
        self.root.configure(bg="#111318")

        # Default always on top (Windows/Linux)
        try:
            self.root.attributes("-topmost", True)
        except Exception:
            pass

        # Remove title bar for clean floating window
        try:
            self.root.overrideredirect(True)
        except Exception:
            pass

        # Font settings
        try:
            self.time_font = tkfont.Font(family="JetBrains Mono", size=28, weight="bold")
            self.ms_font = tkfont.Font(family="JetBrains Mono", size=16)
        except Exception:
            self.time_font = tkfont.Font(family="Courier", size=28, weight="bold")
            self.ms_font = tkfont.Font(family="Courier", size=16)

        # Time labels
        self.hhmmss = tk.Label(self.root, text="00:00:00", font=self.time_font,
                               fg="#E6E6E6", bg="#111318")
        self.hhmmss.pack(side="left", padx=(10, 0))

        self.dot = tk.Label(self.root, text=".", font=self.time_font,
                            fg="#9AC1FF", bg="#111318")
        self.dot.pack(side="left", padx=(2, 0))

        self.mmm = tk.Label(self.root, text="000", font=self.ms_font,
                            fg="#9AC1FF", bg="#111318")
        self.mmm.pack(side="left", padx=(0, 10))

        # Drag window functionality
        self._drag_data = {"x": 0, "y": 0}
        for w in (self.root, self.hhmmss, self.dot, self.mmm):
            w.bind("<ButtonPress-1>", self._on_start_move)
            w.bind("<B1-Motion>", self._on_move)
            w.bind("<Button-3>", lambda e: self.root.destroy())

        # Window size and position
        self.root.update_idletasks()
        w = self.hhmmss.winfo_reqwidth() + self.dot.winfo_reqwidth() + self.mmm.winfo_reqwidth() + 30
        h = max(self.hhmmss.winfo_reqheight(), self.mmm.winfo_reqheight()) + 20
        sw = self.root.winfo_screenwidth()
        self.root.geometry(f"{w}x{h}+{sw - w - 40}+40")

        # macOS special handling: true global floating
        if sys.platform == "darwin":
            self._make_macos_floating()

        # Start refresh cycle
        self._schedule_next_tick()

    def _on_start_move(self, event):
        self._drag_data["x"] = event.x_root - self.root.winfo_x()
        self._drag_data["y"] = event.y_root - self.root.winfo_y()

    def _on_move(self, event):
        x = event.x_root - self._drag_data["x"]
        y = event.y_root - self._drag_data["y"]
        self.root.geometry(f"+{x}+{y}")

    def _update_time(self):
        now = datetime.now()
        self.hhmmss.config(text=now.strftime("%H:%M:%S"))
        self.mmm.config(text=f"{int(now.microsecond/1000):03d}")
        self._schedule_next_tick()

    def _schedule_next_tick(self):
        now_ns = time.perf_counter_ns()
        interval_ns = int(UPDATE_INTERVAL_MS * 1_000_000)
        next_tick_ns = ((now_ns // interval_ns) + 1) * interval_ns
        delay_ms = max(1, int((next_tick_ns - now_ns) / 1_000_000))
        self.root.after(delay_ms, self._update_time)

    def _make_macos_floating(self):
        try:
            from Cocoa import NSApp, NSFloatingWindowLevel
            self.root.update_idletasks()
            nswindow = NSApp().windows()[-1]
            nswindow.setLevel_(NSFloatingWindowLevel)
            print("macOS: Clock window elevated to floating level (NSFloatingWindowLevel)")
        except Exception as e:
            print("macOS: Failed to set floating level:", e)

    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    DesktopClock().run()
