"""
CRUD para Clientes
"""

from tkinter import messagebox
from .base import CRUDBase, styled_entry, styled_label, styled_combo
from database.conecction import get_conn


class CRUDCliente(CRUDBase):
    TITLE       = "GESTIÓN DE CLIENTES"
    TABLE       = "CLIENTE"
    PK          = "id_cliente"
    COLUMNS     = ("ID","Tipo","Documento","Nombre/Razón Social",
                   "Correo","Teléfono","Ciudad","Estado")
    COL_WIDTHS  = {"ID":45,"Tipo":80,"Documento":100,
                   "Nombre/Razón Social":180,"Correo":150,
                   "Teléfono":100,"Ciudad":90,"Estado":80}
    FIELD_NAMES = ("tipo_persona","documento","nombre_razon_social",
                   "correo","telefono","ciudad","estado")

    def build_form(self, p):
        styled_label(p, "Tipo Persona*").grid(row=0, column=0, sticky="w", pady=3)
        self.tipo_cb = styled_combo(p, ["natural","juridica"], width=26)
        self.tipo_cb.grid(row=0, column=1, pady=3, padx=(6,0))
        self.tipo_cb.set("natural")

        text_fields = [
            ("Documento*",       "documento"),
            ("Nombre/Razón Soc*","nombre"),
            ("Correo",           "correo"),
            ("Teléfono",         "telefono"),
            ("Ciudad",           "ciudad"),
        ]
        self.vars = {}
        for i, (lbl, key) in enumerate(text_fields, start=1):
            styled_label(p, lbl).grid(row=i, column=0, sticky="w", pady=3)
            e = styled_entry(p, width=28)
            e.grid(row=i, column=1, pady=3, padx=(6,0))
            self.vars[key] = e

        r = len(text_fields) + 1
        styled_label(p, "Estado*").grid(row=r, column=0, sticky="w", pady=3)
        self.est_cb = styled_combo(p, ["activo","inactivo"], width=26)
        self.est_cb.grid(row=r, column=1, pady=3, padx=(6,0))
        self.est_cb.set("activo")

    def get_form_values(self):
        doc    = self.vars["documento"].get().strip()
        nombre = self.vars["nombre"].get().strip()
        if not doc:
            messagebox.showwarning("Campo requerido", "Documento es obligatorio.")
            return None
        if not nombre:
            messagebox.showwarning("Campo requerido", "Nombre/Razón Social es obligatorio.")
            return None
        return (self.tipo_cb.get(), doc, nombre,
                self.vars["correo"].get().strip(),
                self.vars["telefono"].get().strip(),
                self.vars["ciudad"].get().strip(),
                self.est_cb.get())

    def set_form_values(self, row):
        self.tipo_cb.set(row[1])
        for key, val in zip(["documento","nombre","correo","telefono","ciudad"],
                             row[2:7]):
            self.vars[key].delete(0,"end")
            self.vars[key].insert(0, val or "")
        self.est_cb.set(row[7])

    def clear_form(self):
        self.tipo_cb.set("natural")
        for e in self.vars.values():
            e.delete(0,"end")
        self.est_cb.set("activo")

    def db_read(self, kw=""):
        conn = get_conn()
        c = conn.cursor()
        q = ("SELECT id_cliente, tipo_persona, documento, nombre_razon_social, "
             "correo, telefono, ciudad, estado FROM CLIENTE")
        if kw:
            c.execute(q + " WHERE nombre_razon_social LIKE %s"
                        + " OR documento LIKE %s OR ciudad LIKE %s",
                      (f"%{kw}%",)*3)
        else:
            c.execute(q)
        rows = c.fetchall()
        conn.close()
        return rows