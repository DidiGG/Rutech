"""
RUTECH — Sistema de Gestión de Flotas
TransCarga Andina S.A.S. · Universidad del Quindío · Bases de Datos 1 · 2026-1

Aplicación principal con Tkinter
"""

import tkinter as tk
import sys
import os
sys.path.append(os.path.dirname(__file__))
from cruds.conductor import CRUDConductor
from cruds.vehiculo import CRUDVehiculo
from cruds.cliente import CRUDCliente
from cruds.ruta import CRUDRuta
from cruds.proveedor import CRUDProveedor
from cruds.usuario import CRUDUsuario
from cruds.tarifa import CRUDTarifa
from cruds.contrato import CRUDContrato
from cruds.documento_conductor import CRUDDocumentoConductor
from cruds.documento_vehiculo import CRUDDocumentoVehiculo
from cruds.envio import CRUDEnvio
from cruds.detalle_envio import CRUDDetalleEnvio
from cruds.posicion_gps import CRUDPosicionGPS
from cruds.mantenimiento import CRUDMantenimiento
from cruds.repuesto_mantenimiento import CRUDRepuestoMantenimiento
from cruds.combustible import CRUDCombustible
from cruds.viaje import CRUDViaje
from cruds.infraccion import CRUDInfraccion
from cruds.novedad_viaje import CRUDNovedadViaje
from cruds.factura import CRUDFactura
from cruds.detalle_factura import CRUDDetalleFactura
from cruds.pago import CRUDPago
from cruds.notificacion import CRUDNotificacion
from cruds.reportes import CRUDReportes
from cruds.base import BG, ACCENT, TEXT_DIM, FONT_BODY, FONT_SM, notify_upcoming_due_invoices

# ═════════════════════════════════════════════════════════════════════════════
#  VENTANA PRINCIPAL con navegación lateral
# ═════════════════════════════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RUTECH — Sistema de Gestión de Flotas · TransCarga Andina S.A.S.")
        self.geometry("1200x700")
        self.configure(bg=BG)
        self.resizable(True, True)
        self._build()
        try:
            notify_upcoming_due_invoices()
        except Exception:
            pass

    def _build(self):
        # Sidebar
        sidebar_container = tk.Frame(self, bg=BG, width=210)
        sidebar_container.pack(side="left", fill="y")
        sidebar_container.pack_propagate(False)

        sidebar_canvas = tk.Canvas(sidebar_container, bg=BG, highlightthickness=0)
        sidebar_canvas.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(sidebar_container, orient="vertical", command=sidebar_canvas.yview)
        scrollbar.pack(side="right", fill="y")
        sidebar_canvas.configure(yscrollcommand=scrollbar.set)

        sidebar = tk.Frame(sidebar_canvas, bg=BG)
        sidebar_canvas.create_window((0, 0), window=sidebar, anchor="nw")
        sidebar.bind("<Configure>", lambda e: sidebar_canvas.configure(scrollregion=sidebar_canvas.bbox("all")))
        sidebar_canvas.bind_all("<MouseWheel>", lambda event: sidebar_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

        # Logo / Brand
        tk.Label(sidebar, text="RUTECH", bg=BG, fg=ACCENT,
                 font=("Courier New", 20, "bold")).pack(pady=(24,2))
        tk.Label(sidebar, text="TransCarga Andina", bg=BG, fg=TEXT_DIM,
                 font=("Courier New", 8)).pack()
        tk.Frame(sidebar, bg="#23263a", height=1).pack(fill="x", padx=16, pady=16)

        # Menú
        self.pages = {}
        nav_items = [
            ("🧑‍✈️  Conductores", CRUDConductor),
            ("🚛  Vehículos",    CRUDVehiculo),
            ("🏢  Clientes",     CRUDCliente),
            ("🗺️   Rutas",        CRUDRuta),
            ("🛠️  Proveedores",   CRUDProveedor),
            ("👤  Usuarios",      CRUDUsuario),
            ("💲  Tarifas",       CRUDTarifa),
            ("📄  Contratos",     CRUDContrato),
            ("📑  Docs Conductor", CRUDDocumentoConductor),
            ("📑  Docs Vehículo",  CRUDDocumentoVehiculo),
            ("📦  Envíos",         CRUDEnvio),
            ("📋  Detalles Envío", CRUDDetalleEnvio),
            ("🚧  Mantenimientos", CRUDMantenimiento),
            ("⛽  Combustible",    CRUDCombustible),
            ("🔧  Repuestos Mantenimiento", CRUDRepuestoMantenimiento),
            ("🚚  Viajes",        CRUDViaje),
            ("🚨  Infracciones",   CRUDInfraccion),
            ("⚠️  Novedades Viaje", CRUDNovedadViaje),
            ("🧾  Facturas",      CRUDFactura),
            ("📋  Detalle Factura", CRUDDetalleFactura),
            ("💳  Pagos",         CRUDPago),
            ("🔔  Notificaciones", CRUDNotificacion),
            ("📊  Reportes",       CRUDReportes),
            ("📡  Posiciones GPS", CRUDPosicionGPS),
        ]

        self.content = tk.Frame(self, bg="#1a1d27")
        self.content.pack(side="right", fill="both", expand=True)

        self._active_btn = None
        for label, cls in nav_items:
            page = cls(self.content)
            self.pages[label] = page
            btn = tk.Button(
                sidebar, text=label, bg=BG, fg="#e8eaf6",
                font=FONT_BODY, relief="flat", anchor="w", bd=0,
                padx=18, pady=10, cursor="hand2",
                activebackground="#23263a", activeforeground=ACCENT,
                command=lambda l=label: self._show(l)
            )
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#23263a", fg=ACCENT))
            btn.bind("<Leave>", lambda e, b=btn, l=label:
                     b.config(bg=BG if l != self._current else "#23263a",
                              fg="#e8eaf6" if l != self._current else ACCENT))

        tk.Frame(sidebar, bg="#23263a", height=1).pack(fill="x", padx=16, pady=16)
        tk.Label(sidebar, text="Bases de Datos I\nUniquindío · 2026-1",
                 bg=BG, fg=TEXT_DIM, font=("Courier New", 8),
                 justify="center").pack(pady=8)

        self._current = None
        first = nav_items[0][0]
        self._show(first)

    def _show(self, label):
        self._current = label
        for name, page in self.pages.items():
            page.pack_forget()
        self.pages[label].pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()