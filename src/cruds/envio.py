"""
CRUD para Envíos
"""

from tkinter import messagebox
from .base import CRUDBase, styled_entry, styled_label, styled_combo
from database.conecction import get_conn


class CRUDEnvio(CRUDBase):
    TITLE       = "GESTIÓN DE ENVÍOS"
    TABLE       = "ENVIO"
    PK          = "id_envio"
    COLUMNS     = ("ID","Cliente","Viaje","Origen","Destino","Descripción","Solicitud","Estado")
    COL_WIDTHS  = {"ID":50,"Cliente":180,"Viaje":140,"Origen":150,"Destino":150,
                   "Descripción":180,"Solicitud":140,"Estado":110}
    FIELD_NAMES = ("id_cliente","id_viaje","direccion_origen","direccion_destino",
                   "descripcion","estado","creado_por")

    def build_form(self, p):
        styled_label(p, "Cliente*").grid(row=0, column=0, sticky="w", pady=3)
        self.cliente_cb = styled_combo(p, self._load_cliente_options(), width=26)
        self.cliente_cb.grid(row=0, column=1, pady=3, padx=(6,0))
        if self.cliente_cb['values']:
            self.cliente_cb.set(self.cliente_cb['values'][0])

        styled_label(p, "Viaje*").grid(row=1, column=0, sticky="w", pady=3)
        self.viaje_cb = styled_combo(p, self._load_viaje_options(), width=26)
        self.viaje_cb.grid(row=1, column=1, pady=3, padx=(6,0))
        if self.viaje_cb['values']:
            self.viaje_cb.set(self.viaje_cb['values'][0])

        fields = [
            ("Dirección origen*", "origen"),
            ("Dirección destino*", "destino"),
            ("Descripción", "descripcion"),
        ]
        self.vars = {}
        for i, (lbl, key) in enumerate(fields, start=2):
            styled_label(p, lbl).grid(row=i, column=0, sticky="w", pady=3)
            e = styled_entry(p, width=28)
            e.grid(row=i, column=1, pady=3, padx=(6,0))
            self.vars[key] = e

        styled_label(p, "Estado*").grid(row=5, column=0, sticky="w", pady=3)
        self.est_cb = styled_combo(p, ["pendiente","en_transito","entregado","devuelto","cancelado"], width=26)
        self.est_cb.grid(row=5, column=1, pady=3, padx=(6,0))
        self.est_cb.set("pendiente")

        styled_label(p, "Creado por").grid(row=6, column=0, sticky="w", pady=3)
        self.usuario_cb = styled_combo(p, self._load_usuario_options(), width=26)
        self.usuario_cb.grid(row=6, column=1, pady=3, padx=(6,0))
        self.usuario_cb.set("Ninguno")

    def _load_cliente_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_cliente, nombre_razon_social FROM CLIENTE")
        rows = c.fetchall()
        conn.close()
        self.cliente_map = {f"{r[0]} - {r[1]}": r[0] for r in rows}
        return list(self.cliente_map.keys())

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

    def _selected_cliente_id(self):
        return self.cliente_map.get(self.cliente_cb.get())

    def _selected_viaje_id(self):
        return self.viaje_map.get(self.viaje_cb.get())

    def _selected_usuario_id(self):
        return self.usuario_map.get(self.usuario_cb.get())

    def get_form_values(self):
        cliente_id = self._selected_cliente_id()
        if cliente_id is None:
            messagebox.showwarning("Campo requerido", "Selecciona un cliente válido.")
            return None
        viaje_id = self._selected_viaje_id()
        if viaje_id is None:
            messagebox.showwarning("Campo requerido", "Selecciona un viaje válido.")
            return None
        origen = self.vars["origen"].get().strip()
        destino = self.vars["destino"].get().strip()
        if not origen:
            messagebox.showwarning("Campo requerido", "Dirección origen es obligatoria.")
            return None
        if not destino:
            messagebox.showwarning("Campo requerido", "Dirección destino es obligatoria.")
            return None
        return (cliente_id, viaje_id, origen, destino,
                self.vars["descripcion"].get().strip(),
                self.est_cb.get(), self._selected_usuario_id())

    def set_form_values(self, row):
        cliente_key = next((k for k, v in self.cliente_map.items() if v == row[1]), None)
        if cliente_key:
            self.cliente_cb.set(cliente_key)
        viaje_key = next((k for k, v in self.viaje_map.items() if v == row[2]), None)
        if viaje_key:
            self.viaje_cb.set(viaje_key)
        self.vars["origen"].delete(0, "end")
        self.vars["origen"].insert(0, row[3])
        self.vars["destino"].delete(0, "end")
        self.vars["destino"].insert(0, row[4])
        self.vars["descripcion"].delete(0, "end")
        self.vars["descripcion"].insert(0, row[5] or "")
        self.est_cb.set(row[7])
        self.usuario_cb.set(row[8] or "Ninguno")

    def clear_form(self):
        if self.cliente_cb['values']:
            self.cliente_cb.set(self.cliente_cb['values'][0])
        if self.viaje_cb['values']:
            self.viaje_cb.set(self.viaje_cb['values'][0])
        for key in ["origen","destino","descripcion"]:
            self.vars[key].delete(0, "end")
        self.est_cb.set("pendiente")
        self.usuario_cb.set("Ninguno")

    def _label_from_map(self, mapping, value):
        for key, val in mapping.items():
            if val == value:
                return key
        return value

    def db_read(self, kw=""):
        conn = get_conn()
        c = conn.cursor()
        q = ("SELECT e.id_envio, e.id_cliente, e.id_viaje, e.direccion_origen, e.direccion_destino, "
             "e.descripcion, e.fecha_solicitud, e.estado, e.creado_por "
             "FROM ENVIO e")
        if kw:
            c.execute(q + " WHERE e.direccion_origen LIKE %s OR e.direccion_destino LIKE %s OR e.descripcion LIKE %s OR e.estado LIKE %s",
                      (f"%{kw}%",)*4)
        else:
            c.execute(q)
        rows = []
        for r in c.fetchall():
            rows.append((
                r[0],
                self._label_from_map(self.cliente_map, r[1]),
                self._label_from_map(self.viaje_map, r[2]),
                r[3],
                r[4],
                r[5],
                r[6],
                r[7],
            ))
        conn.close()
        return rows
