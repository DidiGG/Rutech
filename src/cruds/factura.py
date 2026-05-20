"""
CRUD para Facturas
"""

from tkinter import messagebox
from .base import CRUDBase, styled_entry, styled_label, styled_combo, notify_invoice_state
from database.conecction import get_conn


class CRUDFactura(CRUDBase):
    TITLE       = "GESTIÓN DE FACTURAS"
    TABLE       = "FACTURA"
    PK          = "id_factura"
    COLUMNS     = ("ID","Viaje","Cliente","Número","Emisión","Vencimiento","Subtotal","IVA %","Total","Estado","Creado por")
    COL_WIDTHS  = {"ID":50,"Viaje":140,"Cliente":150,"Número":130,
                   "Emisión":90,"Vencimiento":90,"Subtotal":100,"IVA %":70,
                   "Total":100,"Estado":90,"Creado por":140}
    FIELD_NAMES = ("id_viaje","id_cliente","numero_factura","fecha_emision",
                   "fecha_vencimiento","subtotal","porcentaje_iva","total",
                   "estado","creado_por")

    def build_form(self, p):
        styled_label(p, "Viaje*").grid(row=0, column=0, sticky="w", pady=3)
        self.viaje_cb = styled_combo(p, self._load_viaje_options(), width=26)
        self.viaje_cb.grid(row=0, column=1, pady=3, padx=(6,0))

        styled_label(p, "Cliente*").grid(row=1, column=0, sticky="w", pady=3)
        self.cliente_cb = styled_combo(p, self._load_cliente_options(), width=26)
        self.cliente_cb.grid(row=1, column=1, pady=3, padx=(6,0))

        fields = [
            ("Número factura*", "numero"),
            ("Fecha emisión*", "emision"),
            ("Fecha vencimiento*", "vencimiento"),
            ("Subtotal*", "subtotal"),
            ("IVA %*", "iva"),
            ("Total", "total"),
        ]
        self.vars = {}
        for i, (lbl, key) in enumerate(fields, start=2):
            styled_label(p, lbl).grid(row=i, column=0, sticky="w", pady=3)
            e = styled_entry(p, width=28)
            e.grid(row=i, column=1, pady=3, padx=(6,0))
            self.vars[key] = e

        styled_label(p, "Estado*").grid(row=len(fields)+2, column=0, sticky="w", pady=3)
        self.est_cb = styled_combo(p, ["pendiente","pagada","vencida","anulada"], width=26)
        self.est_cb.grid(row=len(fields)+2, column=1, pady=3, padx=(6,0))
        self.est_cb.set("pendiente")

        styled_label(p, "Creado por").grid(row=len(fields)+3, column=0, sticky="w", pady=3)
        self.usuario_cb = styled_combo(p, self._load_usuario_options(), width=26)
        self.usuario_cb.grid(row=len(fields)+3, column=1, pady=3, padx=(6,0))
        self.usuario_cb.set("Ninguno")

    def _load_viaje_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_viaje, tipo_carga FROM VIAJE")
        rows = c.fetchall()
        conn.close()
        self.viaje_map = {f"{r[0]} - {r[1]}": r[0] for r in rows}
        return list(self.viaje_map.keys())

    def _load_cliente_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_cliente, nombre_razon_social FROM CLIENTE")
        rows = c.fetchall()
        conn.close()
        self.cliente_map = {f"{r[0]} - {r[1]}": r[0] for r in rows}
        return list(self.cliente_map.keys())

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

    def _selected_cliente_id(self):
        return self.cliente_map.get(self.cliente_cb.get())

    def _selected_usuario_id(self):
        return self.usuario_map.get(self.usuario_cb.get())

    def _compute_total(self, subtotal, iva):
        return round(subtotal + (subtotal * iva / 100), 2)

    def get_form_values(self):
        viaje_id = self._selected_viaje_id()
        if viaje_id is None:
            messagebox.showwarning("Campo requerido", "Selecciona un viaje válido.")
            return None
        cliente_id = self._selected_cliente_id()
        if cliente_id is None:
            messagebox.showwarning("Campo requerido", "Selecciona un cliente válido.")
            return None
        numero = self.vars["numero"].get().strip()
        emision = self.vars["emision"].get().strip()
        vencimiento = self.vars["vencimiento"].get().strip()
        if not numero or not emision or not vencimiento:
            messagebox.showwarning("Campo requerido", "Número, emisión y vencimiento son obligatorios.")
            return None
        if vencimiento < emision:
            messagebox.showwarning("Validación", "La fecha de vencimiento debe ser igual o posterior a la fecha de emisión.")
            return None
        try:
            subtotal = float(self.vars["subtotal"].get().strip())
            if subtotal < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Formato", "Subtotal debe ser un número mayor o igual a 0.")
            return None
        try:
            iva = float(self.vars["iva"].get().strip())
            if iva < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Formato", "IVA debe ser un número mayor o igual a 0.")
            return None
        total_txt = self.vars["total"].get().strip()
        total = self._compute_total(subtotal, iva)
        if total_txt:
            try:
                total_manual = float(total_txt)
                if abs(total_manual - total) > 0.01:
                    messagebox.showwarning("Validación", "El total no coincide con subtotal e IVA.")
                    return None
            except ValueError:
                messagebox.showwarning("Formato", "Total debe ser un número válido.")
                return None
        else:
            self.vars["total"].delete(0, "end")
            self.vars["total"].insert(0, str(total))
        return (viaje_id, cliente_id, numero, emision, vencimiento,
                subtotal, iva, total, self.est_cb.get(), self._selected_usuario_id())

    def set_form_values(self, row):
        self.viaje_cb.set(row[1] or "")
        self.cliente_cb.set(row[2] or "")
        self.vars["numero"].delete(0, "end")
        self.vars["numero"].insert(0, row[3])
        self.vars["emision"].delete(0, "end")
        self.vars["emision"].insert(0, row[4])
        self.vars["vencimiento"].delete(0, "end")
        self.vars["vencimiento"].insert(0, row[5])
        self.vars["subtotal"].delete(0, "end")
        self.vars["subtotal"].insert(0, row[6])
        self.vars["iva"].delete(0, "end")
        self.vars["iva"].insert(0, row[7])
        self.vars["total"].delete(0, "end")
        self.vars["total"].insert(0, row[8])
        self.est_cb.set(row[9])
        self.usuario_cb.set(row[10] or "Ninguno")

    def clear_form(self):
        if self.viaje_cb['values']:
            self.viaje_cb.set(self.viaje_cb['values'][0])
        if self.cliente_cb['values']:
            self.cliente_cb.set(self.cliente_cb['values'][0])
        self.vars["numero"].delete(0, "end")
        self.vars["emision"].delete(0, "end")
        self.vars["vencimiento"].delete(0, "end")
        self.vars["subtotal"].delete(0, "end")
        self.vars["iva"].delete(0, "end")
        self.vars["total"].delete(0, "end")
        self.est_cb.set("pendiente")
        self.usuario_cb.set("Ninguno")

    def _insert(self):
        vals = self.get_form_values()
        if vals is None:
            return
        try:
            conn = get_conn()
            c = conn.cursor()
            ph = ", ".join(["%s"] * len(self.FIELD_NAMES))
            fields = ", ".join(self.FIELD_NAMES)
            c.execute(f"INSERT INTO {self.TABLE} ({fields}) VALUES ({ph})", vals)
            conn.commit()
            factura_id = c.lastrowid
            conn.close()
            notify_invoice_state(factura_id, vals[8])
            messagebox.showinfo("✅ Éxito", "Registro insertado correctamente.")
            self._clear()
            self._load()
        except Exception as e:
            messagebox.showerror("Error al insertar", str(e))

    def _update(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showwarning("Selección", "Selecciona un registro primero.")
            return
        pk_val = self.tv.item(sel[0])["values"][0]
        old_state = None
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT estado FROM FACTURA WHERE id_factura = %s", (pk_val,))
        row = c.fetchone()
        old_state = row[0] if row else None
        conn.close()
        vals = self.get_form_values()
        if vals is None:
            return
        try:
            conn = get_conn()
            c = conn.cursor()
            set_clause = ", ".join(f"{f}=%s" for f in self.FIELD_NAMES)
            c.execute(
                f"UPDATE {self.TABLE} SET {set_clause} WHERE {self.PK}=%s",
                (*vals, pk_val)
            )
            conn.commit()
            conn.close()
            if old_state != vals[8]:
                notify_invoice_state(pk_val, vals[8])
            messagebox.showinfo("✅ Éxito", "Registro actualizado.")
            self._load()
        except Exception as e:
            messagebox.showerror("Error al actualizar", str(e))

    def db_read(self, kw=""):
        conn = get_conn()
        c = conn.cursor()
        q = ("SELECT f.id_factura, CONCAT(v.id_viaje, ' - ', v.tipo_carga), CONCAT(c.id_cliente, ' - ', c.nombre_razon_social), "
             "f.numero_factura, f.fecha_emision, f.fecha_vencimiento, f.subtotal, f.porcentaje_iva, f.total, f.estado, "
             "IFNULL(u.nombre_usuario, 'Ninguno') "
             "FROM FACTURA f "
             "JOIN VIAJE v ON f.id_viaje = v.id_viaje "
             "JOIN CLIENTE c ON f.id_cliente = c.id_cliente "
             "LEFT JOIN USUARIO u ON f.creado_por = u.id_usuario")
        if kw:
            c.execute(q + " WHERE f.numero_factura LIKE %s OR f.estado LIKE %s OR c.nombre_razon_social LIKE %s OR u.nombre_usuario LIKE %s",
                      (f"%{kw}%",)*4)
        else:
            c.execute(q)
        rows = c.fetchall()
        conn.close()
        return rows
