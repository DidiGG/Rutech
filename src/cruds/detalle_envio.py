"""
CRUD para Detalles de Envío
"""

from tkinter import messagebox
from .base import CRUDBase, styled_entry, styled_label, styled_combo
from database.conecction import get_conn


class CRUDDetalleEnvio(CRUDBase):
    TITLE       = "GESTIÓN DE DETALLES DE ENVÍO"
    TABLE       = "DETALLE_ENVIO"
    PK          = "id_detalle_envio"
    COLUMNS     = ("ID","Envío","Descripción","Embalaje","Cantidad","Peso (kg)","Volumen (m3)","Valor declarado")
    COL_WIDTHS  = {"ID":50, "Envío":180, "Descripción":220, "Embalaje":120,
                   "Cantidad":90, "Peso (kg)":100, "Volumen (m3)":100, "Valor declarado":120}
    FIELD_NAMES = ("id_envio","descripcion_mercancia","tipo_embalaje",
                   "cantidad","peso_kg","volumen_m3","valor_declarado")

    def build_form(self, p):
        styled_label(p, "Envío*").grid(row=0, column=0, sticky="w", pady=3)
        self.envio_cb = styled_combo(p, self._load_envio_options(), width=28)
        self.envio_cb.grid(row=0, column=1, pady=3, padx=(6,0))
        if self.envio_cb['values']:
            self.envio_cb.set(self.envio_cb['values'][0])

        fields = [
            ("Descripción mercancía*", "descripcion_mercancia"),
            ("Tipo embalaje", "tipo_embalaje"),
            ("Cantidad*", "cantidad"),
            ("Peso (kg)*", "peso_kg"),
            ("Volumen (m3)", "volumen_m3"),
            ("Valor declarado*", "valor_declarado"),
        ]
        self.vars = {}
        for i, (lbl, key) in enumerate(fields, start=1):
            styled_label(p, lbl).grid(row=i, column=0, sticky="w", pady=3)
            e = styled_entry(p, width=28)
            e.grid(row=i, column=1, pady=3, padx=(6,0))
            self.vars[key] = e

    def _load_envio_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_envio, descripcion FROM ENVIO")
        rows = c.fetchall()
        conn.close()
        self.envio_map = {f"{r[0]} - {r[1]}": r[0] for r in rows}
        return list(self.envio_map.keys())

    def _selected_envio_id(self):
        return self.envio_map.get(self.envio_cb.get())

    def get_form_values(self):
        envio_id = self._selected_envio_id()
        if envio_id is None:
            messagebox.showwarning("Campo requerido", "Selecciona un envío válido.")
            return None

        descripcion = self.vars["descripcion_mercancia"].get().strip()
        if not descripcion:
            messagebox.showwarning("Campo requerido", "Descripción de la mercancía es obligatoria.")
            return None

        cantidad = self.vars["cantidad"].get().strip()
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

        peso = self.vars["peso_kg"].get().strip()
        if not peso:
            messagebox.showwarning("Campo requerido", "Peso en kg es obligatorio.")
            return None
        try:
            peso_val = float(peso)
            if peso_val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Valor inválido", "Peso debe ser un número mayor a 0.")
            return None

        volumen = self.vars["volumen_m3"].get().strip()
        volumen_val = None
        if volumen:
            try:
                volumen_val = float(volumen)
                if volumen_val <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Valor inválido", "Volumen debe ser un número mayor a 0.")
                return None

        valor = self.vars["valor_declarado"].get().strip()
        if not valor:
            messagebox.showwarning("Campo requerido", "Valor declarado es obligatorio.")
            return None
        try:
            valor_val = float(valor)
            if valor_val < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Valor inválido", "Valor declarado debe ser un número mayor o igual a 0.")
            return None

        return (envio_id,
                descripcion,
                self.vars["tipo_embalaje"].get().strip() or None,
                cantidad_val,
                peso_val,
                volumen_val,
                valor_val)

    def set_form_values(self, row):
        envio_key = next((k for k, v in self.envio_map.items() if v == row[1]), None)
        if envio_key:
            self.envio_cb.set(envio_key)
        self.vars["descripcion_mercancia"].delete(0, "end")
        self.vars["descripcion_mercancia"].insert(0, row[2] or "")
        self.vars["tipo_embalaje"].delete(0, "end")
        self.vars["tipo_embalaje"].insert(0, row[3] or "")
        self.vars["cantidad"].delete(0, "end")
        self.vars["cantidad"].insert(0, row[4])
        self.vars["peso_kg"].delete(0, "end")
        self.vars["peso_kg"].insert(0, row[5])
        self.vars["volumen_m3"].delete(0, "end")
        self.vars["volumen_m3"].insert(0, row[6] or "")
        self.vars["valor_declarado"].delete(0, "end")
        self.vars["valor_declarado"].insert(0, row[7])

    def clear_form(self):
        if self.envio_cb['values']:
            self.envio_cb.set(self.envio_cb['values'][0])
        for key in ["descripcion_mercancia","tipo_embalaje","cantidad",
                    "peso_kg","volumen_m3","valor_declarado"]:
            self.vars[key].delete(0, "end")

    def _label_from_map(self, mapping, value):
        for key, val in mapping.items():
            if val == value:
                return key
        return value

    def db_read(self, kw=""):
        conn = get_conn()
        c = conn.cursor()
        q = ("SELECT d.id_detalle_envio, d.id_envio, d.descripcion_mercancia, d.tipo_embalaje, "
             "d.cantidad, d.peso_kg, d.volumen_m3, d.valor_declarado "
             "FROM DETALLE_ENVIO d "
             "JOIN ENVIO e ON d.id_envio = e.id_envio")
        if kw:
            c.execute(q + " WHERE d.descripcion_mercancia LIKE %s OR d.tipo_embalaje LIKE %s "
                      "OR e.direccion_origen LIKE %s OR e.direccion_destino LIKE %s",
                      (f"%{kw}%",)*4)
        else:
            c.execute(q)

        rows = []
        for r in c.fetchall():
            rows.append((
                r[0],
                self._label_from_map(self.envio_map, r[1]),
                r[2],
                r[3] or "",
                r[4],
                r[5],
                r[6] or "",
                r[7],
            ))
        conn.close()
        return rows
