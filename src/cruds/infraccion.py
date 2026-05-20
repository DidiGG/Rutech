"""
CRUD para Infracciones
"""

from tkinter import messagebox
from .base import CRUDBase, styled_entry, styled_label, styled_combo
from database.conecction import get_conn


class CRUDInfraccion(CRUDBase):
    TITLE       = "GESTIÓN DE INFRACCIONES"
    TABLE       = "INFRACCION"
    PK          = "id_infraccion"
    COLUMNS     = ("ID","Conductor","Viaje","Fecha","Tipo","Monto","Estado pago","Autoridad")
    COL_WIDTHS  = {"ID":50,"Conductor":180,"Viaje":120,"Fecha":90,"Tipo":140,
                   "Monto":90,"Estado pago":120,"Autoridad":140}
    FIELD_NAMES = ("id_conductor","id_viaje","fecha","tipo","monto",
                   "descripcion","estado_pago","autoridad")

    def build_form(self, p):
        styled_label(p, "Conductor*").grid(row=0, column=0, sticky="w", pady=3)
        self.cond_cb = styled_combo(p, self._load_conductor_options(), width=26)
        self.cond_cb.grid(row=0, column=1, pady=3, padx=(6,0))

        styled_label(p, "Viaje").grid(row=1, column=0, sticky="w", pady=3)
        self.viaje_cb = styled_combo(p, self._load_viaje_options(), width=26)
        self.viaje_cb.grid(row=1, column=1, pady=3, padx=(6,0))
        self.viaje_cb.set("Ninguno")

        fields = [
            ("Fecha*", "fecha"),
            ("Tipo*", "tipo"),
            ("Monto*", "monto"),
            ("Autoridad*", "autoridad"),
            ("Descripción", "descripcion"),
        ]
        self.vars = {}
        for i, (lbl, key) in enumerate(fields, start=2):
            styled_label(p, lbl).grid(row=i, column=0, sticky="w", pady=3)
            e = styled_entry(p, width=28)
            e.grid(row=i, column=1, pady=3, padx=(6,0))
            self.vars[key] = e

        styled_label(p, "Estado pago*").grid(row=len(fields)+2, column=0, sticky="w", pady=3)
        self.est_cb = styled_combo(p, ["pendiente","pagada","en_disputa","condonada"], width=26)
        self.est_cb.grid(row=len(fields)+2, column=1, pady=3, padx=(6,0))
        self.est_cb.set("pendiente")

    def _load_conductor_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_conductor, nombre, apellido FROM CONDUCTOR WHERE estado = 'activo'")
        rows = c.fetchall()
        conn.close()
        self.conductor_map = {f"{r[0]} - {r[1]} {r[2]}": r[0] for r in rows}
        return list(self.conductor_map.keys())

    def _load_viaje_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_viaje, tipo_carga FROM VIAJE")
        rows = c.fetchall()
        conn.close()
        self.viaje_map = {"Ninguno": None}
        self.viaje_map.update({f"{r[0]} - {r[1]}": r[0] for r in rows})
        return list(self.viaje_map.keys())

    def _selected_conductor_id(self):
        return self.conductor_map.get(self.cond_cb.get())

    def _selected_viaje_id(self):
        return self.viaje_map.get(self.viaje_cb.get())

    def get_form_values(self):
        conductor_id = self._selected_conductor_id()
        if conductor_id is None:
            messagebox.showwarning("Campo requerido", "Selecciona un conductor válido.")
            return None
        fecha = self.vars["fecha"].get().strip()
        tipo = self.vars["tipo"].get().strip()
        autoridad = self.vars["autoridad"].get().strip()
        monto_txt = self.vars["monto"].get().strip()
        if not fecha:
            messagebox.showwarning("Campo requerido", "Fecha es obligatoria.")
            return None
        if not tipo:
            messagebox.showwarning("Campo requerido", "Tipo es obligatorio.")
            return None
        if not autoridad:
            messagebox.showwarning("Campo requerido", "Autoridad es obligatoria.")
            return None
        try:
            monto = float(monto_txt)
            if monto < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Formato", "Monto debe ser un número mayor o igual a 0.")
            return None
        return (conductor_id, self._selected_viaje_id(), fecha, tipo,
                monto, self.vars["descripcion"].get().strip(),
                self.est_cb.get(), autoridad)

    def set_form_values(self, row):
        self.cond_cb.set(row[1] or "")
        self.viaje_cb.set(row[2] or "Ninguno")
        self.vars["fecha"].delete(0, "end")
        self.vars["fecha"].insert(0, row[3])
        self.vars["tipo"].delete(0, "end")
        self.vars["tipo"].insert(0, row[4])
        self.vars["monto"].delete(0, "end")
        self.vars["monto"].insert(0, row[5])
        self.est_cb.set(row[6])
        self.vars["autoridad"].delete(0, "end")
        self.vars["autoridad"].insert(0, row[7])
        self.vars["descripcion"].delete(0, "end")
        self.vars["descripcion"].insert(0, row[8] or "")

    def clear_form(self):
        if self.cond_cb['values']:
            self.cond_cb.set(self.cond_cb['values'][0])
        self.viaje_cb.set("Ninguno")
        for key in ["fecha","tipo","monto","autoridad","descripcion"]:
            self.vars[key].delete(0, "end")
        self.est_cb.set("pendiente")

    def db_read(self, kw=""):
        conn = get_conn()
        c = conn.cursor()
        q = ("SELECT i.id_infraccion, CONCAT(c.id_conductor, ' - ', c.nombre, ' ', c.apellido), "
             "IFNULL(CONCAT(v.id_viaje, ' - ', v.tipo_carga), 'Ninguno'), i.fecha, i.tipo, "
             "i.monto, i.estado_pago, i.autoridad, i.descripcion "
             "FROM INFRACCION i "
             "JOIN CONDUCTOR c ON i.id_conductor = c.id_conductor "
             "LEFT JOIN VIAJE v ON i.id_viaje = v.id_viaje")
        if kw:
            c.execute(q + " WHERE c.nombre LIKE %s OR c.apellido LIKE %s OR i.tipo LIKE %s OR i.estado_pago LIKE %s OR i.autoridad LIKE %s",
                      (f"%{kw}%",)*5)
        else:
            c.execute(q)
        rows = c.fetchall()
        conn.close()
        return rows
