import psycopg2

def conectar_db():
    """Establece una conexión a la base de datos PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host="23.108.108.219",  # Dirección del host
            port="5432",             # Puerto para PostgreSQL
            dbname="ordenservicio",  # Nombre de la base de datos
            user="rudolfmotos",      # Usuario
            password="cqw2YNdjz6pMPc0Z"  # Contraseña
        )
        return conn
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Llamar a la función para probar la conexión
conn = conectar_db()
if conn:
    print("Conexión exitosa.")
    # Recuerda cerrar la conexión cuando termines
    conn.close()
else:
    print("No se pudo conectar a la base de datos.")