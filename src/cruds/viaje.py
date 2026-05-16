"""
CRUD para Viajes
"""

from tkinter import messagebox
from .base import CRUDBase, styled_entry, styled_label, styled_combo
from database.conecction import get_conn


class CRUDViaje(CRUDBase):
    TITLE       = "GESTIÓN DE VIAJES"
    TABLE       = "VIAJE"
    PK          = "id_viaje"
    COLUMNS     = ("ID","Vehículo","Conductor","Ruta","Tarifa","Carga","Peso","Salida","Llegada Est.","Flete","Estado")
    COL_WIDTHS  = {"ID":50,"Vehículo":120,"Conductor":150,"Ruta":140,
                   "Tarifa":140,"Carga":120,"Peso":70,"Salida":140,
                   "Llegada Est.":140,"Flete":100,"Estado":110}
    FIELD_NAMES = ("id_vehiculo","id_conductor","id_ruta","id_tarifa",
                   "tipo_carga","peso_kg","fecha_salida","fecha_llegada_estimada",
                   "valor_flete","estado","observaciones")

    def build_form(self, p):
        styled_label(p, "Vehículo*").grid(row=0, column=0, sticky="w", pady=3)
        self.veh_cb = styled_combo(p, self._load_vehiculo_options(), width=26)
        self.veh_cb.grid(row=0, column=1, pady=3, padx=(6,0))
        if self.veh_cb['values']:
            self.veh_cb.set(self.veh_cb['values'][0])

        styled_label(p, "Conductor*").grid(row=1, column=0, sticky="w", pady=3)
        self.cond_cb = styled_combo(p, self._load_conductor_options(), width=26)
        self.cond_cb.grid(row=1, column=1, pady=3, padx=(6,0))
        if self.cond_cb['values']:
            self.cond_cb.set(self.cond_cb['values'][0])

        styled_label(p, "Ruta*").grid(row=2, column=0, sticky="w", pady=3)
        self.ruta_cb = styled_combo(p, self._load_route_options(), width=26)
        self.ruta_cb.grid(row=2, column=1, pady=3, padx=(6,0))
        if self.ruta_cb['values']:
            self.ruta_cb.set(self.ruta_cb['values'][0])

        styled_label(p, "Tarifa*").grid(row=3, column=0, sticky="w", pady=3)
        self.tarifa_cb = styled_combo(p, [], width=26)
        self.tarifa_cb.grid(row=3, column=1, pady=3, padx=(6,0))
        self.ruta_cb.bind("<<ComboboxSelected>>", lambda e: self._reload_tarifa_options())
        self._reload_tarifa_options()

        fields = [
            ("Tipo de carga*", "tipo"),
            ("Peso (kg)*", "peso"),
            ("Fecha salida*", "salida"),
            ("Fecha llegada est.*", "llegada"),
            ("Observaciones", "obs"),
        ]
        self.vars = {}
        for i, (lbl, key) in enumerate(fields, start=4):
            styled_label(p, lbl).grid(row=i, column=0, sticky="w", pady=3)
            e = styled_entry(p, width=28)
            e.grid(row=i, column=1, pady=3, padx=(6,0))
            self.vars[key] = e

        styled_label(p, "Estado*").grid(row=len(fields)+4, column=0, sticky="w", pady=3)
        self.est_cb = styled_combo(p, ["programado","en_curso","completado","cancelado"], width=26)
        self.est_cb.grid(row=len(fields)+4, column=1, pady=3, padx=(6,0))
        self.est_cb.set("programado")

    def _load_vehiculo_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_vehiculo, placa, marca FROM VEHICULO WHERE estado = 'disponible'")
        rows = c.fetchall()
        conn.close()
        self.vehicle_map = {f"{r[0]} - {r[1]} ({r[2]})": r[0] for r in rows}
        return list(self.vehicle_map.keys())

    def _load_conductor_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_conductor, nombre, apellido FROM CONDUCTOR WHERE estado = 'activo'")
        rows = c.fetchall()
        conn.close()
        self.conductor_map = {f"{r[0]} - {r[1]} {r[2]}": r[0] for r in rows}
        return list(self.conductor_map.keys())

    def _load_route_options(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id_ruta, nombre FROM RUTA WHERE estado = 'activa'")
        rows = c.fetchall()
        conn.close()
        self.route_map = {f"{r[0]} - {r[1]}": r[0] for r in rows}
        return list(self.route_map.keys())

    def _load_tarifa_options(self):
        route_id = self._selected_route_id()
        if route_id is None:
            self.tarifa_cb['values'] = []
            self.tarifa_map = {}
            return
        conn = get_conn()
        c = conn.cursor()
        c.execute(
            "SELECT t.id_tarifa, t.nombre, t.tipo_calculo, t.valor_base, t.valor_por_km, "
            "t.valor_por_kg, r.distancia_km "
            "FROM TARIFA t JOIN RUTA r ON t.id_ruta = r.id_ruta "
            "WHERE t.id_ruta = %s AND t.estado = 'activa' AND CURRENT_DATE() BETWEEN t.vigente_desde AND t.vigente_hasta",
            (route_id,)
        )
        rows = c.fetchall()
        conn.close()
        self.tarifa_map = {
            f"{r[0]} - {r[1]} ({r[2]})": {
                "id": r[0],
                "tipo": r[2],
                "base": float(r[3]),
                "por_km": float(r[4]),
                "por_kg": float(r[5]),
                "distancia": float(r[6])
            }
            for r in rows
        }
        values = list(self.tarifa_map.keys())
        self.tarifa_cb['values'] = values
        if values:
            self.tarifa_cb.set(values[0])

    def _reload_tarifa_options(self):
        self._load_tarifa_options()

    def _selected_vehicle_id(self):
        return self.vehicle_map.get(self.veh_cb.get())

    def _selected_conductor_id(self):
        return self.conductor_map.get(self.cond_cb.get())

    def _selected_route_id(self):
        return self.route_map.get(self.ruta_cb.get())

    def _selected_tarifa(self):
        return self.tarifa_map.get(self.tarifa_cb.get())

    def _calculate_valor(self, tarifa):
        try:
            peso = float(self.vars["peso"].get().strip())
        except ValueError:
            return None
        tipo = tarifa["tipo"]
        if tipo == "fijo":
            return tarifa["base"]
        if tipo == "por_km":
            return tarifa["por_km"] * tarifa["distancia"]
        if tipo == "por_kg":
            return tarifa["por_kg"] * peso
        return tarifa["base"] + tarifa["por_km"] * tarifa["distancia"] + tarifa["por_kg"] * peso

    def get_form_values(self):
        vehiculo_id = self._selected_vehicle_id()
        if vehiculo_id is None:
            messagebox.showwarning("Campo requerido", "Selecciona un vehículo disponible.")
            return None
        conductor_id = self._selected_conductor_id()
        if conductor_id is None:
            messagebox.showwarning("Campo requerido", "Selecciona un conductor activo.")
            return None
        ruta_id = self._selected_route_id()
        if ruta_id is None:
            messagebox.showwarning("Campo requerido", "Selecciona una ruta activa.")
            return None
        tarifa = self._selected_tarifa()
        if tarifa is None:
            messagebox.showwarning("Campo requerido", "Selecciona una tarifa vigente para la ruta.")
            return None
        tipo = self.vars["tipo"].get().strip()
        if not tipo:
            messagebox.showwarning("Campo requerido", "Tipo de carga es obligatorio.")
            return None
        try:
            peso = float(self.vars["peso"].get().strip())
        except ValueError:
            messagebox.showwarning("Formato", "Peso debe ser un número.")
            return None
        if peso <= 0:
            messagebox.showwarning("Validación", "Peso debe ser mayor que cero.")
            return None
        salida = self.vars["salida"].get().strip()
        llegada = self.vars["llegada"].get().strip()
        if not salida or not llegada:
            messagebox.showwarning("Campo requerido", "Fechas de salida y llegada estimada son obligatorias.")
            return None
        if llegada <= salida:
            messagebox.showwarning("Validación", "La fecha de llegada estimada debe ser posterior a la salida.")
            return None
        valor = self._calculate_valor(tarifa)
        if valor is None:
            messagebox.showwarning("Cálculo", "No se pudo calcular el valor del flete.")
            return None
        return (vehiculo_id, conductor_id, ruta_id, tarifa["id"],
                tipo, peso, salida, llegada, valor, self.est_cb.get(),
                self.vars["obs"].get().strip())

    def set_form_values(self, record):
        veh_key = next((k for k, v in self.vehicle_map.items() if v == record[0]), None)
        if veh_key:
            self.veh_cb.set(veh_key)
        cond_key = next((k for k, v in self.conductor_map.items() if v == record[1]), None)
        if cond_key:
            self.cond_cb.set(cond_key)
        route_key = next((k for k, v in self.route_map.items() if v == record[2]), None)
        if route_key:
            self.ruta_cb.set(route_key)
        self._reload_tarifa_options()
        tarifa_key = next((k for k, v in self.tarifa_map.items() if v["id"] == record[3]), None)
        if tarifa_key:
            self.tarifa_cb.set(tarifa_key)
        self.vars["tipo"].delete(0, "end")
        self.vars["tipo"].insert(0, record[4])
        self.vars["peso"].delete(0, "end")
        self.vars["peso"].insert(0, record[5])
        self.vars["salida"].delete(0, "end")
        self.vars["salida"].insert(0, record[6])
        self.vars["llegada"].delete(0, "end")
        self.vars["llegada"].insert(0, record[7])
        self.est_cb.set(record[8])
        self.vars["obs"].delete(0, "end")
        self.vars["obs"].insert(0, record[9] or "")

    def _on_select(self, _event=None):
        sel = self.tv.selection()
        if sel:
            row = self.tv.item(sel[0])["values"]
            self._load_record_by_id(row[0])

    def _load_record_by_id(self, id_viaje):
        conn = get_conn()
        c = conn.cursor()
        c.execute(
            "SELECT id_vehiculo, id_conductor, id_ruta, id_tarifa, tipo_carga, peso_kg, "
            "fecha_salida, fecha_llegada_estimada, estado, observaciones "
            "FROM VIAJE WHERE id_viaje = %s", (id_viaje,)
        )
        record = c.fetchone()
        conn.close()
        if record:
            self.set_form_values(record)

    def clear_form(self):
        if self.veh_cb['values']:
            self.veh_cb.set(self.veh_cb['values'][0])
        if self.cond_cb['values']:
            self.cond_cb.set(self.cond_cb['values'][0])
        if self.ruta_cb['values']:
            self.ruta_cb.set(self.ruta_cb['values'][0])
        self._reload_tarifa_options()
        for key in ["tipo","peso","salida","llegada","obs"]:
            self.vars[key].delete(0, "end")
        self.est_cb.set("programado")

    def db_read(self, kw=""):
        conn = get_conn()
        c = conn.cursor()
        q = ("SELECT v.id_viaje, CONCAT(vh.id_vehiculo, ' - ', vh.placa, ' (', vh.marca, ')'), "
             "CONCAT(c.id_conductor, ' - ', c.nombre, ' ', c.apellido), "
             "CONCAT(r.id_ruta, ' - ', r.nombre), "
             "CONCAT(t.id_tarifa, ' - ', t.nombre, ' (', t.tipo_calculo, ')'), "
             "v.tipo_carga, v.peso_kg, v.fecha_salida, v.fecha_llegada_estimada, v.valor_flete, v.estado "
             "FROM VIAJE v "
             "JOIN VEHICULO vh ON v.id_vehiculo = vh.id_vehiculo "
             "JOIN CONDUCTOR c ON v.id_conductor = c.id_conductor "
             "JOIN RUTA r ON v.id_ruta = r.id_ruta "
             "JOIN TARIFA t ON v.id_tarifa = t.id_tarifa")
        if kw:
            c.execute(q + " WHERE v.tipo_carga LIKE %s OR v.estado LIKE %s", (f"%{kw}%", f"%{kw}%"))
        else:
            c.execute(q)
        rows = c.fetchall()
        conn.close()
        return rows
