"""
CRUD para Conductores
"""

from tkinter import messagebox
from .base import CRUDBase, styled_entry, styled_label, styled_combo
from database.conecction import get_conn


class CRUDConductor(CRUDBase):
    TITLE       = "GESTIÓN DE CONDUCTORES"
    TABLE       = "CONDUCTOR"
    PK          = "id_conductor"
    COLUMNS     = ("ID","Cédula","Nombre","Apellido","Teléfono",
                   "Licencia","Cat.","Vence","Estado")
    COL_WIDTHS  = {"ID":50,"Cédula":90,"Nombre":110,"Apellido":110,
                   "Teléfono":110,"Licencia":90,"Cat.":60,"Vence":100,"Estado":90}
    FIELD_NAMES = ("cedula","nombre","apellido","telefono",
                   "num_licencia","categoria_licencia",
                   "fecha_venc_licencia","estado")

    def build_form(self, p):
        fields = [
            ("Cédula*",       "cedula"),
            ("Nombre*",       "nombre"),
            ("Apellido*",     "apellido"),
            ("Teléfono",      "telefono"),
            ("Nº Licencia*",  "num_licencia"),
        ]
        self.vars = {}
        for i, (lbl, key) in enumerate(fields):
            styled_label(p, lbl).grid(row=i, column=0, sticky="w", pady=3)
            e = styled_entry(p, width=28)
            e.grid(row=i, column=1, pady=3, padx=(6,0))
            self.vars[key] = e

        r = len(fields)
        styled_label(p, "Categoría*").grid(row=r, column=0, sticky="w", pady=3)
        self.cat_cb = styled_combo(p, ["A2","B1","B2","C1","C2","C3"], width=26)
        self.cat_cb.grid(row=r, column=1, pady=3, padx=(6,0))
        self.cat_cb.set("C2")

        styled_label(p, "Venc. Licencia*").grid(row=r+1, column=0, sticky="w", pady=3)
        self.venc_e = styled_entry(p, width=28)
        self.venc_e.insert(0,"YYYY-MM-DD")
        self.venc_e.grid(row=r+1, column=1, pady=3, padx=(6,0))

        styled_label(p, "Estado*").grid(row=r+2, column=0, sticky="w", pady=3)
        self.est_cb = styled_combo(p, ["activo","inactivo","suspendido"], width=26)
        self.est_cb.grid(row=r+2, column=1, pady=3, padx=(6,0))
        self.est_cb.set("activo")

    def get_form_values(self):
        keys = ["cedula","nombre","apellido","telefono","num_licencia"]
        vals = [self.vars[k].get().strip() for k in keys]
        for i, (k, v) in enumerate(zip(["Cédula","Nombre","Apellido",
                                         "Teléfono","Nº Licencia"], vals)):
            if k != "Teléfono" and not v:
                messagebox.showwarning("Campo requerido", f"{k} es obligatorio.")
                return None
        return (*vals, self.cat_cb.get(),
                self.venc_e.get().strip(), self.est_cb.get())

    def set_form_values(self, row):
        keys = ["cedula","nombre","apellido","telefono","num_licencia"]
        vals = list(row)[1:6]
        for k, v in zip(keys, vals):
            self.vars[k].delete(0,"end")
            self.vars[k].insert(0, v)
        self.cat_cb.set(row[6])
        self.venc_e.delete(0,"end")
        self.venc_e.insert(0, row[7])
        self.est_cb.set(row[8])

    def clear_form(self):
        for e in self.vars.values():
            e.delete(0,"end")
        self.cat_cb.set("C2")
        self.venc_e.delete(0,"end")
        self.venc_e.insert(0,"YYYY-MM-DD")
        self.est_cb.set("activo")

    def db_read(self, kw=""):
        conn = get_conn()
        c = conn.cursor()
        q = """SELECT id_conductor, cedula, nombre, apellido, telefono,
                      num_licencia, categoria_licencia,
                      fecha_venc_licencia, estado
               FROM CONDUCTOR"""
        if kw:
            c.execute(q + " WHERE nombre LIKE %s OR apellido LIKE %s"
                        + " OR cedula LIKE %s OR num_licencia LIKE %s",
                      (f"%{kw}%",)*4)
        else:
            c.execute(q)
        rows = c.fetchall()
        conn.close()
        return rows