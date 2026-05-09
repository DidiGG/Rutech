-- =============================================================================
--  RUTECH — Sistema de Gestión de Flotas y Telemática Empresarial
--  TransCarga Andina S.A.S. · Armenia, Quindío · Colombia
--  Universidad del Quindío · Bases de Datos 1 · 2026-1
--
--  DDL v3.0 — MySQL 8.x
--  Orden de creación respeta dependencias de FK
--  23 tablas 
-- =============================================================================

CREATE DATABASE IF NOT EXISTS rutech
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE rutech;

-- ─────────────────────────────────────────────────────────────────────────────
--  0. CONFIGURACIÓN GLOBAL
-- ─────────────────────────────────────────────────────────────────────────────
SET FOREIGN_KEY_CHECKS = 0;   -- se reactiva al final


-- =============================================================================
--  1. RUTA
--     No depende de ninguna otra tabla.
-- =============================================================================
CREATE TABLE RUTA (
    id_ruta        INT             NOT NULL AUTO_INCREMENT,
    nombre         VARCHAR(100)    NOT NULL,
    origen         VARCHAR(100)    NOT NULL,
    destino        VARCHAR(100)    NOT NULL,
    distancia_km   DECIMAL(8,2)    NOT NULL CHECK (distancia_km > 0),
    estado         ENUM('activa','inactiva')
                                   NOT NULL DEFAULT 'activa',
    created_at     TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                            ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_ruta PRIMARY KEY (id_ruta)
) ENGINE=InnoDB COMMENT='Rutas predefinidas origen-destino para los viajes';


-- =============================================================================
--  2. TARIFA
--     Depende de: RUTA
-- =============================================================================
CREATE TABLE TARIFA (
    id_tarifa       INT             NOT NULL AUTO_INCREMENT,
    id_ruta         INT             NOT NULL,
    nombre          VARCHAR(100)    NOT NULL,
    tipo_calculo    ENUM('fijo','por_km','por_kg','mixto')
                                    NOT NULL,
    valor_base      DECIMAL(12,2)   NOT NULL DEFAULT 0.00
                                    CHECK (valor_base >= 0),
    valor_por_km    DECIMAL(10,2)   NOT NULL DEFAULT 0.00
                                    CHECK (valor_por_km >= 0),
    valor_por_kg    DECIMAL(10,2)   NOT NULL DEFAULT 0.00
                                    CHECK (valor_por_kg >= 0),
    vigente_desde   DATE            NOT NULL,
    vigente_hasta   DATE            NOT NULL,
    estado          ENUM('activa','inactiva')
                                    NOT NULL DEFAULT 'activa',
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_tarifa       PRIMARY KEY (id_tarifa),
    CONSTRAINT fk_tarifa_ruta  FOREIGN KEY (id_ruta)
        REFERENCES RUTA(id_ruta) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT ck_tarifa_fechas
        CHECK (vigente_hasta >= vigente_desde)
) ENGINE=InnoDB COMMENT='Tarifas vigentes por ruta. Base de cálculo para valor_flete en VIAJE';

CREATE INDEX idx_tarifa_ruta   ON TARIFA(id_ruta);
CREATE INDEX idx_tarifa_fechas ON TARIFA(vigente_desde, vigente_hasta);


-- =============================================================================
--  3. CONDUCTOR
--     No depende de ninguna otra tabla.
-- =============================================================================
CREATE TABLE CONDUCTOR (
    id_conductor        INT             NOT NULL AUTO_INCREMENT,
    cedula              VARCHAR(20)     NOT NULL,
    nombre              VARCHAR(80)     NOT NULL,
    apellido            VARCHAR(80)     NOT NULL,
    telefono            VARCHAR(20),
    num_licencia        VARCHAR(30)     NOT NULL,
    categoria_licencia  VARCHAR(10)     NOT NULL
                        COMMENT 'Ej: A2, B1, B2, C1, C2, C3',
    fecha_venc_licencia DATE            NOT NULL,
    estado              ENUM('activo','inactivo','suspendido')
                                        NOT NULL DEFAULT 'activo',
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                                 ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_conductor    PRIMARY KEY (id_conductor),
    CONSTRAINT uq_conductor_cedula    UNIQUE (cedula),
    CONSTRAINT uq_conductor_licencia  UNIQUE (num_licencia)
) ENGINE=InnoDB COMMENT='Conductores de la empresa';


-- =============================================================================
--  4. VEHICULO
--     No depende de ninguna otra tabla.
-- =============================================================================
CREATE TABLE VEHICULO (
    id_vehiculo       INT             NOT NULL AUTO_INCREMENT,
    placa             VARCHAR(10)     NOT NULL,
    marca             VARCHAR(50)     NOT NULL,
    modelo            VARCHAR(50)     NOT NULL,
    anio              YEAR            NOT NULL,
    tipo              ENUM('camion','furgon','van')
                                      NOT NULL,
    kilometraje_actual DECIMAL(10,2)  NOT NULL DEFAULT 0.00
                                      CHECK (kilometraje_actual >= 0),
    estado            ENUM('disponible','en_viaje','en_mantenimiento','inactivo')
                                      NOT NULL DEFAULT 'disponible',
    created_at        TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                               ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_vehiculo     PRIMARY KEY (id_vehiculo),
    CONSTRAINT uq_vehiculo_placa UNIQUE (placa)
) ENGINE=InnoDB COMMENT='Flota vehicular de TransCarga Andina';


-- =============================================================================
--  5. CLIENTE
--     No depende de ninguna otra tabla.
-- =============================================================================
CREATE TABLE CLIENTE (
    id_cliente          INT             NOT NULL AUTO_INCREMENT,
    tipo_persona        ENUM('natural','juridica')
                                        NOT NULL,
    documento           VARCHAR(20)     NOT NULL
                        COMMENT 'Cédula si es natural, NIT si es jurídica',
    nombre_razon_social VARCHAR(150)    NOT NULL,
    correo              VARCHAR(120),
    telefono            VARCHAR(20),
    ciudad              VARCHAR(80),
    estado              ENUM('activo','inactivo')
                                        NOT NULL DEFAULT 'activo',
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                                 ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_cliente          PRIMARY KEY (id_cliente),
    CONSTRAINT uq_cliente_documento UNIQUE (documento)
) ENGINE=InnoDB COMMENT='Clientes que contratan servicios de envío';


-- =============================================================================
--  6. PROVEEDOR
--     No depende de ninguna otra tabla.
-- =============================================================================
CREATE TABLE PROVEEDOR (
    id_proveedor  INT             NOT NULL AUTO_INCREMENT,
    nit           VARCHAR(20)     NOT NULL,
    nombre        VARCHAR(150)    NOT NULL,
    tipo          ENUM('taller','gasolinera','distribuidor_repuestos','otro')
                                  NOT NULL,
    telefono      VARCHAR(20),
    ciudad        VARCHAR(80),
    estado        ENUM('activo','inactivo')
                                  NOT NULL DEFAULT 'activo',
    created_at    TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                           ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_proveedor    PRIMARY KEY (id_proveedor),
    CONSTRAINT uq_proveedor_nit UNIQUE (nit)
) ENGINE=InnoDB COMMENT='Proveedores: talleres, gasolineras y distribuidores';


-- =============================================================================
--  7. USUARIO
--     Depende de: CONDUCTOR, CLIENTE
--     FK id_conductor e id_cliente son opcionales (nullable).
--     UNIQUE sobre cada FK garantiza la relación 1-a-1 con cada perfil.
-- =============================================================================
CREATE TABLE USUARIO (
    id_usuario       INT             NOT NULL AUTO_INCREMENT,
    nombre_usuario   VARCHAR(60)     NOT NULL,
    contrasena_hash  VARCHAR(255)    NOT NULL,
    rol              ENUM('admin','coordinador','tecnico','conductor','cliente')
                                     NOT NULL,
    correo           VARCHAR(120)    NOT NULL,
    nombre_completo  VARCHAR(150)    NOT NULL,
    estado           ENUM('activo','inactivo','bloqueado')
                                     NOT NULL DEFAULT 'activo',
    id_conductor     INT             NULL
                     COMMENT 'Poblado solo si rol = conductor',
    id_cliente       INT             NULL
                     COMMENT 'Poblado solo si rol = cliente (o dual)',
    created_at       TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                              ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_usuario            PRIMARY KEY (id_usuario),
    CONSTRAINT uq_usuario_nombre     UNIQUE (nombre_usuario),
    CONSTRAINT uq_usuario_correo     UNIQUE (correo),
    -- Garantiza relación 1:1 con cada perfil
    CONSTRAINT uq_usuario_conductor  UNIQUE (id_conductor),
    CONSTRAINT uq_usuario_cliente    UNIQUE (id_cliente),

    CONSTRAINT fk_usuario_conductor  FOREIGN KEY (id_conductor)
        REFERENCES CONDUCTOR(id_conductor) ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_usuario_cliente    FOREIGN KEY (id_cliente)
        REFERENCES CLIENTE(id_cliente)    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='Accesos al sistema. Un usuario puede tener perfil de conductor, cliente o ambos';


-- =============================================================================
--  8. CONTRATO
--     Depende de: PROVEEDOR, USUARIO (creado_por)
-- =============================================================================
CREATE TABLE CONTRATO (
    id_contrato    INT             NOT NULL AUTO_INCREMENT,
    id_proveedor   INT             NOT NULL,
    fecha_inicio   DATE            NOT NULL,
    fecha_fin      DATE            NOT NULL,
    valor          DECIMAL(14,2)   NOT NULL CHECK (valor >= 0),
    tipo_servicio  VARCHAR(80)     NOT NULL,
    estado         ENUM('vigente','vencido','cancelado')
                                   NOT NULL DEFAULT 'vigente',
    creado_por     INT             NULL,
    created_at     TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                            ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_contrato           PRIMARY KEY (id_contrato),
    CONSTRAINT fk_contrato_proveedor FOREIGN KEY (id_proveedor)
        REFERENCES PROVEEDOR(id_proveedor) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_contrato_usuario   FOREIGN KEY (creado_por)
        REFERENCES USUARIO(id_usuario)    ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT ck_contrato_fechas
        CHECK (fecha_fin >= fecha_inicio)
) ENGINE=InnoDB COMMENT='Contratos vigentes con proveedores';

CREATE INDEX idx_contrato_proveedor ON CONTRATO(id_proveedor);


-- =============================================================================
--  9. DOCUMENTO_CONDUCTOR
--     Depende de: CONDUCTOR
-- =============================================================================
CREATE TABLE DOCUMENTO_CONDUCTOR (
    id_doc_conductor INT             NOT NULL AUTO_INCREMENT,
    id_conductor     INT             NOT NULL,
    tipo             ENUM('licencia','examen_medico','certificado','otro')
                                     NOT NULL,
    numero           VARCHAR(50)     NOT NULL,
    fecha_emision    DATE            NOT NULL,
    fecha_vencimiento DATE           NOT NULL,
    url_archivo      VARCHAR(255)    NULL,
    estado           ENUM('vigente','por_vencer','vencido')
                                     NOT NULL DEFAULT 'vigente',
    created_at       TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_doc_conductor         PRIMARY KEY (id_doc_conductor),
    CONSTRAINT fk_doc_conductor_cond    FOREIGN KEY (id_conductor)
        REFERENCES CONDUCTOR(id_conductor) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT ck_doc_conductor_fechas
        CHECK (fecha_vencimiento >= fecha_emision)
) ENGINE=InnoDB COMMENT='Documentos de conductores con control de vencimiento';

CREATE INDEX idx_doc_conductor_cond ON DOCUMENTO_CONDUCTOR(id_conductor);
CREATE INDEX idx_doc_conductor_venc ON DOCUMENTO_CONDUCTOR(fecha_vencimiento);


-- =============================================================================
--  10. DOCUMENTO_VEHICULO
--      Depende de: VEHICULO
-- =============================================================================
CREATE TABLE DOCUMENTO_VEHICULO (
    id_doc_vehiculo  INT             NOT NULL AUTO_INCREMENT,
    id_vehiculo      INT             NOT NULL,
    tipo             ENUM('soat','tarjeta_propiedad','tecnomecanica','seguro','otro')
                                     NOT NULL,
    numero           VARCHAR(50)     NOT NULL,
    fecha_emision    DATE            NOT NULL,
    fecha_vencimiento DATE           NOT NULL,
    url_archivo      VARCHAR(255)    NULL,
    estado           ENUM('vigente','por_vencer','vencido')
                                     NOT NULL DEFAULT 'vigente',
    created_at       TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_doc_vehiculo        PRIMARY KEY (id_doc_vehiculo),
    CONSTRAINT fk_doc_vehiculo_veh    FOREIGN KEY (id_vehiculo)
        REFERENCES VEHICULO(id_vehiculo) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT ck_doc_vehiculo_fechas
        CHECK (fecha_vencimiento >= fecha_emision)
) ENGINE=InnoDB COMMENT='Documentos del parque automotor: SOAT, tecno, seguros';

CREATE INDEX idx_doc_vehiculo_veh  ON DOCUMENTO_VEHICULO(id_vehiculo);
CREATE INDEX idx_doc_vehiculo_venc ON DOCUMENTO_VEHICULO(fecha_vencimiento);


-- =============================================================================
--  11. VIAJE
--      Depende de: VEHICULO, CONDUCTOR, RUTA, TARIFA, USUARIO
--      NOTA: el cliente NO va directo al viaje; llega a través de ENVIO.
-- =============================================================================
CREATE TABLE VIAJE (
    id_viaje                INT             NOT NULL AUTO_INCREMENT,
    id_vehiculo             INT             NOT NULL,
    id_conductor            INT             NOT NULL,
    id_ruta                 INT             NOT NULL,
    id_tarifa               INT             NOT NULL,
    tipo_carga              VARCHAR(60)     NOT NULL,
    peso_kg                 DECIMAL(10,2)   NOT NULL CHECK (peso_kg > 0),
    fecha_salida            DATETIME        NOT NULL,
    fecha_llegada_estimada  DATETIME        NOT NULL,
    fecha_llegada           DATETIME        NULL
                            COMMENT 'NULL mientras el viaje no ha concluido',
    valor_flete             DECIMAL(14,2)   NOT NULL DEFAULT 0.00
                            COMMENT 'Calculado a partir de TARIFA según tipo_calculo',
    estado                  ENUM('programado','en_curso','completado','cancelado')
                                            NOT NULL DEFAULT 'programado',
    observaciones           TEXT            NULL,
    creado_por              INT             NULL,
    created_at              TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                                     ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_viaje            PRIMARY KEY (id_viaje),
    CONSTRAINT fk_viaje_vehiculo   FOREIGN KEY (id_vehiculo)
        REFERENCES VEHICULO(id_vehiculo)    ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_viaje_conductor  FOREIGN KEY (id_conductor)
        REFERENCES CONDUCTOR(id_conductor)  ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_viaje_ruta       FOREIGN KEY (id_ruta)
        REFERENCES RUTA(id_ruta)            ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_viaje_tarifa     FOREIGN KEY (id_tarifa)
        REFERENCES TARIFA(id_tarifa)        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_viaje_usuario    FOREIGN KEY (creado_por)
        REFERENCES USUARIO(id_usuario)      ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT ck_viaje_fechas
        CHECK (fecha_llegada_estimada > fecha_salida)
) ENGINE=InnoDB COMMENT='Operaciones de transporte. Un viaje puede agrupar múltiples envíos de distintos clientes';

CREATE INDEX idx_viaje_vehiculo  ON VIAJE(id_vehiculo);
CREATE INDEX idx_viaje_conductor ON VIAJE(id_conductor);
CREATE INDEX idx_viaje_ruta      ON VIAJE(id_ruta);
CREATE INDEX idx_viaje_estado    ON VIAJE(estado);
CREATE INDEX idx_viaje_salida    ON VIAJE(fecha_salida);


-- =============================================================================
--  12. ENVIO
--      Depende de: CLIENTE, VIAJE, USUARIO
--      Un cliente puede tener muchos envíos. Un viaje agrupa muchos envíos.
-- =============================================================================
CREATE TABLE ENVIO (
    id_envio          INT             NOT NULL AUTO_INCREMENT,
    id_cliente        INT             NOT NULL,
    id_viaje          INT             NOT NULL,
    direccion_origen  VARCHAR(200)    NOT NULL,
    direccion_destino VARCHAR(200)    NOT NULL,
    descripcion       TEXT            NULL,
    fecha_solicitud   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado            ENUM('pendiente','en_transito','entregado','devuelto','cancelado')
                                      NOT NULL DEFAULT 'pendiente',
    creado_por        INT             NULL,
    created_at        TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                               ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_envio           PRIMARY KEY (id_envio),
    CONSTRAINT fk_envio_cliente   FOREIGN KEY (id_cliente)
        REFERENCES CLIENTE(id_cliente)  ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_envio_viaje     FOREIGN KEY (id_viaje)
        REFERENCES VIAJE(id_viaje)      ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_envio_usuario   FOREIGN KEY (creado_por)
        REFERENCES USUARIO(id_usuario)  ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='Envíos individuales de clientes. Múltiples envíos pueden ir en un mismo viaje';

CREATE INDEX idx_envio_cliente ON ENVIO(id_cliente);
CREATE INDEX idx_envio_viaje   ON ENVIO(id_viaje);
CREATE INDEX idx_envio_estado  ON ENVIO(estado);


-- =============================================================================
--  13. DETALLE_ENVIO
--      Depende de: ENVIO
--      Líneas de mercancía dentro de un envío.
-- =============================================================================
CREATE TABLE DETALLE_ENVIO (
    id_detalle_envio      INT             NOT NULL AUTO_INCREMENT,
    id_envio              INT             NOT NULL,
    descripcion_mercancia VARCHAR(200)    NOT NULL,
    tipo_embalaje         VARCHAR(80)     NULL,
    cantidad              INT             NOT NULL CHECK (cantidad > 0),
    peso_kg               DECIMAL(10,2)   NOT NULL CHECK (peso_kg > 0),
    volumen_m3            DECIMAL(8,4)    NULL      CHECK (volumen_m3 > 0),
    valor_declarado       DECIMAL(14,2)   NOT NULL  CHECK (valor_declarado >= 0),
    created_at            TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_detalle_envio        PRIMARY KEY (id_detalle_envio),
    CONSTRAINT fk_detalle_envio_envio  FOREIGN KEY (id_envio)
        REFERENCES ENVIO(id_envio) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB COMMENT='Líneas de mercancía dentro de un envío';

CREATE INDEX idx_detalle_envio ON DETALLE_ENVIO(id_envio);


-- =============================================================================
--  14. MANTENIMIENTO
--      Depende de: VEHICULO, PROVEEDOR, USUARIO
-- =============================================================================
CREATE TABLE MANTENIMIENTO (
    id_mantenimiento INT             NOT NULL AUTO_INCREMENT,
    id_vehiculo      INT             NOT NULL,
    id_proveedor     INT             NOT NULL
                     COMMENT 'Taller que ejecuta el mantenimiento',
    tipo             ENUM('preventivo','correctivo')
                                     NOT NULL,
    fecha            DATE            NOT NULL,
    kilometros       DECIMAL(10,2)   NOT NULL CHECK (kilometros >= 0)
                     COMMENT 'Kilometraje del vehículo al momento de la intervención',
    descripcion      TEXT            NOT NULL,
    costo            DECIMAL(14,2)   NOT NULL CHECK (costo >= 0),
    estado           ENUM('pendiente','en_proceso','completado','cancelado')
                                     NOT NULL DEFAULT 'pendiente',
    creado_por       INT             NULL,
    created_at       TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                              ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_mantenimiento           PRIMARY KEY (id_mantenimiento),
    CONSTRAINT fk_mant_vehiculo           FOREIGN KEY (id_vehiculo)
        REFERENCES VEHICULO(id_vehiculo)    ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_mant_proveedor          FOREIGN KEY (id_proveedor)
        REFERENCES PROVEEDOR(id_proveedor)  ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_mant_usuario            FOREIGN KEY (creado_por)
        REFERENCES USUARIO(id_usuario)      ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='Intervenciones mecánicas preventivas y correctivas de la flota';

CREATE INDEX idx_mant_vehiculo  ON MANTENIMIENTO(id_vehiculo);
CREATE INDEX idx_mant_proveedor ON MANTENIMIENTO(id_proveedor);
CREATE INDEX idx_mant_fecha     ON MANTENIMIENTO(fecha);


-- =============================================================================
--  15. REPUESTO_MANTENIMIENTO
--      Depende de: MANTENIMIENTO
-- =============================================================================
CREATE TABLE REPUESTO_MANTENIMIENTO (
    id_repuesto       INT             NOT NULL AUTO_INCREMENT,
    id_mantenimiento  INT             NOT NULL,
    nombre            VARCHAR(120)    NOT NULL,
    referencia        VARCHAR(60)     NULL,
    cantidad          INT             NOT NULL CHECK (cantidad > 0),
    costo_unitario    DECIMAL(12,2)   NOT NULL CHECK (costo_unitario >= 0),
    created_at        TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_repuesto          PRIMARY KEY (id_repuesto),
    CONSTRAINT fk_repuesto_mant     FOREIGN KEY (id_mantenimiento)
        REFERENCES MANTENIMIENTO(id_mantenimiento) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB COMMENT='Repuestos utilizados en cada intervención de mantenimiento';

CREATE INDEX idx_repuesto_mant ON REPUESTO_MANTENIMIENTO(id_mantenimiento);


-- =============================================================================
--  16. COMBUSTIBLE
--      Depende de: VEHICULO, PROVEEDOR, USUARIO
-- =============================================================================
CREATE TABLE COMBUSTIBLE (
    id_combustible            INT             NOT NULL AUTO_INCREMENT,
    id_vehiculo               INT             NOT NULL,
    id_proveedor              INT             NOT NULL
                              COMMENT 'Gasolinera o distribuidora',
    fecha                     DATE            NOT NULL,
    litros                    DECIMAL(8,2)    NOT NULL CHECK (litros > 0),
    precio_por_litro          DECIMAL(8,2)    NOT NULL CHECK (precio_por_litro > 0),
    km_al_recargar            DECIMAL(10,2)   NOT NULL CHECK (km_al_recargar >= 0),
    km_desde_ultima_recarga   DECIMAL(10,2)   NULL     CHECK (km_desde_ultima_recarga >= 0)
                              COMMENT 'Permite calcular rendimiento km/litro',
    tipo_combustible          ENUM('diesel','gasolina_corriente','gasolina_extra','gas')
                                              NOT NULL,
    creado_por                INT             NULL,
    created_at                TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_combustible          PRIMARY KEY (id_combustible),
    CONSTRAINT fk_combustible_veh      FOREIGN KEY (id_vehiculo)
        REFERENCES VEHICULO(id_vehiculo)    ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_combustible_prov     FOREIGN KEY (id_proveedor)
        REFERENCES PROVEEDOR(id_proveedor)  ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_combustible_usuario  FOREIGN KEY (creado_por)
        REFERENCES USUARIO(id_usuario)      ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='Recargas de combustible por vehículo. Permite calcular eficiencia km/litro';

CREATE INDEX idx_comb_vehiculo  ON COMBUSTIBLE(id_vehiculo);
CREATE INDEX idx_comb_fecha     ON COMBUSTIBLE(fecha);


-- =============================================================================
--  17. INFRACCION
--      Depende de: CONDUCTOR, VIAJE
-- =============================================================================
CREATE TABLE INFRACCION (
    id_infraccion  INT             NOT NULL AUTO_INCREMENT,
    id_conductor   INT             NOT NULL,
    id_viaje       INT             NULL
                   COMMENT 'Nullable: hay infracciones fuera de viajes activos',
    fecha          DATE            NOT NULL,
    tipo           VARCHAR(80)     NOT NULL,
    monto          DECIMAL(12,2)   NOT NULL CHECK (monto >= 0),
    descripcion    TEXT            NULL,
    estado_pago    ENUM('pendiente','pagada','en_disputa','condonada')
                                   NOT NULL DEFAULT 'pendiente',
    autoridad      VARCHAR(100)    NOT NULL,
    created_at     TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                            ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_infraccion          PRIMARY KEY (id_infraccion),
    CONSTRAINT fk_infraccion_cond     FOREIGN KEY (id_conductor)
        REFERENCES CONDUCTOR(id_conductor) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_infraccion_viaje    FOREIGN KEY (id_viaje)
        REFERENCES VIAJE(id_viaje)         ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='Infracciones de tránsito de conductores. Puede asociarse al viaje en curso';

CREATE INDEX idx_infraccion_cond  ON INFRACCION(id_conductor);
CREATE INDEX idx_infraccion_viaje ON INFRACCION(id_viaje);


-- =============================================================================
--  18. POSICION_GPS
--      Depende de: VIAJE
--      No puede existir sin un viaje activo (ON DELETE RESTRICT).
-- =============================================================================
CREATE TABLE POSICION_GPS (
    id_posicion    INT             NOT NULL AUTO_INCREMENT,
    id_viaje       INT             NOT NULL,
    latitud        DECIMAL(10,7)   NOT NULL,
    longitud       DECIMAL(10,7)   NOT NULL,
    velocidad_kmh  DECIMAL(6,2)    NULL      CHECK (velocidad_kmh >= 0),
    marca_tiempo   DATETIME        NOT NULL,
    tipo_evento    VARCHAR(60)     NULL
                   COMMENT 'Ej: inicio, parada, desvio, fin',
    created_at     TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_posicion_gps      PRIMARY KEY (id_posicion),
    CONSTRAINT fk_gps_viaje         FOREIGN KEY (id_viaje)
        REFERENCES VIAJE(id_viaje) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB COMMENT='Trazabilidad GPS por viaje. Alto volumen — considerar particionamiento por fecha en producción';

CREATE INDEX idx_gps_viaje        ON POSICION_GPS(id_viaje);
CREATE INDEX idx_gps_marca_tiempo ON POSICION_GPS(marca_tiempo);


-- =============================================================================
--  19. NOVEDAD_VIAJE
--      Depende de: VIAJE, USUARIO
--      No puede existir sin un viaje (ON DELETE RESTRICT).
-- =============================================================================
CREATE TABLE NOVEDAD_VIAJE (
    id_novedad   INT             NOT NULL AUTO_INCREMENT,
    id_viaje     INT             NOT NULL,
    tipo         ENUM('accidente','demora','desvio','averia','otro')
                                 NOT NULL,
    descripcion  TEXT            NOT NULL,
    fecha_hora   DATETIME        NOT NULL,
    estado       ENUM('abierta','en_gestion','cerrada')
                                 NOT NULL DEFAULT 'abierta',
    creado_por   INT             NULL,
    created_at   TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_novedad_viaje     PRIMARY KEY (id_novedad),
    CONSTRAINT fk_novedad_viaje     FOREIGN KEY (id_viaje)
        REFERENCES VIAJE(id_viaje)       ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_novedad_usuario   FOREIGN KEY (creado_por)
        REFERENCES USUARIO(id_usuario)   ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='Novedades e incidentes registrados durante un viaje';

CREATE INDEX idx_novedad_viaje ON NOVEDAD_VIAJE(id_viaje);


-- =============================================================================
--  20. FACTURA
--      Depende de: VIAJE, CLIENTE, USUARIO
-- =============================================================================
CREATE TABLE FACTURA (
    id_factura        INT             NOT NULL AUTO_INCREMENT,
    id_viaje          INT             NOT NULL,
    id_cliente        INT             NOT NULL,
    numero_factura    VARCHAR(30)     NOT NULL
                      COMMENT 'Formato sugerido: FACT-YYYY-NNNN',
    fecha_emision     DATE            NOT NULL,
    fecha_vencimiento DATE            NOT NULL,
    subtotal          DECIMAL(14,2)   NOT NULL CHECK (subtotal >= 0),
    porcentaje_iva    DECIMAL(5,2)    NOT NULL DEFAULT 19.00
                                     CHECK (porcentaje_iva >= 0),
    total             DECIMAL(14,2)   NOT NULL CHECK (total >= 0)
                      COMMENT 'Calculado: subtotal + (subtotal * porcentaje_iva / 100)',
    estado            ENUM('pendiente','pagada','vencida','anulada')
                                      NOT NULL DEFAULT 'pendiente',
    creado_por        INT             NULL,
    created_at        TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                               ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_factura           PRIMARY KEY (id_factura),
    CONSTRAINT uq_factura_numero    UNIQUE (numero_factura),
    CONSTRAINT fk_factura_viaje     FOREIGN KEY (id_viaje)
        REFERENCES VIAJE(id_viaje)       ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_factura_cliente   FOREIGN KEY (id_cliente)
        REFERENCES CLIENTE(id_cliente)   ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_factura_usuario   FOREIGN KEY (creado_por)
        REFERENCES USUARIO(id_usuario)   ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT ck_factura_fechas
        CHECK (fecha_vencimiento >= fecha_emision)
) ENGINE=InnoDB COMMENT='Facturas emitidas por viaje. El total se valida en capa de negocio';

CREATE INDEX idx_factura_viaje   ON FACTURA(id_viaje);
CREATE INDEX idx_factura_cliente ON FACTURA(id_cliente);
CREATE INDEX idx_factura_estado  ON FACTURA(estado);


-- =============================================================================
--  21. DETALLE_FACTURA
--      Depende de: FACTURA, ENVIO
--      Desglosa qué envíos componen cada factura.
-- =============================================================================
CREATE TABLE DETALLE_FACTURA (
    id_detalle_factura INT             NOT NULL AUTO_INCREMENT,
    id_factura         INT             NOT NULL,
    id_envio           INT             NOT NULL,
    descripcion        VARCHAR(200)    NOT NULL,
    cantidad           INT             NOT NULL DEFAULT 1 CHECK (cantidad > 0),
    valor_unitario     DECIMAL(14,2)   NOT NULL CHECK (valor_unitario >= 0),
    subtotal_linea     DECIMAL(14,2)   NOT NULL CHECK (subtotal_linea >= 0)
                       COMMENT 'Calculado: cantidad * valor_unitario',
    created_at         TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_detalle_factura        PRIMARY KEY (id_detalle_factura),
    CONSTRAINT fk_det_fact_factura       FOREIGN KEY (id_factura)
        REFERENCES FACTURA(id_factura) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_det_fact_envio         FOREIGN KEY (id_envio)
        REFERENCES ENVIO(id_envio)     ON UPDATE CASCADE ON DELETE RESTRICT,
    -- Un envío aparece como máximo una vez por factura
    CONSTRAINT uq_det_factura_envio      UNIQUE (id_factura, id_envio)
) ENGINE=InnoDB COMMENT='Desglose de envíos por factura. Permite facturas multi-envío';

CREATE INDEX idx_det_fact_factura ON DETALLE_FACTURA(id_factura);
CREATE INDEX idx_det_fact_envio   ON DETALLE_FACTURA(id_envio);


-- =============================================================================
--  22. PAGO
--      Depende de: FACTURA, USUARIO
-- =============================================================================
CREATE TABLE PAGO (
    id_pago                 INT             NOT NULL AUTO_INCREMENT,
    id_factura              INT             NOT NULL,
    fecha_pago              DATE            NOT NULL,
    monto                   DECIMAL(14,2)   NOT NULL CHECK (monto > 0),
    metodo                  ENUM('transferencia','efectivo','cheque','tarjeta_credito','tarjeta_debito','pse')
                                            NOT NULL,
    referencia_transaccion  VARCHAR(100)    NULL,
    estado                  ENUM('confirmado','pendiente','rechazado')
                                            NOT NULL DEFAULT 'pendiente',
    url_comprobante         VARCHAR(255)    NULL,
    creado_por              INT             NULL,
    created_at              TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_pago           PRIMARY KEY (id_pago),
    CONSTRAINT fk_pago_factura   FOREIGN KEY (id_factura)
        REFERENCES FACTURA(id_factura)   ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_pago_usuario   FOREIGN KEY (creado_por)
        REFERENCES USUARIO(id_usuario)   ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='Abonos o pagos totales contra una factura. Soporta pagos parciales';

CREATE INDEX idx_pago_factura ON PAGO(id_factura);
CREATE INDEX idx_pago_fecha   ON PAGO(fecha_pago);


-- =============================================================================
--  23. NOTIFICACION
--      Depende de: USUARIO
--      No puede existir sin su usuario (ON DELETE CASCADE).
-- =============================================================================
CREATE TABLE NOTIFICACION (
    id_notificacion INT             NOT NULL AUTO_INCREMENT,
    id_usuario      INT             NOT NULL,
    tipo            VARCHAR(60)     NOT NULL
                    COMMENT 'Ej: vencimiento_doc, mantenimiento_programado, pago_pendiente',
    mensaje         TEXT            NOT NULL,
    fecha_hora      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    leida           BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_notificacion      PRIMARY KEY (id_notificacion),
    CONSTRAINT fk_notif_usuario     FOREIGN KEY (id_usuario)
        REFERENCES USUARIO(id_usuario) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='Notificaciones internas del sistema dirigidas a usuarios';

CREATE INDEX idx_notif_usuario ON NOTIFICACION(id_usuario);
CREATE INDEX idx_notif_leida   ON NOTIFICACION(leida);


-- ─────────────────────────────────────────────────────────────────────────────
--  CIERRE
-- ─────────────────────────────────────────────────────────────────────────────
SET FOREIGN_KEY_CHECKS = 1;

-- =============================================================================
--  RESUMEN
--  Tabla                    | Depende de
--  ─────────────────────────┼──────────────────────────────────────────────
--  RUTA                     | –
--  TARIFA                   | RUTA
--  CONDUCTOR                | –
--  VEHICULO                 | –
--  CLIENTE                  | –
--  PROVEEDOR                | –
--  USUARIO                  | CONDUCTOR, CLIENTE
--  CONTRATO                 | PROVEEDOR, USUARIO
--  DOCUMENTO_CONDUCTOR      | CONDUCTOR
--  DOCUMENTO_VEHICULO       | VEHICULO
--  VIAJE                    | VEHICULO, CONDUCTOR, RUTA, TARIFA, USUARIO
--  ENVIO                    | CLIENTE, VIAJE, USUARIO
--  DETALLE_ENVIO            | ENVIO
--  MANTENIMIENTO            | VEHICULO, PROVEEDOR, USUARIO
--  REPUESTO_MANTENIMIENTO   | MANTENIMIENTO
--  COMBUSTIBLE              | VEHICULO, PROVEEDOR, USUARIO
--  INFRACCION               | CONDUCTOR, VIAJE
--  POSICION_GPS             | VIAJE
--  NOVEDAD_VIAJE            | VIAJE, USUARIO
--  FACTURA                  | VIAJE, CLIENTE, USUARIO
--  DETALLE_FACTURA          | FACTURA, ENVIO
--  PAGO                     | FACTURA, USUARIO
--  NOTIFICACION             | USUARIO
-- =============================================================================