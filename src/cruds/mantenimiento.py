"""
CRUD para Mantenimientos
"""

from tkinter import messagebox
from .base import CRUDBase, styled_entry, styled_label, styled_combo
from database.conecction import get_conn


class CRUDMantenimiento(CRUDBase):
    TITLE       = "GESTIÓN DE MANTENIMIENTOS"
    TABLE       = "MANTENIMIENTO"
    PK          = "id_mantenimiento"
    COLUMNS     = ("ID","Vehículo","Proveedor","Tipo","Fecha","Km","Descripción","Costo","Estado","Creado por")
    COL_WIDTHS  = {"ID":50, "Vehículo":150, "Proveedor":140, "Tipo":100,
                   "Fecha":110, "Km":90, "Descripción":200, "Costo":110,
                   "Estado":110, "Creado por":140}
    FIELD_NAMES = ("id_vehiculo","id_proveedor","tipo","fecha",
                   "kilometros","descripcion","costo","estado","creado_por")

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

        styled_label(p, "Tipo*").grid(row=2, column=0, sticky="w", pady=3)
        self.tipo_cb = styled_combo(p, ["preventivo", "correctivo"], width=28)
        self.tipo_cb.grid(row=2, column=1, pady=3, padx=(6,0))
        self.tipo_cb.set("preventivo")

        styled_label(p, "Fecha*").grid(row=3, column=0, sticky="w", pady=3)
        self.fecha_entry = styled_entry(p, width=28)
        self.fecha_entry.grid(row=3, column=1, pady=3, padx=(6,0))
        self.fecha_entry.insert(0, "2026-01-01")

        styled_label(p, "Kilómetros*").grid(row=4, column=0, sticky="w", pady=3)
        self.km_entry = styled_entry(p, width=28)
        self.km_entry.grid(row=4, column=1, pady=3, padx=(6,0))

        styled_label(p, "Descripción*").grid(row=5, column=0, sticky="w", pady=3)
        self.descripcion_entry = styled_entry(p, width=28)
        self.descripcion_entry.grid(row=5, column=1, pady=3, padx=(6,0))

        styled_label(p, "Costo*").grid(row=6, column=0, sticky="w", pady=3)
        self.costo_entry = styled_entry(p, width=28)
        self.costo_entry.grid(row=6, column=1, pady=3, padx=(6,0))

        styled_label(p, "Estado*").grid(row=7, column=0, sticky="w", pady=3)
        self.estado_cb = styled_combo(p, ["pendiente", "en_proceso", "completado", "cancelado"], width=28)
        self.estado_cb.grid(row=7, column=1, pady=3, padx=(6,0))
        self.estado_cb.set("pendiente")

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

        tipo = self.tipo_cb.get()
        if tipo not in ("preventivo", "correctivo"):
            messagebox.showwarning("Campo requerido", "Selecciona un tipo válido.")
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

        kilometros = self.km_entry.get().strip()
        if not kilometros:
            messagebox.showwarning("Campo requerido", "Kilómetros es obligatorio.")
            return None
        try:
            km_val = float(kilometros)
            if km_val < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Valor inválido", "Kilómetros debe ser un número mayor o igual a 0.")
            return None

        descripcion = self.descripcion_entry.get().strip()
        if not descripcion:
            messagebox.showwarning("Campo requerido", "Descripción es obligatoria.")
            return None

        costo = self.costo_entry.get().strip()
        if not costo:
            messagebox.showwarning("Campo requerido", "Costo es obligatorio.")
            return None
        try:
            costo_val = float(costo)
            if costo_val < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Valor inválido", "Costo debe ser un número mayor o igual a 0.")
            return None

        estado = self.estado_cb.get()
        if estado not in ("pendiente", "en_proceso", "completado", "cancelado"):
            messagebox.showwarning("Campo requerido", "Selecciona un estado válido.")
            return None

        return (vehiculo_id, proveedor_id, tipo, fecha, km_val,
                descripcion, costo_val, estado, self._selected_usuario_id())

    def set_form_values(self, row):
        vehiculo_key = next((k for k, v in self.vehiculo_map.items() if v == row[1]), None)
        if vehiculo_key:
            self.vehiculo_cb.set(vehiculo_key)
        proveedor_key = next((k for k, v in self.proveedor_map.items() if v == row[2]), None)
        if proveedor_key:
            self.proveedor_cb.set(proveedor_key)
        self.tipo_cb.set(row[3])
        self.fecha_entry.delete(0, "end")
        self.fecha_entry.insert(0, row[4])
        self.km_entry.delete(0, "end")
        self.km_entry.insert(0, row[5])
        self.descripcion_entry.delete(0, "end")
        self.descripcion_entry.insert(0, row[6] or "")
        self.costo_entry.delete(0, "end")
        self.costo_entry.insert(0, row[7])
        self.estado_cb.set(row[8])
        self.usuario_cb.set(next((k for k, v in self.usuario_map.items() if v == row[9]), "Ninguno"))

    def clear_form(self):
        if self.vehiculo_cb['values']:
            self.vehiculo_cb.set(self.vehiculo_cb['values'][0])
        if self.proveedor_cb['values']:
            self.proveedor_cb.set(self.proveedor_cb['values'][0])
        self.tipo_cb.set("preventivo")
        self.fecha_entry.delete(0, "end")
        self.km_entry.delete(0, "end")
        self.descripcion_entry.delete(0, "end")
        self.costo_entry.delete(0, "end")
        self.estado_cb.set("pendiente")
        self.usuario_cb.set("Ninguno")

    def _label_from_map(self, mapping, value):
        for key, val in mapping.items():
            if val == value:
                return key
        return value

    def db_read(self, kw=""):
        conn = get_conn()
        c = conn.cursor()
        q = ("SELECT m.id_mantenimiento, m.id_vehiculo, m.id_proveedor, m.tipo, m.fecha, "
             "m.kilometros, m.descripcion, m.costo, m.estado, m.creado_por "
             "FROM MANTENIMIENTO m")
        if kw:
            c.execute(q + " WHERE m.descripcion LIKE %s OR m.estado LIKE %s ",
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
                r[7],
                r[8],
                self._label_from_map(self.usuario_map, r[9]),
            ))
        conn.close()
        return rows
