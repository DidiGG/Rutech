"""
CRUD para Documentos de Vehículo
"""

from tkinter import messagebox
from .base import CRUDBase, styled_entry, styled_label, styled_combo
from database.conecction import get_conn


class CRUDDocumentoVehiculo(CRUDBase):
    TITLE       = "DOCUMENTOS DE VEHÍCULO"
    TABLE       = "DOCUMENTO_VEHICULO"
    PK          = "id_doc_vehiculo"
    COLUMNS     = ("ID","Vehículo","Tipo","Número","Emisión","Vencimiento","Estado")
    COL_WIDTHS  = {"ID":50,"Vehículo":140,"Tipo":120,"Número":120,
                   "Emisión":90,"Vencimiento":90,"Estado":100}
    FIELD_NAMES = ("id_vehiculo","tipo","numero","fecha_emision",
                   "fecha_vencimiento","url_archivo","estado")

    def build_form(self, p):
        styled_label(p, "Vehículo*").grid(row=0, column=0, sticky="w", pady=3)
        self.veh_cb = styled_combo(p, self._load_vehiculo_options(), width=26)
        self.veh_cb.grid(row=0, column=1, pady=3, padx=(6,0))
        if self.veh_cb['values']:
            self.veh_cb.set(self.veh_cb['values'][0])

        styled_label(p, "Tipo*").grid(row=1, column=0, sticky="w", pady=3)
        self.tipo_cb = styled_combo(p, ["soat","tarjeta_propiedad","tecnomecanica","seguro","otro"], width=26)
        self.tipo_cb.grid(row=1, column=1, pady=3, padx=(6,0))
        self.tipo_cb.set("soat")

        fields = [
            ("Número*", "numero"),
            ("Fecha emisión*", "emision"),
            ("Fecha vencimiento*", "vencimiento"),
            ("URL archivo", "url"),
        ]
        self.vars = {}
        for i, (lbl, key) in enumerate(fields, start=2):
            styled_label(p, lbl).grid(row=i, column=0, sticky="w", pady=3)
            e = styled_entry(p, width=28)
            e.grid(row=i, column=1, pady=3, padx=(6,0))
            self.vars[key] = e

        styled_label(p, "Estado*").grid(row=len(fields)+2, column=0, sticky="w", pady=3)
        self.est_cb = styled_combo(p, ["vigente","por_vencer","vencido"], width=26)
        self.est_cb.grid(row=len(fields)+2, column=1, pady=3, padx=(6,0))
        self.est_cb.set("vigente")

    def _load_vehiculo_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_vehiculo, placa FROM VEHICULO")
        rows = c.fetchall()
        conn.close()
        self.vehiculo_map = {f"{r[0]} - {r[1]}": r[0] for r in rows}
        return list(self.vehiculo_map.keys())

    def _selected_vehiculo_id(self):
        return self.vehiculo_map.get(self.veh_cb.get())

    def get_form_values(self):
        vehiculo_id = self._selected_vehiculo_id()
        if vehiculo_id is None:
            messagebox.showwarning("Campo requerido", "Selecciona un vehículo válido.")
            return None
        numero = self.vars["numero"].get().strip()
        if not numero:
            messagebox.showwarning("Campo requerido", "Número es obligatorio.")
            return None
        emision = self.vars["emision"].get().strip()
        vencimiento = self.vars["vencimiento"].get().strip()
        if not emision or not vencimiento:
            messagebox.showwarning("Campo requerido", "Fechas de emisión y vencimiento son obligatorias.")
            return None
        if vencimiento < emision:
            messagebox.showwarning("Validación", "La fecha de vencimiento debe ser igual o posterior a emisión.")
            return None
        return (vehiculo_id, self.tipo_cb.get(), numero,
                emision, vencimiento, self.vars["url"].get().strip(),
                self.est_cb.get())

    def set_form_values(self, row):
        vehiculo_name = row[1]
        vehiculo_key = next((k for k in self.vehiculo_map if k.endswith(f" - {vehiculo_name}")), None)
        if vehiculo_key:
            self.veh_cb.set(vehiculo_key)
        self.tipo_cb.set(row[2])
        self.vars["numero"].delete(0, "end")
        self.vars["numero"].insert(0, row[3])
        self.vars["emision"].delete(0, "end")
        self.vars["emision"].insert(0, row[4])
        self.vars["vencimiento"].delete(0, "end")
        self.vars["vencimiento"].insert(0, row[5])
        self.vars["url"].delete(0, "end")
        self.vars["url"].insert(0, row[6] or "")
        self.est_cb.set(row[7])

    def clear_form(self):
        if self.veh_cb['values']:
            self.veh_cb.set(self.veh_cb['values'][0])
        self.tipo_cb.set("soat")
        for key in ["numero","emision","vencimiento","url"]:
            self.vars[key].delete(0, "end")
        self.est_cb.set("vigente")

    def db_read(self, kw=""):
        conn = get_conn()
        c = conn.cursor()
        q = ("SELECT d.id_doc_vehiculo, CONCAT(v.placa, ' - ', v.marca), d.tipo, d.numero, "
             "d.fecha_emision, d.fecha_vencimiento, d.estado "
             "FROM DOCUMENTO_VEHICULO d "
             "JOIN VEHICULO v ON d.id_vehiculo = v.id_vehiculo")
        if kw:
            c.execute(q + " WHERE v.placa LIKE %s OR d.numero LIKE %s OR d.tipo LIKE %s",
                      (f"%{kw}%",)*3)
        else:
            c.execute(q)
        rows = c.fetchall()
        conn.close()
        return rows
