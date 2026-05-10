"""
RUTECH — Sistema de Gestión de Flotas
TransCarga Andina S.A.S. · Universidad del Quindío · Bases de Datos 1 · 2026-1

Módulo base para CRUDs con Tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from database.conecction import get_conn

# ═════════════════════════════════════════════════════════════════════════════
#  UTILIDADES DE UI
# ═════════════════════════════════════════════════════════════════════════════
BG        = "#0f1117"
BG2       = "#1a1d27"
BG3       = "#23263a"
ACCENT    = "#4f8ef7"
ACCENT2   = "#f7714f"
TEXT      = "#e8eaf6"
TEXT_DIM  = "#7986cb"
SUCCESS   = "#43a047"
DANGER    = "#e53935"
FONT_HEAD = ("Courier New", 13, "bold")
FONT_BODY = ("Courier New", 11)
FONT_SM   = ("Courier New", 9)

STYLE_BTN  = dict(bg=ACCENT,  fg="white", font=FONT_BODY, relief="flat",
                  cursor="hand2", padx=14, pady=6, bd=0)
STYLE_BTN2 = dict(bg=ACCENT2, fg="white", font=FONT_BODY, relief="flat",
                  cursor="hand2", padx=14, pady=6, bd=0)
STYLE_BTN3 = dict(bg=DANGER,  fg="white", font=FONT_BODY, relief="flat",
                  cursor="hand2", padx=14, pady=6, bd=0)
STYLE_BTN4 = dict(bg=SUCCESS,  fg="white", font=FONT_BODY, relief="flat",
                  cursor="hand2", padx=14, pady=6, bd=0)

def styled_entry(parent, **kw):
    e = tk.Entry(parent, bg=BG3, fg=TEXT, insertbackground=TEXT,
                 relief="flat", font=FONT_BODY, bd=4, **kw)
    return e

def styled_label(parent, text, **kw):
    return tk.Label(parent, text=text, bg=BG2, fg=TEXT_DIM,
                    font=FONT_SM, **kw)

def styled_combo(parent, values, **kw):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Dark.TCombobox",
                    fieldbackground=BG3, background=BG3,
                    foreground=TEXT, selectbackground=ACCENT,
                    selectforeground="white")
    cb = ttk.Combobox(parent, values=values, style="Dark.TCombobox",
                      font=FONT_BODY, state="readonly", **kw)
    return cb

def make_treeview(parent, columns, heights=14):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Dark.Treeview",
                    background=BG3, foreground=TEXT,
                    rowheight=26, fieldbackground=BG3,
                    font=FONT_BODY)
    style.configure("Dark.Treeview.Heading",
                    background=BG2, foreground=ACCENT,
                    font=("Courier New", 10, "bold"), relief="flat")
    style.map("Dark.Treeview",
              background=[("selected", ACCENT)],
              foreground=[("selected", "white")])

    frame = tk.Frame(parent, bg=BG)
    tv = ttk.Treeview(frame, columns=columns, show="headings",
                      height=heights, style="Dark.Treeview")
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tv.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tv.xview)
    tv.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tv.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    return frame, tv


# ═════════════════════════════════════════════════════════════════════════════
#  CRUD BASE GENÉRICO
# ═════════════════════════════════════════════════════════════════════════════
class CRUDBase(tk.Frame):
    """
    Clase base reutilizable.  Las subclases sólo declaran:
      - TITLE, TABLE, PK, COLUMNS, LABELS, FIELD_NAMES,
        build_form(), get_form_values(), set_form_values()
    """
    TITLE       = "CRUD"
    TABLE       = ""
    PK          = ""
    COLUMNS     = ()   # tupla de nombres para el treeview
    COL_WIDTHS  = {}   # {col: width}
    FIELD_NAMES = ()   # campos DB (sin PK)

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG2, **kw)
        self._build_ui()

    # ── UI principal ────────────────────────────────────────────────────────
    def _build_ui(self):
        # Encabezado
        hdr = tk.Frame(self, bg=ACCENT, pady=8)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"  ▸  {self.TITLE}", bg=ACCENT, fg="white",
                 font=("Courier New", 15, "bold")).pack(side="left")

        body = tk.Frame(self, bg=BG2)
        body.pack(fill="both", expand=True, padx=16, pady=12)

        # Formulario (izquierda)
        form_wrap = tk.LabelFrame(body, text=" Formulario ", bg=BG2,
                                  fg=ACCENT, font=FONT_SM, bd=1,
                                  relief="ridge", padx=12, pady=8)
        form_wrap.grid(row=0, column=0, sticky="nw", padx=(0,16))
        self.build_form(form_wrap)

        # Botones
        btn_row = tk.Frame(body, bg=BG2)
        btn_row.grid(row=1, column=0, sticky="w", pady=(10,0))
        tk.Button(btn_row, text="➕  Insertar", **STYLE_BTN4,
                  command=self._insert).pack(side="left", padx=(0,6))
        tk.Button(btn_row, text="✏️  Actualizar", **STYLE_BTN,
                  command=self._update).pack(side="left", padx=(0,6))
        tk.Button(btn_row, text="🗑  Eliminar", **STYLE_BTN3,
                  command=self._delete).pack(side="left", padx=(0,6))
        tk.Button(btn_row, text="🔄  Limpiar", **STYLE_BTN2,
                  command=self._clear).pack(side="left")

        # Búsqueda
        srch = tk.Frame(body, bg=BG2)
        srch.grid(row=0, column=1, rowspan=2, sticky="nw")
        tk.Label(srch, text="🔍  Buscar:", bg=BG2, fg=TEXT_DIM,
                 font=FONT_SM).pack(anchor="w")
        self.search_var = tk.StringVar()
        se = styled_entry(srch, textvariable=self.search_var, width=28)
        se.pack(fill="x", pady=(0,4))
        se.bind("<KeyRelease>", lambda e: self._load())

        # Tabla
        tbl_frame, self.tv = make_treeview(body, self.COLUMNS)
        tbl_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(12,0))
        body.grid_rowconfigure(2, weight=1)
        body.grid_columnconfigure(1, weight=1)

        for col in self.COLUMNS:
            w = self.COL_WIDTHS.get(col, 110)
            self.tv.heading(col, text=col)
            self.tv.column(col, width=w, anchor="center")

        self.tv.bind("<<TreeviewSelect>>", self._on_select)
        self._load()

    # ── CRUD DB ──────────────────────────────────────────────────────────────
    def _load(self):
        kw = self.search_var.get().strip()
        rows = self.db_read(kw)
        for item in self.tv.get_children():
            self.tv.delete(item)
        for r in rows:
            self.tv.insert("", "end", values=r)

    def _insert(self):
        vals = self.get_form_values()
        if vals is None:
            return
        try:
            conn = get_conn()
            c = conn.cursor()
            ph = ", ".join(["%s"] * len(self.FIELD_NAMES))
            fields = ", ".join(self.FIELD_NAMES)
            c.execute(f"INSERT INTO {self.TABLE} ({fields}) VALUES ({ph})", vals)
            conn.commit()
            conn.close()
            messagebox.showinfo("✅ Éxito", "Registro insertado correctamente.")
            self._clear()
            self._load()
        except Exception as e:
            messagebox.showerror("Error al insertar", str(e))

    def _update(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showwarning("Selección", "Selecciona un registro primero.")
            return
        pk_val = self.tv.item(sel[0])["values"][0]
        vals = self.get_form_values()
        if vals is None:
            return
        try:
            conn = get_conn()
            c = conn.cursor()
            set_clause = ", ".join(f"{f}=%s" for f in self.FIELD_NAMES)
            c.execute(
                f"UPDATE {self.TABLE} SET {set_clause} WHERE {self.PK}=%s",
                (*vals, pk_val)
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("✅ Éxito", "Registro actualizado.")
            self._load()
        except Exception as e:
            messagebox.showerror("Error al actualizar", str(e))

    def _delete(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showwarning("Selección", "Selecciona un registro primero.")
            return
        pk_val = self.tv.item(sel[0])["values"][0]
        if not messagebox.askyesno("Confirmar", f"¿Eliminar registro #{pk_val}?"):
            return
        try:
            conn = get_conn()
            c = conn.cursor()
            c.execute(f"DELETE FROM {self.TABLE} WHERE {self.PK}=%s", (pk_val,))
            conn.commit()
            conn.close()
            messagebox.showinfo("✅ Éxito", "Registro eliminado.")
            self._clear()
            self._load()
        except Exception as e:
            messagebox.showerror("Error al eliminar", str(e))

    def _on_select(self, _event=None):
        sel = self.tv.selection()
        if sel:
            self.set_form_values(self.tv.item(sel[0])["values"])

    def _clear(self):
        self.tv.selection_remove(self.tv.selection())
        self.clear_form()

    # ── Para sobreescribir ────────────────────────────────────────────────────
    def build_form(self, parent):      pass
    def get_form_values(self):         return None
    def set_form_values(self, row):    pass
    def clear_form(self):              pass
    def db_read(self, keyword=""):     return []