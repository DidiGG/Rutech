from .conductor import CRUDConductor
from .vehiculo import CRUDVehiculo
from .cliente import CRUDCliente
from .ruta import CRUDRuta
from .proveedor import CRUDProveedor
from .usuario import CRUDUsuario
from .tarifa import CRUDTarifa
from .contrato import CRUDContrato
from .documento_conductor import CRUDDocumentoConductor
from .documento_vehiculo import CRUDDocumentoVehiculo
from .envio import CRUDEnvio
from .detalle_envio import CRUDDetalleEnvio
from .posicion_gps import CRUDPosicionGPS
from .mantenimiento import CRUDMantenimiento
from .repuesto_mantenimiento import CRUDRepuestoMantenimiento
from .combustible import CRUDCombustible
from .viaje import CRUDViaje

__all__ = ["CRUDConductor", "CRUDVehiculo", "CRUDCliente", "CRUDRuta",
           "CRUDProveedor", "CRUDUsuario", "CRUDTarifa", "CRUDContrato",
           "CRUDDocumentoConductor", "CRUDDocumentoVehiculo", "CRUDEnvio", "CRUDDetalleEnvio", "CRUDPosicionGPS", "CRUDMantenimiento", "CRUDRepuestoMantenimiento", "CRUDCombustible", "CRUDViaje"]