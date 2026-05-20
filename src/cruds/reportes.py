"""
Reportes para RUTECH
"""

import csv
import importlib
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from datetime import datetime

FigureCanvasTkAgg = None
Figure = None
MPL_AVAILABLE = False

try:
    mpl_tkagg = importlib.import_module("matplotlib.backends.backend_tkagg")
    mpl_figure = importlib.import_module("matplotlib.figure")
    FigureCanvasTkAgg = mpl_tkagg.FigureCanvasTkAgg
    Figure = mpl_figure.Figure
    MPL_AVAILABLE = True
except ImportError:
    MPL_AVAILABLE = False

from .base import (
    BG,
    BG2,
    BG3,
    ACCENT,
    TEXT,
    TEXT_DIM,
    FONT_BODY,
    FONT_SM,
    make_treeview,
    STYLE_BTN,
    STYLE_BTN2,
    STYLE_BTN4,
)
from database.conecction import get_conn


class CRUDReportes(tk.Frame):
    TITLE = "REPORTES"

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG, **kw)
        self.current_report = None
        self.current_columns = []
        self.current_rows = []
        self.figure = None
        self.canvas = None
        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self, bg=ACCENT, pady=10)
        header.pack(fill="x")
        tk.Label(header, text="  ▸  REPORTES", bg=ACCENT, fg="white",
                 font=("Courier New", 15, "bold")).pack(side="left")

        body = tk.Frame(self, bg=BG2)
        body.pack(fill="both", expand=True, padx=16, pady=12)

        nav = tk.LabelFrame(body, text=" Reportes ", bg=BG2, fg=ACCENT,
                            font=FONT_SM, bd=1, relief="ridge", padx=12, pady=8)
        nav.grid(row=0, column=0, sticky="nsw", padx=(0,16), pady=(0,12))

        self.output = tk.LabelFrame(body, text=" Resultado ", bg=BG2, fg=ACCENT,
                                    font=FONT_SM, bd=1, relief="ridge", padx=12, pady=8)
        self.output.grid(row=0, column=1, sticky="nsew")
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        tk.Button(nav, text="1) Facturas pendientes", **STYLE_BTN,
                  command=self._report_facturas_pendientes).pack(fill="x", pady=3)
        tk.Button(nav, text="2) Pagos recientes", **STYLE_BTN,
                  command=self._report_pagos_recientes).pack(fill="x", pady=3)
        tk.Button(nav, text="3) Conductores con viajes activos", **STYLE_BTN,
                  command=self._report_conductores_viajes_activos).pack(fill="x", pady=3)

        tk.Label(nav, text="Intermedios", bg=BG2, fg=TEXT, font=("Courier New", 11, "bold")).pack(pady=(12,2), anchor="w")
        tk.Button(nav, text="4) Facturación por cliente", **STYLE_BTN,
                  command=self._report_facturacion_por_cliente).pack(fill="x", pady=3)
        tk.Button(nav, text="5) Pagos por método", **STYLE_BTN,
                  command=self._report_pagos_por_metodo).pack(fill="x", pady=3)
        tk.Button(nav, text="6) Viajes por ruta", **STYLE_BTN,
                  command=self._report_viajes_por_ruta).pack(fill="x", pady=3)
        tk.Button(nav, text="7) Mantenimientos por vehículo", **STYLE_BTN,
                  command=self._report_mantenimientos_por_vehiculo).pack(fill="x", pady=3)

        tk.Label(nav, text="Complejos", bg=BG2, fg=TEXT, font=("Courier New", 11, "bold")).pack(pady=(12,2), anchor="w")
        tk.Button(nav, text="8) Facturación mensual", **STYLE_BTN,
                  command=self._report_facturacion_mensual).pack(fill="x", pady=3)
        tk.Button(nav, text="9) Estado de facturas", **STYLE_BTN,
                  command=self._report_estado_facturas).pack(fill="x", pady=3)
        tk.Button(nav, text="10) Notificaciones por tipo", **STYLE_BTN,
                  command=self._report_notificaciones_tipo).pack(fill="x", pady=3)

        controls = tk.Frame(self.output, bg=BG2)
        controls.pack(fill="x", pady=(0,10))
        self.report_title = tk.Label(controls, text="Seleccione un reporte", bg=BG2, fg=TEXT,
                                     font=("Courier New", 13, "bold"))
        self.report_title.pack(side="left", anchor="w")

        btn_bar = tk.Frame(controls, bg=BG2)
        btn_bar.pack(side="right")
        tk.Button(btn_bar, text="Exportar CSV", **STYLE_BTN4,
                  command=self._export_csv).pack(side="left", padx=(0,6))
        self.save_chart_btn = tk.Button(btn_bar, text="Guardar gráfica", **STYLE_BTN2,
                                        command=self._save_chart)
        self.save_chart_btn.pack(side="left")
        if not MPL_AVAILABLE:
            self.save_chart_btn.config(state="disabled")
            tk.Label(self.output, text="Instala matplotlib para ver y guardar gráficos.",
                     bg=BG2, fg=TEXT_DIM, font=FONT_SM).pack(anchor="w", pady=(0,8))

        self.table_frame, self.tree = make_treeview(self.output, [])
        self.table_frame.pack(fill="both", expand=True)

        self.chart_frame = tk.Frame(self.output, bg=BG2, height=240)
        self.chart_frame.pack(fill="both", expand=False, pady=(12,0))

    def _load_table(self, columns, rows):
        self.current_columns = columns
        self.current_rows = rows
        for col in self.tree["columns"]:
            self.tree.heading(col, text="")
            self.tree.column(col, width=100)
        self.tree.configure(columns=columns)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="center")
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", "end", values=row)

    def _clear_chart(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
            self.figure = None

    def _wrap_label(self, s, max_len=18):
        """Return a label possibly split with newlines to fit max_len per line."""
        import textwrap
        s = str(s)
        # use textwrap to split into chunks without breaking words when possible
        parts = textwrap.wrap(s, width=max_len)
        if not parts:
            return s
        return "\n".join(parts)
    def _render_chart(self, title, x, y, kind="bar"):
        self._clear_chart()
        if not MPL_AVAILABLE:
            return

        n = max(1, len(x))
        # adaptative width/height: more items -> wider figure
        width = max(6, min(20, 0.6 * n))
        height = 3.0 if n <= 8 else min(8, 2.5 + n * 0.12)
        fig = Figure(figsize=(width, height), dpi=100)
        ax = fig.add_subplot(111)

        # prepare display labels (wrapped into multiple lines)
        disp_x = [self._wrap_label(xx, max_len=18) for xx in x]

        if kind == "line":
            ax.plot(range(n), y, marker="o", color=ACCENT)
            ax.set_xticks(range(n))
            ax.set_xticklabels(disp_x, rotation=0, ha="center", fontsize=9)
        else:
            ax.bar(range(n), y, color=ACCENT)
            ax.set_xticks(range(n))
            ax.set_xticklabels(disp_x, rotation=0, ha="center", fontsize=9)

        ax.set_title(title, color=TEXT)
        ax.set_facecolor(BG3)
        fig.patch.set_facecolor(BG2)
        for spine in ax.spines.values():
            spine.set_color(TEXT_DIM)
        ax.tick_params(colors=TEXT, labelcolor=TEXT)
        ax.xaxis.label.set_color(TEXT)
        ax.yaxis.label.set_color(TEXT)

        # ensure labels wrap and are readable without diagonal rotation
        # center-align and increase bottom margin if needed
        if n > 6:
            try:
                fig.subplots_adjust(bottom=0.28)
            except Exception:
                pass

        # adjust layout so labels don't overlap
        try:
            fig.tight_layout()
        except Exception:
            fig.subplots_adjust(bottom=0.25)

        self.figure = fig
        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _export_csv(self):
        if not self.current_rows or not self.current_columns:
            messagebox.showwarning("Exportar", "No hay datos para exportar.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Guardar reporte como"
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self.current_columns)
                writer.writerows(self.current_rows)
            messagebox.showinfo("Exportado", f"Reporte guardado en:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _save_chart(self):
        if not MPL_AVAILABLE:
            messagebox.showwarning("Guardar gráfica", "Matplotlib no está instalado.")
            return
        if not self.figure:
            messagebox.showwarning("Guardar gráfica", "No hay gráfica disponible.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg;*.jpeg"), ("All files", "*.*")],
            title="Guardar gráfica como"
        )
        if not path:
            return
        try:
            self.figure.savefig(path, facecolor=self.figure.get_facecolor())
            messagebox.showinfo("Guardado", f"Gráfica guardada en:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _run_query(self, query, params=(), columns=None):
        conn = get_conn()
        c = conn.cursor()
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()
        return rows if columns is None else rows

    def _report_facturas_pendientes(self):
        self.report_title.config(text="Facturas pendientes")
        query = (
            "SELECT f.numero_factura, c.nombre_razon_social, f.fecha_emision, f.fecha_vencimiento, f.total, f.estado "
            "FROM FACTURA f JOIN CLIENTE c ON f.id_cliente = c.id_cliente "
            "WHERE f.estado = 'pendiente' ORDER BY f.fecha_vencimiento"
        )
        rows = self._run_query(query)
        self._load_table(["Factura", "Cliente", "Emisión", "Vencimiento", "Total", "Estado"], rows)
        self._clear_chart()
        self.current_report = "facturas_pendientes"

    def _report_pagos_recientes(self):
        self.report_title.config(text="Pagos recientes")
        query = (
            "SELECT p.id_pago, f.numero_factura, p.fecha_pago, p.monto, p.metodo, p.estado, IFNULL(u.nombre_usuario, 'Ninguno') "
            "FROM PAGO p "
            "JOIN FACTURA f ON p.id_factura = f.id_factura "
            "LEFT JOIN USUARIO u ON p.creado_por = u.id_usuario "
            "WHERE p.fecha_pago >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY) "
            "ORDER BY p.fecha_pago DESC"
        )
        rows = self._run_query(query)
        self._load_table(["Pago", "Factura", "Fecha", "Monto", "Método", "Estado", "Creado por"], rows)
        self._clear_chart()
        self.current_report = "pagos_recientes"

    def _report_conductores_viajes_activos(self):
        self.report_title.config(text="Conductores con viajes activos")
        query = (
            "SELECT CONCAT(c.id_conductor, ' - ', c.nombre_completo), COUNT(v.id_viaje), "
            "GROUP_CONCAT(DISTINCT v.estado ORDER BY v.estado SEPARATOR ', ') "
            "FROM VIAJE v JOIN CONDUCTOR c ON v.id_conductor = c.id_conductor "
            "WHERE v.estado IN ('programado','en_curso') "
            "GROUP BY c.id_conductor "
            "ORDER BY COUNT(v.id_viaje) DESC"
        )
        rows = self._run_query(query)
        self._load_table(["Conductor", "Viajes activos", "Estados"], rows)
        self._clear_chart()
        self.current_report = "conductores_viajes_activos"

    def _report_facturacion_por_cliente(self):
        self.report_title.config(text="Facturación por cliente")
        query = (
            "SELECT CONCAT(c.id_cliente, ' - ', c.nombre_razon_social), COUNT(f.id_factura), SUM(f.total), SUM(CASE WHEN f.estado = 'pendiente' THEN f.total ELSE 0 END) "
            "FROM FACTURA f JOIN CLIENTE c ON f.id_cliente = c.id_cliente "
            "GROUP BY c.id_cliente "
            "ORDER BY SUM(f.total) DESC"
        )
        rows = self._run_query(query)
        self._load_table(["Cliente", "Facturas", "Total facturado", "Pendiente"], rows)
        self._render_chart(
            "Facturación por cliente",
            [r[0] for r in rows],
            [float(r[2]) for r in rows],
            kind="bar"
        )
        self.current_report = "facturacion_por_cliente"

    def _report_pagos_por_metodo(self):
        self.report_title.config(text="Pagos por método")
        query = (
            "SELECT p.metodo, COUNT(p.id_pago), SUM(p.monto) "
            "FROM PAGO p "
            "GROUP BY p.metodo "
            "ORDER BY COUNT(p.id_pago) DESC"
        )
        rows = self._run_query(query)
        self._load_table(["Método", "Cantidad", "Total"], rows)
        self._render_chart(
            "Pagos por método",
            [r[0] for r in rows],
            [float(r[2]) for r in rows],
            kind="bar"
        )
        self.current_report = "pagos_por_metodo"

    def _report_viajes_por_ruta(self):
        self.report_title.config(text="Viajes por ruta")
        query = (
            "SELECT CONCAT(r.id_ruta, ' - ', r.origen, ' → ', r.destino), COUNT(v.id_viaje), SUM(v.valor_flete), "
            "AVG(TIMESTAMPDIFF(HOUR, v.fecha_salida, v.fecha_llegada)) "
            "FROM VIAJE v JOIN RUTA r ON v.id_ruta = r.id_ruta "
            "GROUP BY r.id_ruta "
            "ORDER BY COUNT(v.id_viaje) DESC"
        )
        rows = self._run_query(query)
        self._load_table(["Ruta", "Viajes", "Total flete", "Duración promedio (h)"], rows)
        self._render_chart(
            "Viajes por ruta",
            [r[0] for r in rows],
            [float(r[1]) for r in rows],
            kind="bar"
        )
        self.current_report = "viajes_por_ruta"

    def _report_mantenimientos_por_vehiculo(self):
        self.report_title.config(text="Mantenimientos por vehículo")
        query = (
            "SELECT CONCAT(v.id_vehiculo, ' - ', v.placa), COUNT(m.id_mantenimiento), SUM(m.costo) "
            "FROM MANTENIMIENTO m JOIN VEHICULO v ON m.id_vehiculo = v.id_vehiculo "
            "GROUP BY v.id_vehiculo "
            "ORDER BY SUM(m.costo) DESC"
        )
        rows = self._run_query(query)
        self._load_table(["Vehículo", "Cantidad", "Costo total"], rows)
        self._render_chart(
            "Mantenimientos por vehículo",
            [r[0] for r in rows],
            [float(r[2]) for r in rows],
            kind="bar"
        )
        self.current_report = "mantenimientos_por_vehiculo"

    def _report_facturacion_mensual(self):
        self.report_title.config(text="Facturación mensual")
        query = (
            "SELECT YEAR(f.fecha_emision), MONTH(f.fecha_emision), SUM(f.total) "
            "FROM FACTURA f "
            "GROUP BY YEAR(f.fecha_emision), MONTH(f.fecha_emision) "
            "ORDER BY YEAR(f.fecha_emision), MONTH(f.fecha_emision)"
        )
        rows = self._run_query(query)
        labels = [f"{int(r[0])}-{int(r[1]):02d}" for r in rows]
        values = [float(r[2]) for r in rows]
        self._load_table(["Año", "Mes", "Total facturado"], rows)
        self._render_chart("Facturación mensual", labels, values, kind="line")
        self.current_report = "facturacion_mensual"

    def _report_estado_facturas(self):
        self.report_title.config(text="Estado de facturas")
        query = (
            "SELECT f.estado, COUNT(f.id_factura), SUM(f.total) "
            "FROM FACTURA f "
            "GROUP BY f.estado "
            "ORDER BY FIELD(f.estado, 'pendiente', 'pagada', 'vencida', 'anulada')"
        )
        rows = self._run_query(query)
        self._load_table(["Estado", "Cantidad", "Total"], rows)
        self._render_chart(
            "Estado de facturas",
            [r[0] for r in rows],
            [float(r[1]) for r in rows],
            kind="bar"
        )
        self.current_report = "estado_facturas"

    def _report_notificaciones_tipo(self):
        self.report_title.config(text="Notificaciones por tipo")
        query = (
            "SELECT n.tipo, COUNT(n.id_notificacion), SUM(CASE WHEN n.leida = FALSE THEN 1 ELSE 0 END) "
            "FROM NOTIFICACION n "
            "GROUP BY n.tipo "
            "ORDER BY COUNT(n.id_notificacion) DESC"
        )
        rows = self._run_query(query)
        self._load_table(["Tipo", "Cantidad", "No leídas"], rows)
        self._render_chart(
            "Notificaciones por tipo",
            [r[0] for r in rows],
            [float(r[1]) for r in rows],
            kind="bar"
        )
        self.current_report = "notificaciones_tipo"
