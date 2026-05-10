USE rutech;

-- =====================================================
-- RUTA
-- =====================================================
INSERT INTO RUTA (nombre, origen, destino, distancia_km, estado) VALUES
('Ruta Cafetera', 'Armenia', 'Pereira', 45.5, 'activa'),
('Ruta Pacífica', 'Cali', 'Buenaventura', 115.0, 'activa'),
('Ruta Andina', 'Bogotá', 'Medellín', 420.0, 'activa'),
('Ruta Caribe', 'Barranquilla', 'Cartagena', 120.0, 'activa'),
('Ruta Sur', 'Pasto', 'Ipiales', 90.0, 'inactiva');

-- =====================================================
-- TARIFA
-- =====================================================
INSERT INTO TARIFA (id_ruta, nombre, tipo_calculo, valor_base, valor_por_km, valor_por_kg, vigente_desde, vigente_hasta, estado) VALUES
(1, 'Tarifa Básica', 'fijo', 150000, 0, 0, '2026-01-01', '2026-12-31', 'activa'),
(2, 'Tarifa Pacífica', 'por_km', 50000, 2000, 0, '2026-01-01', '2026-12-31', 'activa'),
(3, 'Tarifa Nacional', 'mixto', 100000, 1500, 300, '2026-01-01', '2026-12-31', 'activa'),
(4, 'Tarifa Caribe', 'por_kg', 30000, 0, 500, '2026-01-01', '2026-12-31', 'activa'),
(5, 'Tarifa Sur', 'fijo', 80000, 0, 0, '2026-01-01', '2026-12-31', 'inactiva');

-- =====================================================
-- CONDUCTOR
-- =====================================================
INSERT INTO CONDUCTOR (cedula, nombre, apellido, telefono, num_licencia, categoria_licencia, fecha_venc_licencia, estado) VALUES
('1001', 'Carlos', 'Ramírez', '3101111111', 'LIC001', 'C2', '2028-01-10', 'activo'),
('1002', 'Andrés', 'López', '3102222222', 'LIC002', 'C3', '2027-05-12', 'activo'),
('1003', 'Miguel', 'Torres', '3103333333', 'LIC003', 'B2', '2029-03-15', 'activo'),
('1004', 'Juan', 'Gómez', '3104444444', 'LIC004', 'C1', '2027-08-20', 'suspendido'),
('1005', 'Pedro', 'Martínez', '3105555555', 'LIC005', 'C2', '2028-11-01', 'activo');

-- =====================================================
-- VEHICULO
-- =====================================================
INSERT INTO VEHICULO (placa, marca, modelo, anio, tipo, kilometraje_actual, estado) VALUES
('ABC123', 'Chevrolet', 'NHR', 2020, 'camion', 120000, 'disponible'),
('DEF456', 'Hino', '300', 2021, 'camion', 90000, 'en_viaje'),
('GHI789', 'Renault', 'Master', 2019, 'furgon', 150000, 'en_mantenimiento'),
('JKL321', 'Ford', 'Transit', 2022, 'van', 40000, 'disponible'),
('MNO654', 'Isuzu', 'FRR', 2018, 'camion', 200000, 'inactivo');

-- =====================================================
-- CLIENTE
-- =====================================================
INSERT INTO CLIENTE (tipo_persona, documento, nombre_razon_social, correo, telefono, ciudad, estado) VALUES
('juridica', '900111222', 'Café Andino SAS', 'contacto@cafe.com', '3111111111', 'Armenia', 'activo'),
('natural', '12345678', 'Luis Pérez', 'luis@gmail.com', '3222222222', 'Pereira', 'activo'),
('juridica', '900333444', 'Textiles del Quindío', 'ventas@textiles.com', '3333333333', 'Cali', 'activo'),
('natural', '87654321', 'María Gómez', 'maria@gmail.com', '3444444444', 'Bogotá', 'activo'),
('juridica', '900555666', 'Logística Express', 'info@logistica.com', '3555555555', 'Medellín', 'inactivo');

-- =====================================================
-- PROVEEDOR
-- =====================================================
INSERT INTO PROVEEDOR (nit, nombre, tipo, telefono, ciudad, estado) VALUES
('800111222', 'Taller Motor SAS', 'taller', '3001111111', 'Armenia', 'activo'),
('800222333', 'Terpel Norte', 'gasolinera', '3002222222', 'Pereira', 'activo'),
('800333444', 'Repuestos Quindío', 'distribuidor_repuestos', '3003333333', 'Cali', 'activo'),
('800444555', 'Lubricantes SA', 'otro', '3004444444', 'Bogotá', 'activo'),
('800555666', 'Taller Diesel', 'taller', '3005555555', 'Medellín', 'inactivo');

-- =====================================================
-- USUARIO
-- =====================================================
INSERT INTO USUARIO (nombre_usuario, contrasena_hash, rol, correo, nombre_completo, estado, id_conductor, id_cliente) VALUES
('admin1', '12345', 'admin', 'admin1@gmail.com', 'Administrador Uno', 'activo', NULL, NULL),
('coord1', '12345', 'coordinador', 'coord@gmail.com', 'Coordinador General', 'activo', NULL, NULL),
('cond1', '12345', 'conductor', 'cond1@gmail.com', 'Carlos Ramírez', 'activo', 1, NULL),
('cliente1', '12345', 'cliente', 'cliente1@gmail.com', 'Luis Pérez', 'activo', NULL, 2),
('tecnico1', '12345', 'tecnico', 'tec@gmail.com', 'Tecnico Principal', 'activo', NULL, NULL);

-- =====================================================
-- CONTRATO
-- =====================================================
INSERT INTO CONTRATO (id_proveedor, fecha_inicio, fecha_fin, valor, tipo_servicio, estado, creado_por) VALUES
(1, '2026-01-01', '2026-12-31', 5000000, 'Mantenimiento', 'vigente', 1),
(2, '2026-01-01', '2026-12-31', 8000000, 'Combustible', 'vigente', 1),
(3, '2026-02-01', '2026-11-30', 3000000, 'Repuestos', 'vigente', 2),
(4, '2026-03-01', '2026-09-30', 2000000, 'Lubricantes', 'vigente', 2),
(5, '2026-01-01', '2026-06-30', 4000000, 'Mantenimiento Diesel', 'cancelado', 1);

-- =====================================================
-- DOCUMENTO_CONDUCTOR
-- =====================================================
INSERT INTO DOCUMENTO_CONDUCTOR (id_conductor, tipo, numero, fecha_emision, fecha_vencimiento, estado) VALUES
(1, 'licencia', 'DOC001', '2025-01-01', '2028-01-01', 'vigente'),
(2, 'licencia', 'DOC002', '2025-02-01', '2027-02-01', 'vigente'),
(3, 'examen_medico', 'DOC003', '2025-03-01', '2026-03-01', 'por_vencer'),
(4, 'certificado', 'DOC004', '2025-04-01', '2026-04-01', 'vigente'),
(5, 'licencia', 'DOC005', '2025-05-01', '2028-05-01', 'vigente');

-- =====================================================
-- DOCUMENTO_VEHICULO
-- =====================================================
INSERT INTO DOCUMENTO_VEHICULO (id_vehiculo, tipo, numero, fecha_emision, fecha_vencimiento, estado) VALUES
(1, 'soat', 'SOAT001', '2025-01-01', '2026-01-01', 'vigente'),
(2, 'tecnomecanica', 'TEC002', '2025-02-01', '2026-02-01', 'vigente'),
(3, 'seguro', 'SEG003', '2025-03-01', '2026-03-01', 'vigente'),
(4, 'soat', 'SOAT004', '2025-04-01', '2026-04-01', 'vigente'),
(5, 'tarjeta_propiedad', 'TP005', '2025-05-01', '2030-05-01', 'vigente');

-- =====================================================
-- VIAJE
-- =====================================================
INSERT INTO VIAJE (id_vehiculo, id_conductor, id_ruta, id_tarifa, tipo_carga, peso_kg, fecha_salida, fecha_llegada_estimada, valor_flete, estado, creado_por) VALUES
(1,1,1,1,'Alimentos',500,'2026-05-01 08:00:00','2026-05-01 12:00:00',150000,'programado',1),
(2,2,2,2,'Electrodomésticos',1200,'2026-05-02 07:00:00','2026-05-02 16:00:00',300000,'en_curso',2),
(3,3,3,3,'Textiles',900,'2026-05-03 06:00:00','2026-05-03 18:00:00',450000,'programado',1),
(4,4,4,4,'Medicamentos',300,'2026-05-04 09:00:00','2026-05-04 14:00:00',200000,'completado',2),
(5,5,5,5,'Muebles',1500,'2026-05-05 05:00:00','2026-05-05 20:00:00',500000,'cancelado',1);

-- =====================================================
-- ENVIO
-- =====================================================
INSERT INTO ENVIO (id_cliente, id_viaje, direccion_origen, direccion_destino, descripcion, estado, creado_por) VALUES
(1,1,'Armenia Centro','Pereira Norte','Carga de café','pendiente',1),
(2,2,'Cali Sur','Buenaventura Puerto','Electrodomésticos','en_transito',2),
(3,3,'Bogotá Norte','Medellín Centro','Textiles varios','pendiente',1),
(4,4,'Barranquilla','Cartagena','Medicamentos','entregado',2),
(5,5,'Pasto','Ipiales','Muebles hogar','cancelado',1);

-- =====================================================
-- DETALLE_ENVIO
-- =====================================================
INSERT INTO DETALLE_ENVIO (id_envio, descripcion_mercancia, tipo_embalaje, cantidad, peso_kg, volumen_m3, valor_declarado) VALUES
(1, 'Café premium', 'Caja', 10, 200, 1.5, 500000),
(2, 'Televisores', 'Estiba', 5, 500, 3.0, 3000000),
(3, 'Ropa importada', 'Bolsa', 20, 300, 2.0, 1500000),
(4, 'Medicamentos', 'Caja térmica', 15, 100, 1.0, 2500000),
(5, 'Muebles sala', 'Guacal', 3, 800, 5.0, 4000000);

-- =====================================================
-- MANTENIMIENTO
-- =====================================================
INSERT INTO MANTENIMIENTO (id_vehiculo, id_proveedor, tipo, fecha, kilometros, descripcion, costo, estado, creado_por) VALUES
(1,1,'preventivo','2026-04-01',120000,'Cambio de aceite',350000,'completado',1),
(2,1,'correctivo','2026-04-05',90000,'Cambio de frenos',800000,'en_proceso',2),
(3,5,'preventivo','2026-04-10',150000,'Revisión general',450000,'pendiente',1),
(4,1,'correctivo','2026-04-15',40000,'Cambio de batería',600000,'completado',2),
(5,5,'preventivo','2026-04-20',200000,'Mantenimiento motor',1200000,'cancelado',1);

-- =====================================================
-- REPUESTO_MANTENIMIENTO
-- =====================================================
INSERT INTO REPUESTO_MANTENIMIENTO (id_mantenimiento, nombre, referencia, cantidad, costo_unitario) VALUES
(1,'Filtro aceite','FA001',2,50000),
(2,'Pastillas freno','PF002',4,120000),
(3,'Aceite motor','AM003',6,45000),
(4,'Batería 12V','BAT004',1,350000),
(5,'Filtro aire','FA005',2,70000);

-- =====================================================
-- COMBUSTIBLE
-- =====================================================
INSERT INTO COMBUSTIBLE (id_vehiculo, id_proveedor, fecha, litros, precio_por_litro, km_al_recargar, km_desde_ultima_recarga, tipo_combustible, creado_por) VALUES
(1,2,'2026-05-01',50,15000,120000,500,'diesel',1),
(2,2,'2026-05-02',60,15500,90500,450,'diesel',2),
(3,2,'2026-05-03',40,14000,150500,400,'gasolina_corriente',1),
(4,2,'2026-05-04',35,14500,40500,350,'gasolina_extra',2),
(5,2,'2026-05-05',70,15000,200500,600,'diesel',1);

-- =====================================================
-- INFRACCION
-- =====================================================
INSERT INTO INFRACCION (id_conductor, id_viaje, fecha, tipo, monto, descripcion, estado_pago, autoridad) VALUES
(1,1,'2026-05-01','Exceso velocidad',500000,'Superó límite permitido','pendiente','Policía Tránsito'),
(2,2,'2026-05-02','Mal estacionamiento',200000,'Parqueo indebido','pagada','Secretaría Movilidad'),
(3,3,'2026-05-03','Documentos vencidos',350000,'Tecnomecánica vencida','pendiente','Policía Tránsito'),
(4,4,'2026-05-04','Semáforo en rojo',700000,'Cruce indebido','en_disputa','Secretaría Movilidad'),
(5,5,'2026-05-05','Sobrecupo',450000,'Exceso de carga','condonada','Policía Carreteras');

-- =====================================================
-- POSICION_GPS
-- =====================================================
INSERT INTO POSICION_GPS (id_viaje, latitud, longitud, velocidad_kmh, marca_tiempo, tipo_evento) VALUES
(1,4.533889,-75.681111,60,'2026-05-01 09:00:00','inicio'),
(2,3.451647,-76.531985,80,'2026-05-02 10:00:00','ruta'),
(3,6.244203,-75.581212,70,'2026-05-03 11:00:00','parada'),
(4,10.968540,-74.781320,50,'2026-05-04 12:00:00','desvio'),
(5,0.825000,-77.639000,40,'2026-05-05 13:00:00','fin');

-- =====================================================
-- NOVEDAD_VIAJE
-- =====================================================
INSERT INTO NOVEDAD_VIAJE (id_viaje, tipo, descripcion, fecha_hora, estado, creado_por) VALUES
(1,'demora','Tráfico pesado','2026-05-01 10:00:00','abierta',1),
(2,'averia','Falla mecánica menor','2026-05-02 11:00:00','en_gestion',2),
(3,'desvio','Cierre de vía','2026-05-03 12:00:00','cerrada',1),
(4,'accidente','Choque leve','2026-05-04 13:00:00','abierta',2),
(5,'otro','Retraso climático','2026-05-05 14:00:00','cerrada',1);

-- =====================================================
-- FACTURA
-- =====================================================
INSERT INTO FACTURA (id_viaje, id_cliente, numero_factura, fecha_emision, fecha_vencimiento, subtotal, porcentaje_iva, total, estado, creado_por) VALUES
(1,1,'FACT-2026-0001','2026-05-01','2026-05-15',150000,19,178500,'pendiente',1),
(2,2,'FACT-2026-0002','2026-05-02','2026-05-16',300000,19,357000,'pagada',2),
(3,3,'FACT-2026-0003','2026-05-03','2026-05-17',450000,19,535500,'pendiente',1),
(4,4,'FACT-2026-0004','2026-05-04','2026-05-18',200000,19,238000,'pagada',2),
(5,5,'FACT-2026-0005','2026-05-05','2026-05-19',500000,19,595000,'vencida',1);

-- =====================================================
-- DETALLE_FACTURA
-- =====================================================
INSERT INTO DETALLE_FACTURA (id_factura, id_envio, descripcion, cantidad, valor_unitario, subtotal_linea) VALUES
(1,1,'Servicio transporte café',1,150000,150000),
(2,2,'Servicio electrodomésticos',1,300000,300000),
(3,3,'Servicio textiles',1,450000,450000),
(4,4,'Servicio medicamentos',1,200000,200000),
(5,5,'Servicio muebles',1,500000,500000);

-- =====================================================
-- PAGO
-- =====================================================
INSERT INTO PAGO (id_factura, fecha_pago, monto, metodo, referencia_transaccion, estado, creado_por) VALUES
(1,'2026-05-10',178500,'transferencia','TRX001','confirmado',1),
(2,'2026-05-11',357000,'pse','TRX002','confirmado',2),
(3,'2026-05-12',535500,'efectivo','TRX003','pendiente',1),
(4,'2026-05-13',238000,'tarjeta_credito','TRX004','confirmado',2),
(5,'2026-05-14',595000,'cheque','TRX005','rechazado',1);

-- =====================================================
-- NOTIFICACION
-- =====================================================
INSERT INTO NOTIFICACION (id_usuario, tipo, mensaje, fecha_hora, leida) VALUES
(1,'pago_pendiente','Tiene un pago pendiente','2026-05-01 08:00:00',false),
(2,'mantenimiento_programado','Mantenimiento programado mañana','2026-05-02 09:00:00',true),
(3,'vencimiento_doc','Licencia próxima a vencer','2026-05-03 10:00:00',false),
(4,'viaje_asignado','Nuevo viaje asignado','2026-05-04 11:00:00',true),
(5,'factura_generada','Factura disponible','2026-05-05 12:00:00',false);