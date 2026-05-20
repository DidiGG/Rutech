"""
CRUD para Novedades de Viaje
"""

from tkinter import messagebox
from .base import CRUDBase, styled_entry, styled_label, styled_combo
from database.conecction import get_conn


class CRUDNovedadViaje(CRUDBase):
    TITLE       = "GESTIÓN DE NOVEDADES DE VIAJE"
    TABLE       = "NOVEDAD_VIAJE"
    PK          = "id_novedad"
    COLUMNS     = ("ID","Viaje","Tipo","Fecha/Hora","Estado","Creado por","Descripción")
    COL_WIDTHS  = {"ID":50,"Viaje":150,"Tipo":100,"Fecha/Hora":140,
                   "Estado":110,"Creado por":140,"Descripción":220}
    FIELD_NAMES = ("id_viaje","tipo","descripcion","fecha_hora","estado","creado_por")

    def build_form(self, p):
        styled_label(p, "Viaje*").grid(row=0, column=0, sticky="w", pady=3)
        self.viaje_cb = styled_combo(p, self._load_viaje_options(), width=26)
        self.viaje_cb.grid(row=0, column=1, pady=3, padx=(6,0))

        styled_label(p, "Tipo*").grid(row=1, column=0, sticky="w", pady=3)
        self.tipo_cb = styled_combo(p, ["accidente","demora","desvio","averia","otro"], width=26)
        self.tipo_cb.grid(row=1, column=1, pady=3, padx=(6,0))
        self.tipo_cb.set("otro")

        self.vars = {}
        fields = [
            ("Fecha/Hora*", "fecha_hora"),
            ("Estado*", "estado"),
            ("Descripción*", "descripcion"),
        ]
        for i, (lbl, key) in enumerate(fields, start=2):
            styled_label(p, lbl).grid(row=i, column=0, sticky="w", pady=3)
            if key == "estado":
                self.est_cb = styled_combo(p, ["abierta","en_gestion","cerrada"], width=26)
                self.est_cb.grid(row=i, column=1, pady=3, padx=(6,0))
                self.est_cb.set("abierta")
            else:
                e = styled_entry(p, width=28)
                e.grid(row=i, column=1, pady=3, padx=(6,0))
                self.vars[key] = e

        styled_label(p, "Creado por").grid(row=len(fields)+2, column=0, sticky="w", pady=3)
        self.usuario_cb = styled_combo(p, self._load_usuario_options(), width=26)
        self.usuario_cb.grid(row=len(fields)+2, column=1, pady=3, padx=(6,0))
        self.usuario_cb.set("Ninguno")

    def _load_viaje_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_viaje, tipo_carga FROM VIAJE")
        rows = c.fetchall()
        conn.close()
        self.viaje_map = {f"{r[0]} - {r[1]}": r[0] for r in rows}
        return list(self.viaje_map.keys())

    def _load_usuario_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_usuario, nombre_usuario FROM USUARIO")
        rows = c.fetchall()
        conn.close()
        self.usuario_map = {"Ninguno": None}
        self.usuario_map.update({f"{r[0]} - {r[1]}": r[0] for r in rows})
        return list(self.usuario_map.keys())

    def _selected_viaje_id(self):
        return self.viaje_map.get(self.viaje_cb.get())

    def _selected_usuario_id(self):
        return self.usuario_map.get(self.usuario_cb.get())

    def get_form_values(self):
        viaje_id = self._selected_viaje_id()
        if viaje_id is None:
            messagebox.showwarning("Campo requerido", "Selecciona un viaje válido.")
            return None
        fecha_hora = self.vars["fecha_hora"].get().strip()
        descripcion = self.vars["descripcion"].get().strip()
        if not fecha_hora:
            messagebox.showwarning("Campo requerido", "Fecha/Hora es obligatoria.")
            return None
        if not descripcion:
            messagebox.showwarning("Campo requerido", "Descripción es obligatoria.")
            return None
        return (viaje_id, self.tipo_cb.get(), descripcion, fecha_hora,
                self.est_cb.get(), self._selected_usuario_id())

    def set_form_values(self, row):
        self.viaje_cb.set(row[1] or "")
        self.tipo_cb.set(row[2])
        self.vars["fecha_hora"].delete(0, "end")
        self.vars["fecha_hora"].insert(0, row[3])
        self.est_cb.set(row[4])
        self.usuario_cb.set(row[5] or "Ninguno")
        self.vars["descripcion"].delete(0, "end")
        self.vars["descripcion"].insert(0, row[6] or "")

    def clear_form(self):
        if self.viaje_cb['values']:
            self.viaje_cb.set(self.viaje_cb['values'][0])
        self.tipo_cb.set("otro")
        self.vars["fecha_hora"].delete(0, "end")
        self.vars["descripcion"].delete(0, "end")
        self.est_cb.set("abierta")
        self.usuario_cb.set("Ninguno")

    def db_read(self, kw=""):
        conn = get_conn()
        c = conn.cursor()
        q = ("SELECT n.id_novedad, CONCAT(v.id_viaje, ' - ', v.tipo_carga), n.tipo, n.fecha_hora, n.estado, "
             "IFNULL(u.nombre_usuario, 'Ninguno'), n.descripcion "
             "FROM NOVEDAD_VIAJE n "
             "JOIN VIAJE v ON n.id_viaje = v.id_viaje "
             "LEFT JOIN USUARIO u ON n.creado_por = u.id_usuario")
        if kw:
            c.execute(q + " WHERE v.tipo_carga LIKE %s OR n.tipo LIKE %s OR n.estado LIKE %s OR u.nombre_usuario LIKE %s",
                      (f"%{kw}%",)*4)
        else:
            c.execute(q)
        rows = c.fetchall()
        conn.close()
        return rows
