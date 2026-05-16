"""
CRUD para Usuarios
"""

import bcrypt
from tkinter import messagebox
from .base import CRUDBase, styled_entry, styled_label, styled_combo
from database.conecction import get_conn


class CRUDUsuario(CRUDBase):
    TITLE       = "GESTIÓN DE USUARIOS"
    TABLE       = "USUARIO"
    PK          = "id_usuario"
    COLUMNS     = ("ID","Usuario","Rol","Correo","Nombre completo","Estado","Conductor","Cliente")
    COL_WIDTHS  = {"ID":50,"Usuario":140,"Rol":100,"Correo":180,
                   "Nombre completo":170,"Estado":90,"Conductor":140,"Cliente":140}
    FIELD_NAMES = ("nombre_usuario","contrasena_hash","rol","correo",
                   "nombre_completo","estado","id_conductor","id_cliente")

    def build_form(self, p):
        fields = [
            ("Nombre usuario*", "usuario"),
            ("Contraseña", "contrasena"),
            ("Correo*", "correo"),
            ("Nombre completo*", "nombre"),
        ]
        self.vars = {}
        for i, (lbl, key) in enumerate(fields):
            styled_label(p, lbl).grid(row=i, column=0, sticky="w", pady=3)
            e = styled_entry(p, width=28)
            if key == "contrasena":
                e.config(show="*")
            e.grid(row=i, column=1, pady=3, padx=(6,0))
            self.vars[key] = e

        styled_label(p, "Rol*").grid(row=len(fields), column=0, sticky="w", pady=3)
        self.rol_cb = styled_combo(p, ["admin","coordinador","tecnico","conductor","cliente"], width=26)
        self.rol_cb.grid(row=len(fields), column=1, pady=3, padx=(6,0))
        self.rol_cb.set("cliente")

        styled_label(p, "Estado*").grid(row=len(fields)+1, column=0, sticky="w", pady=3)
        self.est_cb = styled_combo(p, ["activo","inactivo","bloqueado"], width=26)
        self.est_cb.grid(row=len(fields)+1, column=1, pady=3, padx=(6,0))
        self.est_cb.set("activo")

        styled_label(p, "Conductor").grid(row=len(fields)+2, column=0, sticky="w", pady=3)
        self.cond_cb = styled_combo(p, self._load_conductor_options(), width=26)
        self.cond_cb.grid(row=len(fields)+2, column=1, pady=3, padx=(6,0))
        self.cond_cb.set("Ninguno")

        styled_label(p, "Cliente").grid(row=len(fields)+3, column=0, sticky="w", pady=3)
        self.cliente_cb = styled_combo(p, self._load_cliente_options(), width=26)
        self.cliente_cb.grid(row=len(fields)+3, column=1, pady=3, padx=(6,0))
        self.cliente_cb.set("Ninguno")

        self.current_password_hash = None

    def _load_conductor_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_conductor, nombre, apellido FROM CONDUCTOR")
        rows = c.fetchall()
        conn.close()
        self.conductor_map = {"Ninguno": None}
        self.conductor_map.update({f"{r[0]} - {r[1]} {r[2]}": r[0] for r in rows})
        return list(self.conductor_map.keys())

    def _load_cliente_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_cliente, nombre_razon_social FROM CLIENTE")
        rows = c.fetchall()
        conn.close()
        self.cliente_map = {"Ninguno": None}
        self.cliente_map.update({f"{r[0]} - {r[1]}": r[0] for r in rows})
        return list(self.cliente_map.keys())

    def _selected_conductor_id(self):
        return self.conductor_map.get(self.cond_cb.get())

    def _selected_cliente_id(self):
        return self.cliente_map.get(self.cliente_cb.get())

    def get_form_values(self):
        nombre_usuario = self.vars["usuario"].get().strip()
        correo = self.vars["correo"].get().strip()
        nombre_completo = self.vars["nombre"].get().strip()
        if not nombre_usuario:
            messagebox.showwarning("Campo requerido", "Nombre de usuario es obligatorio.")
            return None
        if not correo:
            messagebox.showwarning("Campo requerido", "Correo es obligatorio.")
            return None
        if not nombre_completo:
            messagebox.showwarning("Campo requerido", "Nombre completo es obligatorio.")
            return None
        password = self.vars["contrasena"].get().strip()
        if password:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        else:
            if not self.current_password_hash:
                messagebox.showwarning("Campo requerido", "Contraseña es obligatoria para un nuevo usuario.")
                return None
            hashed = self.current_password_hash
        return (nombre_usuario, hashed, self.rol_cb.get(), correo,
                nombre_completo, self.est_cb.get(),
                self._selected_conductor_id(), self._selected_cliente_id())

    def _load_password_hash(self, user_id):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT contrasena_hash FROM USUARIO WHERE id_usuario = %s", (user_id,))
        row = c.fetchone()
        conn.close()
        self.current_password_hash = row[0] if row else None

    def set_form_values(self, row):
        self.vars["usuario"].delete(0, "end")
        self.vars["usuario"].insert(0, row[1])
        self.vars["contrasena"].delete(0, "end")
        self.vars["correo"].delete(0, "end")
        self.vars["correo"].insert(0, row[3] or "")
        self.vars["nombre"].delete(0, "end")
        self.vars["nombre"].insert(0, row[4] or "")
        self.rol_cb.set(row[2])
        self.est_cb.set(row[5])
        self.cond_cb.set(row[6] or "Ninguno")
        self.cliente_cb.set(row[7] or "Ninguno")

    def _on_select(self, _event=None):
        sel = self.tv.selection()
        if sel:
            row = self.tv.item(sel[0])["values"]
            self.set_form_values(row)
            self._load_password_hash(row[0])

    def clear_form(self):
        for key in ["usuario","contrasena","correo","nombre"]:
            self.vars[key].delete(0, "end")
        self.rol_cb.set("cliente")
        self.est_cb.set("activo")
        self.cond_cb.set("Ninguno")
        self.cliente_cb.set("Ninguno")
        self.current_password_hash = None

    def db_read(self, kw=""):
        conn = get_conn()
        c = conn.cursor()
        q = ("SELECT u.id_usuario, u.nombre_usuario, u.rol, u.correo, u.nombre_completo, "
             "u.estado, CONCAT(c.nombre, ' ', c.apellido), cl.nombre_razon_social "
             "FROM USUARIO u "
             "LEFT JOIN CONDUCTOR c ON u.id_conductor = c.id_conductor "
             "LEFT JOIN CLIENTE cl ON u.id_cliente = cl.id_cliente")
        if kw:
            c.execute(q + " WHERE u.nombre_usuario LIKE %s OR u.correo LIKE %s OR u.nombre_completo LIKE %s OR u.rol LIKE %s",
                      (f"%{kw}%",)*4)
        else:
            c.execute(q)
        rows = c.fetchall()
        conn.close()
        return rows
