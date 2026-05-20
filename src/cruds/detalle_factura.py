"""
CRUD para Detalles de Factura
"""

from tkinter import messagebox
from .base import CRUDBase, styled_entry, styled_label, styled_combo
from database.conecction import get_conn


class CRUDDetalleFactura(CRUDBase):
    TITLE       = "DETALLE DE FACTURAS"
    TABLE       = "DETALLE_FACTURA"
    PK          = "id_detalle_factura"
    COLUMNS     = ("ID","Factura","Envío","Descripción","Cantidad","Valor unitario","Subtotal línea")
    COL_WIDTHS  = {"ID":50,"Factura":140,"Envío":120,"Descripción":220,
                   "Cantidad":80,"Valor unitario":100,"Subtotal línea":120}
    FIELD_NAMES = ("id_factura","id_envio","descripcion","cantidad",
                   "valor_unitario","subtotal_linea")

    def build_form(self, p):
        styled_label(p, "Factura*").grid(row=0, column=0, sticky="w", pady=3)
        self.factura_cb = styled_combo(p, self._load_factura_options(), width=26)
        self.factura_cb.grid(row=0, column=1, pady=3, padx=(6,0))

        styled_label(p, "Envío*").grid(row=1, column=0, sticky="w", pady=3)
        self.envio_cb = styled_combo(p, self._load_envio_options(), width=26)
        self.envio_cb.grid(row=1, column=1, pady=3, padx=(6,0))

        fields = [
            ("Descripción*", "descripcion"),
            ("Cantidad*", "cantidad"),
            ("Valor unitario*", "valor_unitario"),
            ("Subtotal línea", "subtotal"),
        ]
        self.vars = {}
        for i, (lbl, key) in enumerate(fields, start=2):
            styled_label(p, lbl).grid(row=i, column=0, sticky="w", pady=3)
            e = styled_entry(p, width=28)
            e.grid(row=i, column=1, pady=3, padx=(6,0))
            self.vars[key] = e

    def _load_factura_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_factura, numero_factura FROM FACTURA")
        rows = c.fetchall()
        conn.close()
        self.factura_map = {f"{r[0]} - {r[1]}": r[0] for r in rows}
        return list(self.factura_map.keys())

    def _load_envio_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_envio, direccion_destino FROM ENVIO")
        rows = c.fetchall()
        conn.close()
        self.envio_map = {f"{r[0]} - {r[1]}": r[0] for r in rows}
        return list(self.envio_map.keys())

    def _selected_factura_id(self):
        return self.factura_map.get(self.factura_cb.get())

    def _selected_envio_id(self):
        return self.envio_map.get(self.envio_cb.get())

    def get_form_values(self):
        factura_id = self._selected_factura_id()
        envio_id = self._selected_envio_id()
        if factura_id is None:
            messagebox.showwarning("Campo requerido", "Selecciona una factura válida.")
            return None
        if envio_id is None:
            messagebox.showwarning("Campo requerido", "Selecciona un envío válido.")
            return None
        descripcion = self.vars["descripcion"].get().strip()
        cantidad_txt = self.vars["cantidad"].get().strip()
        valor_txt = self.vars["valor_unitario"].get().strip()
        if not descripcion:
            messagebox.showwarning("Campo requerido", "Descripción es obligatoria.")
            return None
        try:
            cantidad = int(cantidad_txt)
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Formato", "Cantidad debe ser un número entero mayor que 0.")
            return None
        try:
            valor_unitario = float(valor_txt)
            if valor_unitario < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Formato", "Valor unitario debe ser un número mayor o igual a 0.")
            return None
        subtotal_linea = round(cantidad * valor_unitario, 2)
        self.vars["subtotal"].delete(0, "end")
        self.vars["subtotal"].insert(0, str(subtotal_linea))
        return (factura_id, envio_id, descripcion, cantidad, valor_unitario, subtotal_linea)

    def set_form_values(self, row):
        self.factura_cb.set(row[1] or "")
        self.envio_cb.set(row[2] or "")
        self.vars["descripcion"].delete(0, "end")
        self.vars["descripcion"].insert(0, row[3])
        self.vars["cantidad"].delete(0, "end")
        self.vars["cantidad"].insert(0, row[4])
        self.vars["valor_unitario"].delete(0, "end")
        self.vars["valor_unitario"].insert(0, row[5])
        self.vars["subtotal"].delete(0, "end")
        self.vars["subtotal"].insert(0, row[6])

    def clear_form(self):
        if self.factura_cb['values']:
            self.factura_cb.set(self.factura_cb['values'][0])
        if self.envio_cb['values']:
            self.envio_cb.set(self.envio_cb['values'][0])
        for key in ["descripcion","cantidad","valor_unitario","subtotal"]:
            self.vars[key].delete(0, "end")

    def db_read(self, kw=""):
        conn = get_conn()
        c = conn.cursor()
        q = ("SELECT d.id_detalle_factura, CONCAT(f.id_factura, ' - ', f.numero_factura), "
             "CONCAT(e.id_envio, ' - ', e.direccion_destino), d.descripcion, d.cantidad, d.valor_unitario, d.subtotal_linea "
             "FROM DETALLE_FACTURA d "
             "JOIN FACTURA f ON d.id_factura = f.id_factura "
             "JOIN ENVIO e ON d.id_envio = e.id_envio")
        if kw:
            c.execute(q + " WHERE f.numero_factura LIKE %s OR e.numero_envio LIKE %s OR d.descripcion LIKE %s",
                      (f"%{kw}%",)*3)
        else:
            c.execute(q)
        rows = c.fetchall()
        conn.close()
        return rows
