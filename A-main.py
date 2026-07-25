"""
main.py
Punto de entrada de SPAD Pro — Analizador de Clorofila.
Ejecutar con: python main.py
"""

import tkinter as tk                 # Tkinter: librería para construir la interfaz gráfica

from app import SPADApp


def main():
    root = tk.Tk()  ## Crea la ventana principal de la aplicación utilizando Tkinter.
    app = SPADApp(root)  ## Inicializa la aplicación SPADApp, pasando la ventana principal como argumento para configurar la interfaz gráfica y la lógica de captura y análisis de imágenes.
    root.protocol("WM_DELETE_WINDOW", app.on_closing)  ## Configura el protocolo de cierre de la ventana, asignando on_closing para detener la captura de video de manera ordenada.
    root.mainloop()  ## Inicia el bucle principal de la interfaz gráfica, permitiendo que la aplicación responda a eventos hasta que se cierre.


if __name__ == "__main__":
    main()
