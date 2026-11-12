"""
ui/widgets.py - Widgets gráficos personalizados para el Simulador DC (Fase 3).
Autor: José Rolando Álvarez Mejía (Equipo G01T - ACE941 / ACE404)

Contiene componentes visuales reutilizables dibujados directamente sobre Tkinter Canvas.
Garantiza visibilidad y contraste perfecto tanto en macOS (Aqua Dark/Light) como en
Windows, evitando las inconsistencias de renderizado de los controles nativos.
"""

import tkinter as tk


class VisibleSlider(tk.Canvas):
    """
    Control deslizante de alta visibilidad dibujado en Canvas.
    Proporciona un riel con color de acento (#007AFF) y perilla de alto contraste (#FFFFFF),
    independiente de los fallos de transparencia del gestor de temas del sistema operativo.
    """

    def __init__(self, parent, from_, to, value, command=None, **kwargs):
        super().__init__(parent, height=36, highlightthickness=0, bd=0, **kwargs)
        self.from_ = float(from_)
        self.to = float(to)
        self.val = float(value)
        self.command = command

        self.bind("<Configure>", self._draw)
        self.bind("<Button-1>", self._on_interaction)
        self.bind("<B1-Motion>", self._on_interaction)

    def _val_to_x(self, val, w=None):
        if w is None:
            w = self.winfo_width()
        if w < 50:
            w = 240
        margin = 16
        fraction = (val - self.from_) / (self.to - self.from_)
        return margin + fraction * max(1, w - 2 * margin)

    def _x_to_val(self, x, w=None):
        if w is None:
            w = self.winfo_width()
        if w < 50:
            w = 240
        margin = 16
        fraction = max(0.0, min(1.0, (x - margin) / max(1, w - 2 * margin)))
        return round(self.from_ + fraction * (self.to - self.from_), 1)

    def _draw(self, event=None):
        self.delete("all")
        if event is not None and hasattr(event, "width") and event.width > 50:
            w = event.width
        else:
            w = self.winfo_width()
        if w < 50:
            w = 240

        cy = 18
        margin = 16
        kx = self._val_to_x(self.val, w)

        # Fondo del riel (gris neutro oscuro)
        self.create_line(margin, cy, w - margin, cy, fill="#3A3A3C", width=6, capstyle="round")
        # Progreso activo del riel (azul visible #007AFF)
        self.create_line(margin, cy, kx, cy, fill="#007AFF", width=6, capstyle="round")
        # Perilla arrastrable (círculo blanco con borde azul)
        self.create_oval(kx - 10, cy - 10, kx + 10, cy + 10, fill="#FFFFFF", outline="#007AFF", width=2)

    def _on_interaction(self, event):
        nuevo_val = self._x_to_val(event.x)
        if nuevo_val == self.val:
            return
        self.val = nuevo_val
        self._draw()
        if self.command:
            self.command(self.val)

    def get(self):
        return self.val

    def set(self, val):
        self.val = max(self.from_, min(self.to, float(val)))
        self._draw()
