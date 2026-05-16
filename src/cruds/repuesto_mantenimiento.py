"""
CRUD para Repuestos de Mantenimiento
"""

from tkinter import messagebox
from .base import CRUDBase, styled_entry, styled_label, styled_combo
from database.conecction import get_conn


class CRUDRepuestoMantenimiento(CRUDBase):
    TITLE       = "GESTIÓN DE REPUESTOS DE MANTENIMIENTO"
    TABLE       = "REPUESTO_MANTENIMIENTO"
    PK          = "id_repuesto"
    COLUMNS     = ("ID","Mantenimiento","Nombre","Referencia","Cantidad","Costo unitario")
    COL_WIDTHS  = {"ID":50, "Mantenimiento":200, "Nombre":170, "Referencia":130,
                   "Cantidad":100, "Costo unitario":120}
    FIELD_NAMES = ("id_mantenimiento","nombre","referencia","cantidad","costo_unitario")

    def build_form(self, p):
        styled_label(p, "Mantenimiento*").grid(row=0, column=0, sticky="w", pady=3)
        self.mantenimiento_cb = styled_combo(p, self._load_mantenimiento_options(), width=28)
        self.mantenimiento_cb.grid(row=0, column=1, pady=3, padx=(6,0))
        if self.mantenimiento_cb['values']:
            self.mantenimiento_cb.set(self.mantenimiento_cb['values'][0])

        styled_label(p, "Nombre*").grid(row=1, column=0, sticky="w", pady=3)
        self.nombre_entry = styled_entry(p, width=28)
        self.nombre_entry.grid(row=1, column=1, pady=3, padx=(6,0))

        styled_label(p, "Referencia").grid(row=2, column=0, sticky="w", pady=3)
        self.referencia_entry = styled_entry(p, width=28)
        self.referencia_entry.grid(row=2, column=1, pady=3, padx=(6,0))

        styled_label(p, "Cantidad*").grid(row=3, column=0, sticky="w", pady=3)
        self.cantidad_entry = styled_entry(p, width=28)
        self.cantidad_entry.grid(row=3, column=1, pady=3, padx=(6,0))

        styled_label(p, "Costo unitario*").grid(row=4, column=0, sticky="w", pady=3)
        self.costo_entry = styled_entry(p, width=28)
        self.costo_entry.grid(row=4, column=1, pady=3, padx=(6,0))

    def _load_mantenimiento_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_mantenimiento, tipo, fecha FROM MANTENIMIENTO")
        rows = c.fetchall()
        conn.close()
        self.mantenimiento_map = {f"{r[0]} - {r[1]} ({r[2]})": r[0] for r in rows}
        return list(self.mantenimiento_map.keys())

    def _selected_mantenimiento_id(self):
        return self.mantenimiento_map.get(self.mantenimiento_cb.get())

    def get_form_values(self):
        mant_id = self._selected_mantenimiento_id()
        if mant_id is None:
            messagebox.showwarning("Campo requerido", "Selecciona un mantenimiento válido.")
            return None

        nombre = self.nombre_entry.get().strip()
        if not nombre:
            messagebox.showwarning("Campo requerido", "Nombre del repuesto es obligatorio.")
            return None

        referencia = self.referencia_entry.get().strip() or None

        cantidad = self.cantidad_entry.get().strip()
        if not cantidad:
            messagebox.showwarning("Campo requerido", "Cantidad es obligatoria.")
            return None
        try:
            cantidad_val = int(cantidad)
            if cantidad_val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Valor inválido", "Cantidad debe ser un número entero mayor a 0.")
            return None

        costo = self.costo_entry.get().strip()
        if not costo:
            messagebox.showwarning("Campo requerido", "Costo unitario es obligatorio.")
            return None
        try:
            costo_val = float(costo)
            if costo_val < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Valor inválido", "Costo unitario debe ser un número mayor o igual a 0.")
            return None

        return (mant_id, nombre, referencia, cantidad_val, costo_val)

    def set_form_values(self, row):
        mant_key = next((k for k, v in self.mantenimiento_map.items() if v == row[1]), None)
        if mant_key:
            self.mantenimiento_cb.set(mant_key)
        self.nombre_entry.delete(0, "end")
        self.nombre_entry.insert(0, row[2] or "")
        self.referencia_entry.delete(0, "end")
        self.referencia_entry.insert(0, row[3] or "")
        self.cantidad_entry.delete(0, "end")
        self.cantidad_entry.insert(0, row[4])
        self.costo_entry.delete(0, "end")
        self.costo_entry.insert(0, row[5])

    def clear_form(self):
        if self.mantenimiento_cb['values']:
            self.mantenimiento_cb.set(self.mantenimiento_cb['values'][0])
        self.nombre_entry.delete(0, "end")
        self.referencia_entry.delete(0, "end")
        self.cantidad_entry.delete(0, "end")
        self.costo_entry.delete(0, "end")

    def _label_from_map(self, mapping, value):
        for key, val in mapping.items():
            if val == value:
                return key
        return value

    def db_read(self, kw=""):
        conn = get_conn()
        c = conn.cursor()
        q = ("SELECT r.id_repuesto, r.id_mantenimiento, r.nombre, r.referencia, "
             "r.cantidad, r.costo_unitario FROM REPUESTO_MANTENIMIENTO r")
        if kw:
            c.execute(q + " WHERE r.nombre LIKE %s OR r.referencia LIKE %s ",
                      (f"%{kw}%", f"%{kw}%"))
        else:
            c.execute(q)
        rows = []
        for r in c.fetchall():
            rows.append((
                r[0],
                self._label_from_map(self.mantenimiento_map, r[1]),
                r[2],
                r[3] or "",
                r[4],
                r[5],
            ))
        conn.close()
        return rows
