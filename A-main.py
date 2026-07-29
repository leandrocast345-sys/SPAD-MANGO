"""
main.py
=======
Punto de entrada de la aplicación SPAD Pro. Ejecutar con:

    python main.py

Crea la ventana principal de Tkinter, inicializa SPADApp y arranca el
bucle principal de eventos.
"""

import tkinter as tk

from spad_app import SPADApp


def main():
    root = tk.Tk()               # Crea la ventana principal de la aplicación utilizando Tkinter.
    app = SPADApp(root)           # Inicializa la aplicación SPADApp, pasando la ventana principal.
    root.protocol("WM_DELETE_WINDOW", app.on_closing)  # Maneja el cierre ordenado de la ventana.
    root.mainloop()               # Inicia el bucle principal de la interfaz gráfica.


if __name__ == "__main__":
    main()
