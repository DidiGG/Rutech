import mysql.connector

# Configuración de la conexión
DB_CONFIG = {
    'user': 'root',  # cambia este usuario si no es root
    'password': 'Angel180304',  # cambia la contraseña por la tuya
    'host': 'localhost',  # aquí va la IP/nombre del servidor MySQL
    'database': 'rutech',  # la base de datos creada con schema.sql
    'charset': 'utf8mb4',
    'raise_on_warnings': True
}

def get_conn():
    """Devuelve una conexión activa a la base de datos."""
    return mysql.connector.connect(**DB_CONFIG)


def test_connection():
    """Prueba la conexión y cierra correctamente."""
    cnx = None
    cursor = None
    try:
        cnx = get_conn()
        cursor = cnx.cursor()
        print('Conexión exitosa.')
    except mysql.connector.Error as err:
        print(f'Error de conexión: {err}')
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None:
            cnx.close()
            print('Conexión cerrada.')


def fetch_rutas(limit=5):
    """Ejemplo real: obtiene algunas rutas desde la tabla RUTA."""
    cnx = get_conn()
    cursor = cnx.cursor()
    try:
        cursor.execute('SELECT id_ruta, nombre, origen, destino FROM RUTA LIMIT %s', (limit,))
        return cursor.fetchall()
    finally:
        cursor.close()
        cnx.close()


if __name__ == '__main__':
    test_connection()
    rutas = fetch_rutas()
    print('Rutas encontradas:', rutas)
