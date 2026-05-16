"""
CRUD para Tarifas
"""

from tkinter import messagebox
from .base import CRUDBase, styled_entry, styled_label, styled_combo
from database.conecction import get_conn


class CRUDTarifa(CRUDBase):
    TITLE       = "GESTIÓN DE TARIFAS"
    TABLE       = "TARIFA"
    PK          = "id_tarifa"
    COLUMNS     = ("ID","Ruta","Nombre","Tipo cálculo","Base","Por km","Por kg","Desde","Hasta","Estado")
    COL_WIDTHS  = {"ID":50,"Ruta":150,"Nombre":140,"Tipo cálculo":100,
                   "Base":90,"Por km":90,"Por kg":90,"Desde":90,"Hasta":90,"Estado":90}
    FIELD_NAMES = ("id_ruta","nombre","tipo_calculo","valor_base",
                   "valor_por_km","valor_por_kg","vigente_desde",
                   "vigente_hasta","estado")

    def build_form(self, p):
        styled_label(p, "Ruta*").grid(row=0, column=0, sticky="w", pady=3)
        self.ruta_cb = styled_combo(p, self._load_route_options(), width=26)
        self.ruta_cb.grid(row=0, column=1, pady=3, padx=(6,0))
        if self.ruta_cb['values']:
            self.ruta_cb.set(self.ruta_cb['values'][0])

        fields = [
            ("Nombre*", "nombre"),
            ("Tipo cálculo*", "tipo"),
            ("Valor base", "valor_base"),
            ("Valor por km", "valor_por_km"),
            ("Valor por kg", "valor_por_kg"),
            ("Desde*", "desde"),
            ("Hasta*", "hasta"),
        ]
        self.vars = {}
        for i, (lbl, key) in enumerate(fields, start=1):
            styled_label(p, lbl).grid(row=i, column=0, sticky="w", pady=3)
            if key == "tipo":
                self.tipo_cb = styled_combo(p, ["fijo","por_km","por_kg","mixto"], width=26)
                self.tipo_cb.grid(row=i, column=1, pady=3, padx=(6,0))
                self.tipo_cb.set("fijo")
            else:
                e = styled_entry(p, width=28)
                e.grid(row=i, column=1, pady=3, padx=(6,0))
                self.vars[key] = e

        styled_label(p, "Estado*").grid(row=len(fields)+1, column=0, sticky="w", pady=3)
        self.est_cb = styled_combo(p, ["activa","inactiva"], width=26)
        self.est_cb.grid(row=len(fields)+1, column=1, pady=3, padx=(6,0))
        self.est_cb.set("activa")

    def _load_route_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_ruta, nombre FROM RUTA")
        rows = c.fetchall()
        conn.close()
        self.route_map = {f"{r[0]} - {r[1]}": r[0] for r in rows}
        return list(self.route_map.keys())

    def _selected_route_id(self):
        return self.route_map.get(self.ruta_cb.get())

    def get_form_values(self):
        nombre = self.vars["nombre"].get().strip()
        if not nombre:
            messagebox.showwarning("Campo requerido", "Nombre es obligatorio.")
            return None
        ruta_id = self._selected_route_id()
        if ruta_id is None:
            messagebox.showwarning("Campo requerido", "Selecciona una ruta válida.")
            return None
        try:
            valor_base = float(self.vars["valor_base"].get().strip() or 0)
            valor_por_km = float(self.vars["valor_por_km"].get().strip() or 0)
            valor_por_kg = float(self.vars["valor_por_kg"].get().strip() or 0)
        except ValueError:
            messagebox.showwarning("Formato", "Los valores de tarifa deben ser numéricos.")
            return None
        desde = self.vars["desde"].get().strip()
        hasta = self.vars["hasta"].get().strip()
        if not desde or not hasta:
            messagebox.showwarning("Campo requerido", "Las fechas desde/hasta son obligatorias.")
            return None
        if hasta < desde:
            messagebox.showwarning("Validación", "La fecha 'hasta' debe ser igual o posterior a 'desde'.")
            return None
        return (ruta_id, nombre, self.tipo_cb.get(), valor_base,
                valor_por_km, valor_por_kg, desde, hasta, self.est_cb.get())

    def set_form_values(self, row):
        route_name = row[1]
        route_key = next((key for key in self.route_map if key.endswith(f" - {route_name}")), None)
        if route_key:
            self.ruta_cb.set(route_key)
        self.vars["nombre"].delete(0, "end")
        self.vars["nombre"].insert(0, row[2])
        self.tipo_cb.set(row[3])
        self.vars["valor_base"].delete(0, "end")
        self.vars["valor_base"].insert(0, row[4])
        self.vars["valor_por_km"].delete(0, "end")
        self.vars["valor_por_km"].insert(0, row[5])
        self.vars["valor_por_kg"].delete(0, "end")
        self.vars["valor_por_kg"].insert(0, row[6])
        self.vars["desde"].delete(0, "end")
        self.vars["desde"].insert(0, row[7])
        self.vars["hasta"].delete(0, "end")
        self.vars["hasta"].insert(0, row[8])
        self.est_cb.set(row[9])

    def clear_form(self):
        self.ruta_cb.set(self.ruta_cb['values'][0] if self.ruta_cb['values'] else "")
        for key in ["nombre","valor_base","valor_por_km","valor_por_kg","desde","hasta"]:
            self.vars[key].delete(0, "end")
        self.tipo_cb.set("fijo")
        self.est_cb.set("activa")

    def db_read(self, kw=""):
        conn = get_conn()
        c = conn.cursor()
        q = ("SELECT t.id_tarifa, r.nombre, t.nombre, t.tipo_calculo, "
             "t.valor_base, t.valor_por_km, t.valor_por_kg, t.vigente_desde, "
             "t.vigente_hasta, t.estado "
             "FROM TARIFA t JOIN RUTA r ON t.id_ruta = r.id_ruta")
        if kw:
            c.execute(q + " WHERE r.nombre LIKE %s OR t.nombre LIKE %s OR t.tipo_calculo LIKE %s",
                      (f"%{kw}%",)*3)
        else:
            c.execute(q)
        rows = c.fetchall()
        conn.close()
        return rows
