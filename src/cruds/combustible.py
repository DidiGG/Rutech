"""
CRUD para Combustible
"""

from tkinter import messagebox
from .base import CRUDBase, styled_entry, styled_label, styled_combo
from database.conecction import get_conn


class CRUDCombustible(CRUDBase):
    TITLE       = "GESTIÓN DE COMBUSTIBLE"
    TABLE       = "COMBUSTIBLE"
    PK          = "id_combustible"
    COLUMNS     = ("ID","Vehículo","Proveedor","Fecha","Litros","Precio/L","Km recarga","Km desde última","Tipo combustible","Creado por")
    COL_WIDTHS  = {"ID":50, "Vehículo":150, "Proveedor":140, "Fecha":110,
                   "Litros":90, "Precio/L":100, "Km recarga":110,
                   "Km desde última":130, "Tipo combustible":140, "Creado por":140}
    FIELD_NAMES = ("id_vehiculo","id_proveedor","fecha","litros",
                   "precio_por_litro","km_al_recargar","km_desde_ultima_recarga",
                   "tipo_combustible","creado_por")

    def build_form(self, p):
        styled_label(p, "Vehículo*").grid(row=0, column=0, sticky="w", pady=3)
        self.vehiculo_cb = styled_combo(p, self._load_vehiculo_options(), width=28)
        self.vehiculo_cb.grid(row=0, column=1, pady=3, padx=(6,0))
        if self.vehiculo_cb['values']:
            self.vehiculo_cb.set(self.vehiculo_cb['values'][0])

        styled_label(p, "Proveedor*").grid(row=1, column=0, sticky="w", pady=3)
        self.proveedor_cb = styled_combo(p, self._load_proveedor_options(), width=28)
        self.proveedor_cb.grid(row=1, column=1, pady=3, padx=(6,0))
        if self.proveedor_cb['values']:
            self.proveedor_cb.set(self.proveedor_cb['values'][0])

        styled_label(p, "Fecha*").grid(row=2, column=0, sticky="w", pady=3)
        self.fecha_entry = styled_entry(p, width=28)
        self.fecha_entry.grid(row=2, column=1, pady=3, padx=(6,0))
        self.fecha_entry.insert(0, "2026-01-01")

        styled_label(p, "Litros*").grid(row=3, column=0, sticky="w", pady=3)
        self.litros_entry = styled_entry(p, width=28)
        self.litros_entry.grid(row=3, column=1, pady=3, padx=(6,0))

        styled_label(p, "Precio por litro*").grid(row=4, column=0, sticky="w", pady=3)
        self.precio_entry = styled_entry(p, width=28)
        self.precio_entry.grid(row=4, column=1, pady=3, padx=(6,0))

        styled_label(p, "Km al recargar*").grid(row=5, column=0, sticky="w", pady=3)
        self.km_recarga_entry = styled_entry(p, width=28)
        self.km_recarga_entry.grid(row=5, column=1, pady=3, padx=(6,0))

        styled_label(p, "Km desde última recarga").grid(row=6, column=0, sticky="w", pady=3)
        self.km_desde_entry = styled_entry(p, width=28)
        self.km_desde_entry.grid(row=6, column=1, pady=3, padx=(6,0))

        styled_label(p, "Tipo combustible*").grid(row=7, column=0, sticky="w", pady=3)
        self.tipo_cb = styled_combo(p, ["diesel", "gasolina_corriente", "gasolina_extra", "gas"], width=28)
        self.tipo_cb.grid(row=7, column=1, pady=3, padx=(6,0))
        self.tipo_cb.set("diesel")

        styled_label(p, "Creado por").grid(row=8, column=0, sticky="w", pady=3)
        self.usuario_cb = styled_combo(p, self._load_usuario_options(), width=28)
        self.usuario_cb.grid(row=8, column=1, pady=3, padx=(6,0))
        self.usuario_cb.set("Ninguno")

    def _load_vehiculo_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_vehiculo, placa, marca FROM VEHICULO")
        rows = c.fetchall()
        conn.close()
        self.vehiculo_map = {f"{r[0]} - {r[1]} {r[2]}": r[0] for r in rows}
        return list(self.vehiculo_map.keys())

    def _load_proveedor_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_proveedor, nombre FROM PROVEEDOR")
        rows = c.fetchall()
        conn.close()
        self.proveedor_map = {f"{r[0]} - {r[1]}": r[0] for r in rows}
        return list(self.proveedor_map.keys())

    def _load_usuario_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_usuario, nombre_usuario FROM USUARIO")
        rows = c.fetchall()
        conn.close()
        self.usuario_map = {"Ninguno": None}
        self.usuario_map.update({f"{r[0]} - {r[1]}": r[0] for r in rows})
        return list(self.usuario_map.keys())

    def _selected_vehiculo_id(self):
        return self.vehiculo_map.get(self.vehiculo_cb.get())

    def _selected_proveedor_id(self):
        return self.proveedor_map.get(self.proveedor_cb.get())

    def _selected_usuario_id(self):
        return self.usuario_map.get(self.usuario_cb.get())

    def get_form_values(self):
        vehiculo_id = self._selected_vehiculo_id()
        if vehiculo_id is None:
            messagebox.showwarning("Campo requerido", "Selecciona un vehículo válido.")
            return None

        proveedor_id = self._selected_proveedor_id()
        if proveedor_id is None:
            messagebox.showwarning("Campo requerido", "Selecciona un proveedor válido.")
            return None

        fecha = self.fecha_entry.get().strip()
        if not fecha:
            messagebox.showwarning("Campo requerido", "Fecha es obligatoria.")
            return None
        try:
            year, month, day = fecha.split("-")
            int(year); int(month); int(day)
        except Exception:
            messagebox.showwarning("Formato inválido", "Fecha debe tener formato YYYY-MM-DD.")
            return None

        litros = self.litros_entry.get().strip()
        if not litros:
            messagebox.showwarning("Campo requerido", "Litros es obligatorio.")
            return None
        try:
            litros_val = float(litros)
            if litros_val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Valor inválido", "Litros debe ser un número mayor a 0.")
            return None

        precio = self.precio_entry.get().strip()
        if not precio:
            messagebox.showwarning("Campo requerido", "Precio por litro es obligatorio.")
            return None
        try:
            precio_val = float(precio)
            if precio_val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Valor inválido", "Precio por litro debe ser un número mayor a 0.")
            return None

        km_recarga = self.km_recarga_entry.get().strip()
        if not km_recarga:
            messagebox.showwarning("Campo requerido", "Km al recargar es obligatorio.")
            return None
        try:
            km_recarga_val = float(km_recarga)
            if km_recarga_val < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Valor inválido", "Km al recargar debe ser un número mayor o igual a 0.")
            return None

        km_desde = self.km_desde_entry.get().strip()
        km_desde_val = None
        if km_desde:
            try:
                km_desde_val = float(km_desde)
                if km_desde_val < 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Valor inválido", "Km desde última recarga debe ser un número mayor o igual a 0.")
                return None

        tipo = self.tipo_cb.get()
        if tipo not in ("diesel", "gasolina_corriente", "gasolina_extra", "gas"):
            messagebox.showwarning("Campo requerido", "Selecciona un tipo de combustible válido.")
            return None

        return (vehiculo_id, proveedor_id, fecha, litros_val, precio_val,
                km_recarga_val, km_desde_val, tipo, self._selected_usuario_id())

    def set_form_values(self, row):
        vehiculo_key = next((k for k, v in self.vehiculo_map.items() if v == row[1]), None)
        if vehiculo_key:
            self.vehiculo_cb.set(vehiculo_key)
        proveedor_key = next((k for k, v in self.proveedor_map.items() if v == row[2]), None)
        if proveedor_key:
            self.proveedor_cb.set(proveedor_key)
        self.fecha_entry.delete(0, "end")
        self.fecha_entry.insert(0, row[3])
        self.litros_entry.delete(0, "end")
        self.litros_entry.insert(0, row[4])
        self.precio_entry.delete(0, "end")
        self.precio_entry.insert(0, row[5])
        self.km_recarga_entry.delete(0, "end")
        self.km_recarga_entry.insert(0, row[6])
        self.km_desde_entry.delete(0, "end")
        self.km_desde_entry.insert(0, row[7] or "")
        self.tipo_cb.set(row[8])
        self.usuario_cb.set(next((k for k, v in self.usuario_map.items() if v == row[9]), "Ninguno"))

    def clear_form(self):
        if self.vehiculo_cb['values']:
            self.vehiculo_cb.set(self.vehiculo_cb['values'][0])
        if self.proveedor_cb['values']:
            self.proveedor_cb.set(self.proveedor_cb['values'][0])
        self.fecha_entry.delete(0, "end")
        self.fecha_entry.insert(0, "2026-01-01")
        self.litros_entry.delete(0, "end")
        self.precio_entry.delete(0, "end")
        self.km_recarga_entry.delete(0, "end")
        self.km_desde_entry.delete(0, "end")
        self.tipo_cb.set("diesel")
        self.usuario_cb.set("Ninguno")

    def _label_from_map(self, mapping, value):
        for key, val in mapping.items():
            if val == value:
                return key
        return value

    def db_read(self, kw=""):
        conn = get_conn()
        c = conn.cursor()
        q = ("SELECT c.id_combustible, c.id_vehiculo, c.id_proveedor, c.fecha, c.litros, "
             "c.precio_por_litro, c.km_al_recargar, c.km_desde_ultima_recarga, c.tipo_combustible, c.creado_por "
             "FROM COMBUSTIBLE c")
        if kw:
            c.execute(q + " WHERE c.tipo_combustible LIKE %s OR c.fecha LIKE %s ",
                      (f"%{kw}%", f"%{kw}%"))
        else:
            c.execute(q)
        rows = []
        for r in c.fetchall():
            rows.append((
                r[0],
                self._label_from_map(self.vehiculo_map, r[1]),
                self._label_from_map(self.proveedor_map, r[2]),
                r[3],
                r[4],
                r[5],
                r[6],
                r[7] or "",
                r[8],
                self._label_from_map(self.usuario_map, r[9]),
            ))
        conn.close()
        return rows
