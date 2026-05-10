"""
CRUD para Vehículos
"""

from tkinter import messagebox
from .base import CRUDBase, styled_entry, styled_label, styled_combo
from database.conecction import get_conn


class CRUDVehiculo(CRUDBase):
    TITLE       = "GESTIÓN DE VEHÍCULOS"
    TABLE       = "VEHICULO"
    PK          = "id_vehiculo"
    COLUMNS     = ("ID","Placa","Marca","Modelo","Año","Tipo","Km","Estado")
    COL_WIDTHS  = {"ID":50,"Placa":90,"Marca":100,"Modelo":100,
                   "Año":60,"Tipo":90,"Km":100,"Estado":110}
    FIELD_NAMES = ("placa","marca","modelo","anio","tipo",
                   "kilometraje_actual","estado")

    def build_form(self, p):
        fields = [("Placa*","placa"),("Marca*","marca"),
                  ("Modelo*","modelo"),("Año*","anio"),("Kilometraje*","km")]
        self.vars = {}
        for i, (lbl, key) in enumerate(fields):
            styled_label(p, lbl).grid(row=i, column=0, sticky="w", pady=3)
            e = styled_entry(p, width=28)
            e.grid(row=i, column=1, pady=3, padx=(6,0))
            self.vars[key] = e

        r = len(fields)
        styled_label(p, "Tipo*").grid(row=r, column=0, sticky="w", pady=3)
        self.tipo_cb = styled_combo(p, ["camion","furgon","van"], width=26)
        self.tipo_cb.grid(row=r, column=1, pady=3, padx=(6,0))
        self.tipo_cb.set("camion")

        styled_label(p, "Estado*").grid(row=r+1, column=0, sticky="w", pady=3)
        self.est_cb = styled_combo(
            p, ["disponible","en_viaje","en_mantenimiento","inactivo"], width=26)
        self.est_cb.grid(row=r+1, column=1, pady=3, padx=(6,0))
        self.est_cb.set("disponible")

    def get_form_values(self):
        placa  = self.vars["placa"].get().strip()
        marca  = self.vars["marca"].get().strip()
        modelo = self.vars["modelo"].get().strip()
        anio   = self.vars["anio"].get().strip()
        km     = self.vars["km"].get().strip()
        for lbl, v in [("Placa",placa),("Marca",marca),
                       ("Modelo",modelo),("Año",anio),("Km",km)]:
            if not v:
                messagebox.showwarning("Campo requerido", f"{lbl} es obligatorio.")
                return None
        return (placa, marca, modelo, anio, self.tipo_cb.get(),
                km, self.est_cb.get())

    def set_form_values(self, row):
        for key, val in zip(["placa","marca","modelo","anio"], row[1:5]):
            self.vars[key].delete(0,"end")
            self.vars[key].insert(0, val)
        self.tipo_cb.set(row[5])
        self.vars["km"].delete(0,"end")
        self.vars["km"].insert(0, row[6])
        self.est_cb.set(row[7])

    def clear_form(self):
        for e in self.vars.values():
            e.delete(0,"end")
        self.tipo_cb.set("camion")
        self.est_cb.set("disponible")

    def db_read(self, kw=""):
        conn = get_conn()
        c = conn.cursor()
        q = ("SELECT id_vehiculo, placa, marca, modelo, anio, "
             "tipo, kilometraje_actual, estado FROM VEHICULO")
        if kw:
            c.execute(q + " WHERE placa LIKE %s OR marca LIKE %s OR modelo LIKE %s",
                      (f"%{kw}%",)*3)
        else:
            c.execute(q)
        rows = c.fetchall()
        conn.close()
        return rows