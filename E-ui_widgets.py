"""
ui_widgets.py
=============
Widgets de Tkinter reutilizables entre distintas ventanas de la app
(botones con estilo propio, paneles de video con título, y filas de
"etiqueta: valor" para mostrar métricas). Extraerlos evita duplicar
código de estilo entre spad_app.py y historial_window.py.
"""

import tkinter as tk

from config import PANEL, TEXT_SEC, TEXT_DIM, BTN_BG, BTN_HOVER, FONT_MONO


def crear_boton(parent, texto, cmd, color):
    """Crea un botón con estilo personalizado (fondo oscuro, color de texto variable, hover)."""
    b = tk.Button(parent, text=texto, command=cmd,
                  bg=BTN_BG, fg=color,
                  activebackground=BTN_HOVER, activeforeground=color,
                  font=("Segoe UI", 11, "bold"),
                  relief="flat", bd=0, padx=24, pady=8, cursor="hand2")
    b.bind("<Enter>", lambda e: b.config(bg=BTN_HOVER))
    b.bind("<Leave>", lambda e: b.config(bg=BTN_BG))
    return b


def crear_panel_video(parent, titulo, ancho, alto):
    """Crea un panel (Canvas con marco y título) usado para mostrar video en vivo o capturas."""
    wrapper = tk.Frame(parent, bg="#1E3028", padx=1, pady=1)
    wrapper.pack(side="left", padx=5)
    inner = tk.Frame(wrapper, bg=PANEL)
    inner.pack()
    tk.Label(inner, text=titulo, bg=PANEL, fg=TEXT_SEC,
             font=("Segoe UI", 7, "bold")).pack(anchor="w", padx=5, pady=(3, 0))
    c = tk.Canvas(inner, width=ancho, height=alto,
                   bg="#080F0B", highlightthickness=0)
    c.pack(padx=0, pady=(2, 4))
    c.create_text(ancho // 2, alto // 2, text="SIN SEÑAL",
                   fill=TEXT_DIM, font=FONT_MONO, tags="nosig")
    return c


def crear_metrica(parent, label, valor, color):
    """Crea una fila 'etiqueta: valor' usada en el panel de resultados promedio."""
    row = tk.Frame(parent, bg=PANEL)
    row.pack(anchor="w", pady=1)
    tk.Label(row, text=f"{label}:", bg=PANEL, fg=TEXT_SEC,
             font=("Segoe UI", 8), width=20, anchor="w").pack(side="left")
    lbl = tk.Label(row, text=valor, bg=PANEL, fg=color,
                    font=("Segoe UI", 9, "bold"))
    lbl.pack(side="left", padx=4)
    return lbl
