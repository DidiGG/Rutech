"""
CRUD para Proveedores
"""

from tkinter import messagebox
from .base import CRUDBase, styled_entry, styled_label, styled_combo
from database.conecction import get_conn


class CRUDProveedor(CRUDBase):
    TITLE       = "GESTIÓN DE PROVEEDORES"
    TABLE       = "PROVEEDOR"
    PK          = "id_proveedor"
    COLUMNS     = ("ID","NIT","Nombre","Tipo","Teléfono","Ciudad","Estado")
    COL_WIDTHS  = {"ID":50,"NIT":120,"Nombre":170,"Tipo":140,
                   "Teléfono":110,"Ciudad":110,"Estado":90}
    FIELD_NAMES = ("nit","nombre","tipo","telefono","ciudad","estado")

    def build_form(self, p):
        fields = [
            ("NIT*", "nit"),
            ("Nombre*", "nombre"),
            ("Teléfono", "telefono"),
            ("Ciudad", "ciudad"),
        ]
        self.vars = {}
        for i, (lbl, key) in enumerate(fields):
            styled_label(p, lbl).grid(row=i, column=0, sticky="w", pady=3)
            e = styled_entry(p, width=28)
            e.grid(row=i, column=1, pady=3, padx=(6,0))
            self.vars[key] = e

        styled_label(p, "Tipo*").grid(row=len(fields), column=0, sticky="w", pady=3)
        self.tipo_cb = styled_combo(p, ["taller","gasolinera","distribuidor_repuestos","otro"], width=26)
        self.tipo_cb.grid(row=len(fields), column=1, pady=3, padx=(6,0))
        self.tipo_cb.set("taller")

        styled_label(p, "Estado*").grid(row=len(fields)+1, column=0, sticky="w", pady=3)
        self.est_cb = styled_combo(p, ["activo","inactivo"], width=26)
        self.est_cb.grid(row=len(fields)+1, column=1, pady=3, padx=(6,0))
        self.est_cb.set("activo")

    def get_form_values(self):
        nit = self.vars["nit"].get().strip()
        nombre = self.vars["nombre"].get().strip()
        if not nit:
            messagebox.showwarning("Campo requerido", "NIT es obligatorio.")
            return None
        if not nombre:
            messagebox.showwarning("Campo requerido", "Nombre es obligatorio.")
            return None
        return (nit, nombre, self.tipo_cb.get(),
                self.vars["telefono"].get().strip(),
                self.vars["ciudad"].get().strip(),
                self.est_cb.get())

    def set_form_values(self, row):
        self.vars["nit"].delete(0, "end")
        self.vars["nit"].insert(0, row[1])
        self.vars["nombre"].delete(0, "end")
        self.vars["nombre"].insert(0, row[2])
        self.tipo_cb.set(row[3])
        self.vars["telefono"].delete(0, "end")
        self.vars["telefono"].insert(0, row[4])
        self.vars["ciudad"].delete(0, "end")
        self.vars["ciudad"].insert(0, row[5])
        self.est_cb.set(row[6])

    def clear_form(self):
        for e in self.vars.values():
            e.delete(0, "end")
        self.tipo_cb.set("taller")
        self.est_cb.set("activo")

    def db_read(self, kw=""):
        conn = get_conn()
        c = conn.cursor()
        q = ("SELECT id_proveedor, nit, nombre, tipo, telefono, ciudad, estado "
             "FROM PROVEEDOR")
        if kw:
            c.execute(q + " WHERE nit LIKE %s OR nombre LIKE %s OR ciudad LIKE %s OR tipo LIKE %s",
                      (f"%{kw}%",)*4)
        else:
            c.execute(q)
        rows = c.fetchall()
        conn.close()
        return rows
