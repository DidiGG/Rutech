"""
CRUD para Posiciones GPS
"""

from datetime import datetime
from tkinter import messagebox
from .base import CRUDBase, styled_entry, styled_label, styled_combo
from database.conecction import get_conn


class CRUDPosicionGPS(CRUDBase):
    TITLE       = "GESTIÓN DE POSICIONES GPS"
    TABLE       = "POSICION_GPS"
    PK          = "id_posicion"
    COLUMNS     = ("ID","Viaje","Latitud","Longitud","Velocidad (km/h)","Marca tiempo","Evento")
    COL_WIDTHS  = {"ID":50, "Viaje":180, "Latitud":110, "Longitud":110,
                   "Velocidad (km/h)":120, "Marca tiempo":160, "Evento":140}
    FIELD_NAMES = ("id_viaje","latitud","longitud","velocidad_kmh","marca_tiempo","tipo_evento")

    def build_form(self, p):
        styled_label(p, "Viaje*").grid(row=0, column=0, sticky="w", pady=3)
        self.viaje_cb = styled_combo(p, self._load_viaje_options(), width=28)
        self.viaje_cb.grid(row=0, column=1, pady=3, padx=(6,0))
        if self.viaje_cb['values']:
            self.viaje_cb.set(self.viaje_cb['values'][0])

        fields = [
            ("Latitud*", "latitud"),
            ("Longitud*", "longitud"),
            ("Velocidad (km/h)", "velocidad_kmh"),
            ("Marca tiempo*", "marca_tiempo"),
            ("Tipo evento", "tipo_evento"),
        ]
        self.vars = {}
        for i, (lbl, key) in enumerate(fields, start=1):
            styled_label(p, lbl).grid(row=i, column=0, sticky="w", pady=3)
            e = styled_entry(p, width=28)
            e.grid(row=i, column=1, pady=3, padx=(6,0))
            self.vars[key] = e
        self.vars["marca_tiempo"].insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def _load_viaje_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_viaje, tipo_carga FROM VIAJE")
        rows = c.fetchall()
        conn.close()
        self.viaje_map = {f"{r[0]} - {r[1]}": r[0] for r in rows}
        return list(self.viaje_map.keys())

    def _selected_viaje_id(self):
        return self.viaje_map.get(self.viaje_cb.get())

    def get_form_values(self):
        viaje_id = self._selected_viaje_id()
        if viaje_id is None:
            messagebox.showwarning("Campo requerido", "Selecciona un viaje válido.")
            return None

        try:
            latitud = float(self.vars["latitud"].get().strip())
            if not (-90 <= latitud <= 90):
                raise ValueError
        except ValueError:
            messagebox.showwarning("Valor inválido", "Latitud debe ser un número entre -90 y 90.")
            return None

        try:
            longitud = float(self.vars["longitud"].get().strip())
            if not (-180 <= longitud <= 180):
                raise ValueError
        except ValueError:
            messagebox.showwarning("Valor inválido", "Longitud debe ser un número entre -180 y 180.")
            return None

        velocidad = self.vars["velocidad_kmh"].get().strip()
        velocidad_val = None
        if velocidad:
            try:
                velocidad_val = float(velocidad)
                if velocidad_val < 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Valor inválido", "Velocidad debe ser un número mayor o igual a 0.")
                return None

        marca_tiempo = self.vars["marca_tiempo"].get().strip()
        if not marca_tiempo:
            messagebox.showwarning("Campo requerido", "Marca tiempo es obligatoria.")
            return None
        try:
            marca_tiempo_val = datetime.fromisoformat(marca_tiempo)
        except ValueError:
            messagebox.showwarning("Formato inválido", "Marca tiempo debe usar formato YYYY-MM-DD HH:MM:SS.")
            return None

        return (viaje_id,
                latitud,
                longitud,
                velocidad_val,
                marca_tiempo_val.strftime("%Y-%m-%d %H:%M:%S"),
                self.vars["tipo_evento"].get().strip() or None)

    def set_form_values(self, row):
        viaje_key = next((k for k, v in self.viaje_map.items() if v == row[1]), None)
        if viaje_key:
            self.viaje_cb.set(viaje_key)
        self.vars["latitud"].delete(0, "end")
        self.vars["latitud"].insert(0, row[2])
        self.vars["longitud"].delete(0, "end")
        self.vars["longitud"].insert(0, row[3])
        self.vars["velocidad_kmh"].delete(0, "end")
        self.vars["velocidad_kmh"].insert(0, row[4] if row[4] is not None else "")
        self.vars["marca_tiempo"].delete(0, "end")
        self.vars["marca_tiempo"].insert(0, row[5])
        self.vars["tipo_evento"].delete(0, "end")
        self.vars["tipo_evento"].insert(0, row[6] or "")

    def clear_form(self):
        if self.viaje_cb['values']:
            self.viaje_cb.set(self.viaje_cb['values'][0])
        for key in ["latitud","longitud","velocidad_kmh","marca_tiempo","tipo_evento"]:
            self.vars[key].delete(0, "end")
        self.vars["marca_tiempo"].insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def _label_from_map(self, mapping, value):
        for key, val in mapping.items():
            if val == value:
                return key
        return value

    def db_read(self, kw=""):
        conn = get_conn()
        c = conn.cursor()
        q = ("SELECT p.id_posicion, p.id_viaje, p.latitud, p.longitud, p.velocidad_kmh, "
             "p.marca_tiempo, p.tipo_evento "
             "FROM POSICION_GPS p")
        if kw:
            c.execute(q + " WHERE p.tipo_evento LIKE %s OR p.marca_tiempo LIKE %s ",
                      (f"%{kw}%", f"%{kw}%"))
        else:
            c.execute(q)
        rows = []
        for r in c.fetchall():
            rows.append((
                r[0],
                self._label_from_map(self.viaje_map, r[1]),
                r[2],
                r[3],
                r[4] if r[4] is not None else "",
                r[5],
                r[6] or "",
            ))
        conn.close()
        return rows
