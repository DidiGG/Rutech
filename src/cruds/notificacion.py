"""
CRUD para Notificaciones
"""

import tkinter as tk
from tkinter import messagebox, StringVar
from .base import CRUDBase, styled_entry, styled_label, styled_combo, STYLE_BTN4, STYLE_BTN2
from database.conecction import get_conn


class CRUDNotificacion(CRUDBase):
    TITLE       = "GESTIÓN DE NOTIFICACIONES"
    TABLE       = "NOTIFICACION"
    PK          = "id_notificacion"
    COLUMNS     = ("ID","Usuario","Tipo","Mensaje","Fecha/Hora","Leída")
    COL_WIDTHS  = {"ID":50,"Usuario":140,"Tipo":140,"Mensaje":220,"Fecha/Hora":140,"Leída":70}
    FIELD_NAMES = ("id_usuario","tipo","mensaje","fecha_hora","leida")

    def build_form(self, p):
        styled_label(p, "Usuario*").grid(row=0, column=0, sticky="w", pady=3)
        self.usuario_cb = styled_combo(p, self._load_usuario_options(), width=26)
        self.usuario_cb.grid(row=0, column=1, pady=3, padx=(6,0))

        fields = [
            ("Tipo*", "tipo"),
            ("Mensaje*", "mensaje"),
            ("Fecha/Hora*", "fecha_hora"),
            ("Leída*", "leida"),
        ]
        self.vars = {}
        for i, (lbl, key) in enumerate(fields, start=1):
            styled_label(p, lbl).grid(row=i, column=0, sticky="w", pady=3)
            if key == "leida":
                self.leida_cb = styled_combo(p, ["false","true"], width=26)
                self.leida_cb.grid(row=i, column=1, pady=3, padx=(6,0))
                self.leida_cb.set("false")
            else:
                e = styled_entry(p, width=28)
                e.grid(row=i, column=1, pady=3, padx=(6,0))
                self.vars[key] = e

        styled_label(p, "Mostrar").grid(row=len(fields)+1, column=0, sticky="w", pady=3)
        self.filter_var = StringVar(value="Todas")
        self.filter_cb = styled_combo(p, ["Todas","No leídas","Leídas"], width=26, textvariable=self.filter_var)
        self.filter_cb.grid(row=len(fields)+1, column=1, pady=3, padx=(6,0))
        self.filter_cb.bind("<<ComboboxSelected>>", lambda e: self._load())

    def _load_usuario_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_usuario, nombre_usuario FROM USUARIO")
        rows = c.fetchall()
        conn.close()
        self.usuario_map = {f"{r[0]} - {r[1]}": r[0] for r in rows}
        return list(self.usuario_map.keys())

    def _selected_usuario_id(self):
        return self.usuario_map.get(self.usuario_cb.get())

    def get_form_values(self):
        usuario_id = self._selected_usuario_id()
        if usuario_id is None:
            messagebox.showwarning("Campo requerido", "Selecciona un usuario válido.")
            return None
        tipo = self.vars["tipo"].get().strip()
        mensaje = self.vars["mensaje"].get().strip()
        fecha_hora = self.vars["fecha_hora"].get().strip()
        if not tipo:
            messagebox.showwarning("Campo requerido", "Tipo es obligatorio.")
            return None
        if not mensaje:
            messagebox.showwarning("Campo requerido", "Mensaje es obligatorio.")
            return None
        if not fecha_hora:
            messagebox.showwarning("Campo requerido", "Fecha/Hora es obligatoria.")
            return None
        leida = self.leida_cb.get() == "true"
        return (usuario_id, tipo, mensaje, fecha_hora, leida)

    def set_form_values(self, row):
        self.usuario_cb.set(row[1] or "")
        self.vars["tipo"].delete(0, "end")
        self.vars["tipo"].insert(0, row[2])
        self.vars["mensaje"].delete(0, "end")
        self.vars["mensaje"].insert(0, row[3] or "")
        self.vars["fecha_hora"].delete(0, "end")
        self.vars["fecha_hora"].insert(0, row[4])
        self.leida_cb.set("true" if row[5] else "false")

    def clear_form(self):
        if self.usuario_cb['values']:
            self.usuario_cb.set(self.usuario_cb['values'][0])
        self.vars["tipo"].delete(0, "end")
        self.vars["mensaje"].delete(0, "end")
        self.vars["fecha_hora"].delete(0, "end")
        self.leida_cb.set("false")

    def build_extra_buttons(self, parent):
        tk.Button(parent, text="✔️  Marcar como leída", **STYLE_BTN4,
                  command=self._mark_as_read).pack(side="left", padx=(0,6))
        tk.Button(parent, text="↩️  Marcar como no leída", **STYLE_BTN2,
                  command=self._mark_as_unread).pack(side="left", padx=(0,6))

    def _mark_as_read(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showwarning("Selección", "Selecciona una notificación primero.")
            return
        pk_val = self.tv.item(sel[0])["values"][0]
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT leida FROM NOTIFICACION WHERE id_notificacion = %s", (pk_val,))
        row = c.fetchone()
        if not row:
            conn.close()
            messagebox.showerror("Error", "No se encontró la notificación seleccionada.")
            return
        if row[0]:
            conn.close()
            messagebox.showinfo("Información", "La notificación ya está marcada como leída.")
            return
        c.execute("UPDATE NOTIFICACION SET leida = TRUE WHERE id_notificacion = %s", (pk_val,))
        conn.commit()
        conn.close()
        messagebox.showinfo("✅ Éxito", "Notificación marcada como leída.")
        self._load()

    def _mark_as_unread(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showwarning("Selección", "Selecciona una notificación primero.")
            return
        pk_val = self.tv.item(sel[0])["values"][0]
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT leida FROM NOTIFICACION WHERE id_notificacion = %s", (pk_val,))
        row = c.fetchone()
        if not row:
            conn.close()
            messagebox.showerror("Error", "No se encontró la notificación seleccionada.")
            return
        if not row[0]:
            conn.close()
            messagebox.showinfo("Información", "La notificación ya está marcada como no leída.")
            return
        c.execute("UPDATE NOTIFICACION SET leida = FALSE WHERE id_notificacion = %s", (pk_val,))
        conn.commit()
        conn.close()
        messagebox.showinfo("✅ Éxito", "Notificación marcada como no leída.")
        self._load()

    def db_read(self, kw=""):
        conn = get_conn()
        c = conn.cursor()
        q = ("SELECT n.id_notificacion, CONCAT(u.id_usuario, ' - ', u.nombre_usuario), n.tipo, n.mensaje, n.fecha_hora, n.leida "
             "FROM NOTIFICACION n "
             "JOIN USUARIO u ON n.id_usuario = u.id_usuario")
        params = []
        if kw:
            q += " WHERE u.nombre_usuario LIKE %s OR n.tipo LIKE %s OR n.mensaje LIKE %s"
            params.extend((f"%{kw}%",)*3)

        if hasattr(self, 'filter_var') and self.filter_var.get() != "Todas":
            if "WHERE" in q:
                q += " AND "
            else:
                q += " WHERE "
            if self.filter_var.get() == "No leídas":
                q += "n.leida = FALSE"
            else:
                q += "n.leida = TRUE"

        c.execute(q, tuple(params))
        rows = c.fetchall()
        conn.close()
        return rows
