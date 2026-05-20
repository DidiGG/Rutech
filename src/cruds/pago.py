"""
CRUD para Pagos
"""

from tkinter import messagebox
from .base import CRUDBase, styled_entry, styled_label, styled_combo, notify_invoice_state
from database.conecction import get_conn


class CRUDPago(CRUDBase):
    TITLE       = "GESTIÓN DE PAGOS"
    TABLE       = "PAGO"
    PK          = "id_pago"
    COLUMNS     = ("ID","Factura","Fecha pago","Monto","Método","Referencia","Estado","Creado por")
    COL_WIDTHS  = {"ID":50,"Factura":140,"Fecha pago":90,"Monto":100,
                   "Método":120,"Referencia":160,"Estado":100,"Creado por":140}
    FIELD_NAMES = ("id_factura","fecha_pago","monto","metodo","referencia_transaccion",
                   "estado","url_comprobante","creado_por")

    def build_form(self, p):
        styled_label(p, "Factura*").grid(row=0, column=0, sticky="w", pady=3)
        self.factura_cb = styled_combo(p, self._load_factura_options(), width=26)
        self.factura_cb.grid(row=0, column=1, pady=3, padx=(6,0))

        fields = [
            ("Fecha pago*", "fecha_pago"),
            ("Monto*", "monto"),
            ("Referencia", "referencia"),
            ("URL comprobante", "url"),
        ]
        self.vars = {}
        for i, (lbl, key) in enumerate(fields, start=1):
            styled_label(p, lbl).grid(row=i, column=0, sticky="w", pady=3)
            e = styled_entry(p, width=28)
            e.grid(row=i, column=1, pady=3, padx=(6,0))
            self.vars[key] = e

        styled_label(p, "Método*").grid(row=len(fields)+1, column=0, sticky="w", pady=3)
        self.met_cb = styled_combo(p, ["transferencia","efectivo","cheque","tarjeta_credito","tarjeta_debito","pse"], width=26)
        self.met_cb.grid(row=len(fields)+1, column=1, pady=3, padx=(6,0))
        self.met_cb.set("transferencia")

        styled_label(p, "Estado*").grid(row=len(fields)+2, column=0, sticky="w", pady=3)
        self.est_cb = styled_combo(p, ["confirmado","pendiente","rechazado"], width=26)
        self.est_cb.grid(row=len(fields)+2, column=1, pady=3, padx=(6,0))
        self.est_cb.set("pendiente")

        styled_label(p, "Creado por").grid(row=len(fields)+3, column=0, sticky="w", pady=3)
        self.usuario_cb = styled_combo(p, self._load_usuario_options(), width=26)
        self.usuario_cb.grid(row=len(fields)+3, column=1, pady=3, padx=(6,0))
        self.usuario_cb.set("Ninguno")

    def _load_factura_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_factura, numero_factura FROM FACTURA")
        rows = c.fetchall()
        conn.close()
        self.factura_map = {f"{r[0]} - {r[1]}": r[0] for r in rows}
        return list(self.factura_map.keys())

    def _load_usuario_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_usuario, nombre_usuario FROM USUARIO")
        rows = c.fetchall()
        conn.close()
        self.usuario_map = {"Ninguno": None}
        self.usuario_map.update({f"{r[0]} - {r[1]}": r[0] for r in rows})
        return list(self.usuario_map.keys())

    def _selected_factura_id(self):
        return self.factura_map.get(self.factura_cb.get())

    def _selected_usuario_id(self):
        return self.usuario_map.get(self.usuario_cb.get())

    def get_form_values(self):
        factura_id = self._selected_factura_id()
        if factura_id is None:
            messagebox.showwarning("Campo requerido", "Selecciona una factura válida.")
            return None
        fecha_pago = self.vars["fecha_pago"].get().strip()
        if not fecha_pago:
            messagebox.showwarning("Campo requerido", "Fecha de pago es obligatoria.")
            return None
        try:
            monto = float(self.vars["monto"].get().strip())
            if monto <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Formato", "Monto debe ser un número mayor que 0.")
            return None
        return (factura_id, fecha_pago, monto, self.met_cb.get(),
                self.vars["referencia"].get().strip(), self.est_cb.get(),
                self.vars["url"].get().strip(), self._selected_usuario_id())

    def _sync_invoice_status(self, factura_id):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT total, estado FROM FACTURA WHERE id_factura = %s", (factura_id,))
        factura = c.fetchone()
        if not factura:
            conn.close()
            return
        total, estado = float(factura[0]), factura[1]
        c.execute("SELECT SUM(monto) FROM PAGO WHERE id_factura = %s", (factura_id,))
        paid = c.fetchone()[0] or 0
        paid = float(paid)
        if estado == 'anulada':
            conn.close()
            return
        new_state = 'pagada' if paid >= total else ('vencida' if estado == 'vencida' else 'pendiente')
        if new_state != estado:
            c.execute("UPDATE FACTURA SET estado = %s WHERE id_factura = %s", (new_state, factura_id))
            conn.commit()
            notify_invoice_state(factura_id, new_state)
        conn.close()

    def _insert(self):
        vals = self.get_form_values()
        if vals is None:
            return
        factura_id = vals[0]
        try:
            conn = get_conn()
            c = conn.cursor()
            ph = ", ".join(["%s"] * len(self.FIELD_NAMES))
            fields = ", ".join(self.FIELD_NAMES)
            c.execute(f"INSERT INTO {self.TABLE} ({fields}) VALUES ({ph})", vals)
            conn.commit()
            self._sync_invoice_status(factura_id)
            conn.close()
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
        vals = self.get_form_values()
        if vals is None:
            return
        factura_id = vals[0]
        try:
            conn = get_conn()
            c = conn.cursor()
            set_clause = ", ".join(f"{f}=%s" for f in self.FIELD_NAMES)
            c.execute(
                f"UPDATE {self.TABLE} SET {set_clause} WHERE {self.PK}=%s",
                (*vals, pk_val)
            )
            conn.commit()
            self._sync_invoice_status(factura_id)
            conn.close()
            messagebox.showinfo("✅ Éxito", "Registro actualizado.")
            self._load()
        except Exception as e:
            messagebox.showerror("Error al actualizar", str(e))

    def _delete(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showwarning("Selección", "Selecciona un registro primero.")
            return
        pk_val = self.tv.item(sel[0])["values"][0]
        if not messagebox.askyesno("Confirmar", f"¿Eliminar registro #{pk_val}?"):
            return
        try:
            conn = get_conn()
            c = conn.cursor()
            c.execute("SELECT id_factura FROM PAGO WHERE id_pago = %s", (pk_val,))
            row = c.fetchone()
            factura_id = row[0] if row else None
            c.execute(f"DELETE FROM {self.TABLE} WHERE {self.PK}=%s", (pk_val,))
            conn.commit()
            if factura_id:
                self._sync_invoice_status(factura_id)
            conn.close()
            messagebox.showinfo("✅ Éxito", "Registro eliminado.")
            self._clear()
            self._load()
        except Exception as e:
            messagebox.showerror("Error al eliminar", str(e))

    def set_form_values(self, row):
        self.factura_cb.set(row[1] or "")
        self.vars["fecha_pago"].delete(0, "end")
        self.vars["fecha_pago"].insert(0, row[2])
        self.vars["monto"].delete(0, "end")
        self.vars["monto"].insert(0, row[3])
        self.met_cb.set(row[4])
        self.vars["referencia"].delete(0, "end")
        self.vars["referencia"].insert(0, row[5] or "")
        self.est_cb.set(row[6])
        self.vars["url"].delete(0, "end")
        self.vars["url"].insert(0, row[7] or "")
        self.usuario_cb.set(row[8] or "Ninguno")

    def clear_form(self):
        if self.factura_cb['values']:
            self.factura_cb.set(self.factura_cb['values'][0])
        self.vars["fecha_pago"].delete(0, "end")
        self.vars["monto"].delete(0, "end")
        self.vars["referencia"].delete(0, "end")
        self.vars["url"].delete(0, "end")
        self.met_cb.set("transferencia")
        self.est_cb.set("pendiente")
        self.usuario_cb.set("Ninguno")

    def db_read(self, kw=""):
        conn = get_conn()
        c = conn.cursor()
        q = ("SELECT p.id_pago, CONCAT(f.id_factura, ' - ', f.numero_factura), p.fecha_pago, p.monto, p.metodo, "
             "p.referencia_transaccion, p.estado, IFNULL(u.nombre_usuario, 'Ninguno') "
             "FROM PAGO p "
             "JOIN FACTURA f ON p.id_factura = f.id_factura "
             "LEFT JOIN USUARIO u ON p.creado_por = u.id_usuario")
        if kw:
            c.execute(q + " WHERE f.numero_factura LIKE %s OR p.metodo LIKE %s OR p.estado LIKE %s OR u.nombre_usuario LIKE %s",
                      (f"%{kw}%",)*4)
        else:
            c.execute(q)
        rows = c.fetchall()
        conn.close()
        return rows
