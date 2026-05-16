# RUTECH — Sistema de Gestión de Flotas

## Estado actual del proyecto

- Aplicación UI en `src/main.py` con `tkinter`.
- CRUDs implementados para:
  - `CONDUCTOR`
  - `VEHICULO`
  - `CLIENTE`
  - `RUTA`
  - `PROVEEDOR`
  - `USUARIO`
  - `TARIFA`
  - `CONTRATO`
  - `DOCUMENTO_CONDUCTOR`
  - `DOCUMENTO_VEHICULO`
  - `ENVIO`
  - `DETALLE_ENVIO`
  - `POSICION_GPS`
  - `MANTENIMIENTO`
  - `REPUESTO_MANTENIMIENTO`
  - `COMBUSTIBLE`
  - `VIAJE`
- Base de datos MySQL configurada en `database/conecction.py`.
- Semilla de datos de prueba lista en `database/insert_data.sql`.
- Esquema de base de datos completo en `database/schema.sql`.

## Mi estado con respecto al plan de tareas

### Lo que ya está cubierto
- CRUD básicos con interfaz de lista/insertar/editar/eliminar.
- Estructura base reutilizable en `src/cruds/base.py`.
- Datos de prueba para muchas tablas en `database/insert_data.sql`.

### Fase 2 a Fase 9 pendientes

Faltan implementaciones para:
- `DETALLE_ENVIO`
- `POSICION_GPS`
- `NOVEDAD_VIAJE`
- `MANTENIMIENTO`
- `REPUESTO_MANTENIMIENTO`
- `COMBUSTIBLE`
- `INFRACCION`
- `FACTURA`
- `DETALLE_FACTURA`
- `PAGO`
- `NOTIFICACION`
- Autenticación y control de acceso
- Reportes y validaciones de negocio

## Siguientes pasos recomendados

1. Crear CRUDs adicionales siguiendo el patrón de `src/cruds/base.py`.
   - Empieza por `PROVEEDOR`, `USUARIO`, `TARIFA` y `CONTRATO`.
2. Agregar navegación lateral en `src/main.py` para esos CRUDs.
3. Desarrollar el módulo `VIAJE` con validaciones de vehículo/conductor disponible.
4. Añadir `ENVIO` y `DETALLE_ENVIO` para el flujo de carga y cálculo de peso.
5. Implementar `FACTURA`/`PAGO` para completar facturación y estado de cuenta.
6. Añadir autenticación y roles solo cuando haya CRUDs base suficientes.

## Cómo ejecutar

1. Crear la base de datos y ejecutar `database/schema.sql` en MySQL.
2. Ejecutar `database/insert_data.sql` para cargar datos de prueba.
3. Instalar dependencias:

```bash
pip install -r src/requirements.txt
```

4. Ejecutar la aplicación:

```bash
python src/main.py
```

> Si `tkinter` no está instalado con tu Python, instálalo desde el instalador oficial de Python o usa el paquete de tu sistema.

## Nota importante

- El proyecto actual usa `tkinter`, no Flask.
- Si tu plan requiere Flask, deberás adaptar la arquitectura y crear un backend separado.
