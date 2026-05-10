"""
CRUD para Rutas
"""

from tkinter import messagebox
from .base import CRUDBase, styled_entry, styled_label, styled_combo
from database.conecction import get_conn


class CRUDRuta(CRUDBase):
    TITLE       = "GESTIÓN DE RUTAS"
    TABLE       = "RUTA"
    PK          = "id_ruta"
    COLUMNS     = ("ID","Nombre","Origen","Destino","Distancia (km)","Estado")
    COL_WIDTHS  = {"ID":50,"Nombre":160,"Origen":120,
                   "Destino":120,"Distancia (km)":120,"Estado":90}
    FIELD_NAMES = ("nombre","origen","destino","distancia_km","estado")

    def build_form(self, p):
        text_fields = [
            ("Nombre*",        "nombre"),
            ("Origen*",        "origen"),
            ("Destino*",       "destino"),
            ("Distancia km*",  "distancia"),
        ]
        self.vars = {}
        for i, (lbl, key) in enumerate(text_fields):
            styled_label(p, lbl).grid(row=i, column=0, sticky="w", pady=3)
            e = styled_entry(p, width=28)
            e.grid(row=i, column=1, pady=3, padx=(6,0))
            self.vars[key] = e

        r = len(text_fields)
        styled_label(p, "Estado*").grid(row=r, column=0, sticky="w", pady=3)
        self.est_cb = styled_combo(p, ["activa","inactiva"], width=26)
        self.est_cb.grid(row=r, column=1, pady=3, padx=(6,0))
        self.est_cb.set("activa")

    def get_form_values(self):
        nombre   = self.vars["nombre"].get().strip()
        origen   = self.vars["origen"].get().strip()
        destino  = self.vars["destino"].get().strip()
        dist     = self.vars["distancia"].get().strip()
        for lbl, v in [("Nombre",nombre),("Origen",origen),
                       ("Destino",destino),("Distancia",dist)]:
            if not v:
                messagebox.showwarning("Campo requerido", f"{lbl} es obligatorio.")
                return None
        try:
            float(dist)
        except ValueError:
            messagebox.showwarning("Formato", "Distancia debe ser un número.")
            return None
        return (nombre, origen, destino, dist, self.est_cb.get())

    def set_form_values(self, row):
        for key, val in zip(["nombre","origen","destino","distancia"], row[1:5]):
            self.vars[key].delete(0,"end")
            self.vars[key].insert(0, val)
        self.est_cb.set(row[5])

    def clear_form(self):
        for e in self.vars.values():
            e.delete(0,"end")
        self.est_cb.set("activa")

    def db_read(self, kw=""):
        conn = get_conn()
        c = conn.cursor()
        q = ("SELECT id_ruta, nombre, origen, destino, "
             "distancia_km, estado FROM RUTA")
        if kw:
            c.execute(q + " WHERE nombre LIKE %s OR origen LIKE %s OR destino LIKE %s",
                      (f"%{kw}%",)*3)
        else:
            c.execute(q)
        rows = c.fetchall()
        conn.close()
        return rows