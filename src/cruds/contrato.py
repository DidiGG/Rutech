"""
CRUD para Contratos
"""

from tkinter import messagebox
from .base import CRUDBase, styled_entry, styled_label, styled_combo
from database.conecction import get_conn


class CRUDContrato(CRUDBase):
    TITLE       = "GESTIÓN DE CONTRATOS"
    TABLE       = "CONTRATO"
    PK          = "id_contrato"
    COLUMNS     = ("ID","Proveedor","Inicio","Fin","Valor","Servicio","Estado","Creado por")
    COL_WIDTHS  = {"ID":50,"Proveedor":150,"Inicio":90,"Fin":90,
                   "Valor":100,"Servicio":140,"Estado":90,"Creado por":140}
    FIELD_NAMES = ("id_proveedor","fecha_inicio","fecha_fin","valor",
                   "tipo_servicio","estado","creado_por")

    def build_form(self, p):
        styled_label(p, "Proveedor*").grid(row=0, column=0, sticky="w", pady=3)
        self.proveedor_cb = styled_combo(p, self._load_proveedor_options(), width=26)
        self.proveedor_cb.grid(row=0, column=1, pady=3, padx=(6,0))
        if self.proveedor_cb['values']:
            self.proveedor_cb.set(self.proveedor_cb['values'][0])

        fields = [
            ("Fecha inicio*", "inicio"),
            ("Fecha fin*", "fin"),
            ("Valor*", "valor"),
            ("Tipo servicio*", "servicio"),
        ]
        self.vars = {}
        for i, (lbl, key) in enumerate(fields, start=1):
            styled_label(p, lbl).grid(row=i, column=0, sticky="w", pady=3)
            if key == "servicio":
                self.vars[key] = styled_entry(p, width=28)
                self.vars[key].grid(row=i, column=1, pady=3, padx=(6,0))
            else:
                e = styled_entry(p, width=28)
                e.grid(row=i, column=1, pady=3, padx=(6,0))
                self.vars[key] = e

        styled_label(p, "Estado*").grid(row=len(fields)+1, column=0, sticky="w", pady=3)
        self.est_cb = styled_combo(p, ["vigente","vencido","cancelado"], width=26)
        self.est_cb.grid(row=len(fields)+1, column=1, pady=3, padx=(6,0))
        self.est_cb.set("vigente")

        styled_label(p, "Creado por").grid(row=len(fields)+2, column=0, sticky="w", pady=3)
        self.usuario_cb = styled_combo(p, self._load_usuario_options(), width=26)
        self.usuario_cb.grid(row=len(fields)+2, column=1, pady=3, padx=(6,0))
        self.usuario_cb.set("Ninguno")

    def _load_proveedor_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_proveedor, nombre FROM PROVEEDOR")
        rows = c.fetchall()
        conn.close()
        self.proveedor_map = {f"{r[0]} - {r[1]}": r[0] for r in rows}
        return list(self.proveedor_map.keys())

    def _load_usuario_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_usuario, nombre_usuario FROM USUARIO")
        rows = c.fetchall()
        conn.close()
        self.usuario_map = {"Ninguno": None}
        self.usuario_map.update({f"{r[0]} - {r[1]}": r[0] for r in rows})
        return list(self.usuario_map.keys())

    def _selected_proveedor_id(self):
        return self.proveedor_map.get(self.proveedor_cb.get())

    def _selected_usuario_id(self):
        return self.usuario_map.get(self.usuario_cb.get())

    def get_form_values(self):
        proveedor_id = self._selected_proveedor_id()
        if proveedor_id is None:
            messagebox.showwarning("Campo requerido", "Selecciona un proveedor válido.")
            return None
        inicio = self.vars["inicio"].get().strip()
        fin = self.vars["fin"].get().strip()
        if not inicio or not fin:
            messagebox.showwarning("Campo requerido", "Fecha inicio y fecha fin son obligatorias.")
            return None
        if fin < inicio:
            messagebox.showwarning("Validación", "La fecha fin debe ser igual o posterior a inicio.")
            return None
        servicio = self.vars["servicio"].get().strip()
        if not servicio:
            messagebox.showwarning("Campo requerido", "Tipo de servicio es obligatorio.")
            return None
        try:
            valor = float(self.vars["valor"].get().strip())
        except ValueError:
            messagebox.showwarning("Formato", "El valor debe ser numérico.")
            return None
        return (proveedor_id, inicio, fin, valor,
                servicio, self.est_cb.get(), self._selected_usuario_id())

    def set_form_values(self, row):
        provider_name = row[1]
        provider_key = next((key for key in self.proveedor_map if key.endswith(f" - {provider_name}")), None)
        if provider_key:
            self.proveedor_cb.set(provider_key)
        self.vars["inicio"].delete(0, "end")
        self.vars["inicio"].insert(0, row[2])
        self.vars["fin"].delete(0, "end")
        self.vars["fin"].insert(0, row[3])
        self.vars["valor"].delete(0, "end")
        self.vars["valor"].insert(0, row[4])
        self.vars["servicio"].delete(0, "end")
        self.vars["servicio"].insert(0, row[5])
        self.est_cb.set(row[6])
        if row[7] and any(key.endswith(f" - {row[7]}") for key in self.usuario_map):
            usuario_key = next((key for key in self.usuario_map if key.endswith(f" - {row[7]}")), "Ninguno")
            self.usuario_cb.set(usuario_key)
        else:
            self.usuario_cb.set("Ninguno")

    def clear_form(self):
        if self.proveedor_cb['values']:
            self.proveedor_cb.set(self.proveedor_cb['values'][0])
        self.usuario_cb.set("Ninguno")
        for key in ["inicio","fin","valor","servicio"]:
            self.vars[key].delete(0, "end")
        self.est_cb.set("vigente")

    def db_read(self, kw=""):
        conn = get_conn()
        c = conn.cursor()
        q = ("SELECT ct.id_contrato, p.nombre, ct.fecha_inicio, ct.fecha_fin, ct.valor, "
             "ct.tipo_servicio, ct.estado, u.nombre_usuario "
             "FROM CONTRATO ct "
             "JOIN PROVEEDOR p ON ct.id_proveedor = p.id_proveedor "
             "LEFT JOIN USUARIO u ON ct.creado_por = u.id_usuario")
        if kw:
            c.execute(q + " WHERE p.nombre LIKE %s OR ct.tipo_servicio LIKE %s OR ct.estado LIKE %s",
                      (f"%{kw}%",)*3)
        else:
            c.execute(q)
        rows = c.fetchall()
        conn.close()
        return rows
