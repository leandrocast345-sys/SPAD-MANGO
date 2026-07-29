"""
historial_window.py
====================
Ventana (Toplevel) que muestra el historial de sesiones guardadas en el
Excel: cada sesión muestra fecha + promedio, y se puede desplegar para ver
sus 5 mediciones. Incluye opciones para eliminar una sesión puntual o
borrar todo el historial.

Se separa de spad_app.py porque es una pieza de UI independiente y
reutilizable: solo necesita una instancia de ExcelDB y una ventana padre.
"""

import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox

from config import BG, PANEL, ACCENT, BTN_BG, BTN_HOVER, TEXT_DIM, RED
from ui_widgets import crear_boton


def mostrar_historial(parent_window, db):
    """
    Abre la ventana de historial de mediciones.

    Parámetros
    ----------
    parent_window : tk.Tk o tk.Toplevel
        Ventana principal de la aplicación (dueña del Toplevel).
    db : ExcelDB
        Instancia de la base de datos Excel de la que se lee/borra el historial.
    """
    win = tk.Toplevel(parent_window)
    win.title("Historial de Mediciones — Excel")
    win.configure(bg=BG)
    win.geometry("700x480")

    tk.Label(win, text="◈ HISTORIAL DE SESIONES", bg=BG, fg=ACCENT,
             font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(14, 2))
    tk.Label(win, text=f"Archivo: {os.path.basename(db.path)}", bg=BG, fg=TEXT_DIM,
             font=("Segoe UI", 8)).pack(anchor="w", padx=14, pady=(0, 8))

    style = ttk.Style(win)  # Estiliza el Treeview para que combine con la paleta oscura del resto de la app.
    style.theme_use("clam")
    style.configure("Treeview", background=PANEL, fieldbackground=PANEL,
                    foreground="white", rowheight=24, font=("Courier New", 9), borderwidth=0)
    style.configure("Treeview.Heading", background=BTN_BG, foreground=ACCENT,
                    font=("Segoe UI", 9, "bold"))
    style.map("Treeview", background=[("selected", BTN_HOVER)])

    tree_frame = tk.Frame(win, bg=BG)
    tree_frame.pack(fill="both", expand=True, padx=14)

    cols = ("verde", "amarillo", "spad")
    tree = ttk.Treeview(tree_frame, columns=cols, show="tree headings")
    tree.heading("#0", text="Sesión / Zona")
    tree.heading("verde", text="Verde %")
    tree.heading("amarillo", text="Amarillo %")
    tree.heading("spad", text="SPAD")
    tree.column("#0", width=280)
    tree.column("verde", width=90, anchor="center")
    tree.column("amarillo", width=90, anchor="center")
    tree.column("spad", width=130, anchor="center")
    tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscroll=scrollbar.set)

    lbl_estado = tk.Label(win, text="Cargando historial…", bg=BG, fg=TEXT_DIM, font=("Segoe UI", 8))
    lbl_estado.pack(anchor="w", padx=14, pady=(4, 0))

    sesion_por_iid = {}   # iid del árbol -> ID de sesión en el Excel (solo filas raíz = sesiones)

    def poblar(historial):
        """Vuelca la lista de sesiones en el Treeview (se ejecuta en el hilo de la UI)."""
        tree.delete(*tree.get_children())
        sesion_por_iid.clear()
        if not historial:
            lbl_estado.config(text="Todavía no hay sesiones guardadas.")
            return
        for item in historial:
            sid, fecha, avg_spad, avg_pv, avg_pa, std_spad, diag = item["resumen"]
            iid = tree.insert("", "end", text=f"{fecha}  —  {diag}",
                               values=(f"{avg_pv:.1f}%", f"{avg_pa:.1f}%",
                                       f"{avg_spad:.1f} (± {std_spad:.2f})"))
            sesion_por_iid[iid] = sid
            for zona, pv, pa, spad in item["mediciones"]:
                tree.insert(iid, "end", text=f"   Zona {zona}",
                            values=(f"{pv:.1f}%", f"{pa:.1f}%", f"{spad:.1f}"))
        lbl_estado.config(text=f"{len(historial)} sesión(es) guardada(s)")

    def cargar():
        """Lee el Excel en un hilo aparte (por si el archivo ya es grande) y actualiza la UI cuando termina."""
        historial = db.obtener_historial()
        parent_window.after(0, lambda: poblar(historial))

    threading.Thread(target=cargar, daemon=True).start()

    # Botones para eliminar datos
    btns = tk.Frame(win, bg=BG)
    btns.pack(fill="x", padx=14, pady=12)

    def eliminar_seleccion():
        """Elimina del Excel las sesiones seleccionadas en el árbol (ignora si lo seleccionado es una zona individual, no una sesión)."""
        raiz_sel = [iid for iid in tree.selection() if iid in sesion_por_iid]
        if not raiz_sel:
            messagebox.showinfo("Eliminar", "Selecciona una sesión (no una zona individual).", parent=win)
            return
        if not messagebox.askyesno("Eliminar sesión",
                                    f"¿Eliminar {len(raiz_sel)} sesión(es) del Excel? Esta acción no se puede deshacer.",
                                    parent=win):
            return
        for iid in raiz_sel:
            db.eliminar_sesion(sesion_por_iid[iid])
            tree.delete(iid)
            del sesion_por_iid[iid]
        lbl_estado.config(text="Sesión(es) eliminada(s).")

    def borrar_todo():
        """Borra por completo el historial guardado en el Excel (reinicia el archivo)."""
        if not messagebox.askyesno("Borrar historial completo",
                                    "Esto eliminará TODAS las sesiones guardadas en el Excel. ¿Continuar?",
                                    parent=win):
            return
        db.eliminar_todo()
        tree.delete(*tree.get_children())
        sesion_por_iid.clear()
        lbl_estado.config(text="Historial borrado.")

    crear_boton(btns, " Eliminar sesión seleccionada", eliminar_seleccion, RED).pack(side="left", padx=(0, 8))
    crear_boton(btns, " Borrar todo el historial", borrar_todo, RED).pack(side="left")
