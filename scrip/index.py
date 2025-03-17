import sys
import os
import flet as ft
import psycopg2
import bcrypt

# Añadir el directorio superior al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import conectar_db 
from secundario.bienvenida import mostrar_bienvenida 

# ---------- FUNCIONES DE SEGURIDAD ----------
def hash_password(password):
    """Genera un hash seguro para la contraseña."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verificar_password(password, hashed_password):
    """Verifica si la contraseña ingresada coincide con el hash almacenado."""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

# ---------- FUNCIONES DE BASE DE DATOS ----------
def insertar_usuario(nombre, apellido, celular, dni, correo, contraseña):
    """Inserta un nuevo usuario en la base de datos con validaciones mejoradas."""
    # Validaciones previas antes de la inserción
    if len(nombre) < 2 or len(apellido) < 2:
        return "❌ Nombre y apellido deben tener al menos 2 caracteres."
    if not celular.isdigit() or len(celular) < 9:
        return "❌ Número de celular inválido."
    if not dni.isdigit() or len(dni) != 8:
        return "❌ DNI inválido (Debe tener 8 dígitos)."
    if "@" not in correo or "." not in correo:
        return "❌ Correo electrónico no válido."
    if len(contraseña) < 6:
        return "❌ La contraseña debe tener al menos 6 caracteres."

    hashed_password = hash_password(contraseña)

    try:
        with conectar_db() as conn:
            with conn.cursor() as cursor:
                # Verificar si el correo ya está registrado
                cursor.execute("SELECT 1 FROM usuario WHERE correo = %s", (correo,))
                if cursor.fetchone():
                    return "⚠️ Este correo ya está registrado."

                # Insertar usuario
                query = '''INSERT INTO usuario (nombre, apellido, celular, dni, correo, contraseña) 
                           VALUES (%s, %s, %s, %s, %s, %s)'''
                cursor.execute(query, (nombre, apellido, celular, dni, correo, hashed_password))
                conn.commit()

        return "✅ ¡Cuenta creada con éxito!"

    except psycopg2.Error as e:
        return f"❌ Error en la base de datos: {e}"
    except Exception as e:
        return f"❌ Error inesperado: {e}"

def iniciar_sesion(correo, contraseña):
    """Verifica el usuario y la contraseña para iniciar sesión."""
    try:
        with conectar_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT nombre, contraseña FROM usuario WHERE correo = %s", (correo,))
                resultado = cursor.fetchone()

                if not resultado:
                    return None, "⚠️ Este correo no está registrado."

                nombre, hashed_password = resultado

                if verificar_password(contraseña, hashed_password):
                    return nombre, "✅ Inicio de sesión exitoso."
                else:
                    return None, "❌ Contraseña incorrecta."

    except psycopg2.Error as e:
        return None, f"❌ Error en la base de datos: {e}"
    except Exception as e:
        return None, f"❌ Error inesperado: {e}"

# ---------- INTERFAZ CON FLET ----------
def main(page: ft.Page):
    page.title = "Login y Registro"
    page.window_width = 800
    page.window_height = 500
    page.bgcolor = "#F8F9FA"

    def mostrar_mensaje(texto, color):
        page.snack_bar = ft.SnackBar(content=ft.Text(texto), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def mostrar_login(e):
        frame_login.visible = True
        frame_registro.visible = False
        page.update()

    def mostrar_registro(e):
        frame_login.visible = False
        frame_registro.visible = True
        page.update()

    def registrar_usuario(e):
        nombre = entry_nombre.value.strip()
        apellido = entry_apellido.value.strip()
        celular = entry_celular_reg.value.strip()
        dni = entry_dni_reg.value.strip()
        correo = entry_correo_reg.value.strip()
        contraseña = entry_contraseña_reg.value.strip()

        resultado = insertar_usuario(nombre, apellido, celular, dni, correo, contraseña)
        color = "green" if "✅" in resultado else "red"
        mostrar_mensaje(resultado, color)

        if "✅" in resultado:
            # Limpiar campos de registro
            entry_nombre.value = ""
            entry_apellido.value = ""
            entry_celular_reg.value = ""
            entry_dni_reg.value = ""
            entry_correo_reg.value = ""
            entry_contraseña_reg.value = ""
            page.update()
            mostrar_bienvenida(page, nombre, mostrar_inicio)  # Asegúrate de pasar mostrar_inicio

    def iniciar_sesion_usuario(e):
        correo = entry_correo_login.value.strip()
        contraseña = entry_contraseña_login.value.strip()

        nombre, resultado = iniciar_sesion(correo, contraseña)
        color = "green" if "✅" in resultado else "red"
        mostrar_mensaje(resultado, color)

        if nombre:  # Si el inicio de sesión es exitoso
            page.update()
            mostrar_bienvenida(page, nombre, mostrar_inicio)  # Asegúrate de pasar mostrar_inicio

    def mostrar_inicio():
        """Función para mostrar la pantalla de inicio."""
        frame_login.visible = True
        frame_registro.visible = False
        page.update()

    # Definición de campos de entrada
    entry_nombre = ft.TextField(label="Nombre")
    entry_apellido = ft.TextField(label="Apellido")
    entry_celular_reg = ft.TextField(label="Celular")
    entry_dni_reg = ft.TextField(label="DNI")
    entry_correo_reg = ft.TextField(label="Correo")
    entry_contraseña_reg = ft.TextField(label="Contraseña", password=True)

    entry_correo_login = ft.TextField(label="Correo")
    entry_contraseña_login = ft.TextField(label="Contraseña", password=True)

    # Panel Izquierdo
    panel_izquierdo = ft.Container(
        width=300,
        height=600,
        bgcolor="#343A40",
        border_radius=10,
        padding=30,
        content=ft.Column(
            [
                ft.Text("¿Ya tienes cuenta?", size=16, weight="bold", color="white"),
                ft.ElevatedButton("INICIAR SESIÓN", bgcolor="#007BFF", color="white", on_click=mostrar_login),
                ft.Divider(color="white"),
                ft.Text("¿Eres nuevo?", size=16, weight="bold", color="white"),
                ft.ElevatedButton("REGISTRARSE", bgcolor="#28A745", color="white", on_click=mostrar_registro),
            ],
            alignment="center",
            spacing=10
        )
    )

    # Formulario de Registro
    frame_registro = ft.Container(
        visible=False,
        content=ft.Column(
            [
                ft.Text("Crear Cuenta", size=18, weight="bold"),
                entry_nombre,
                entry_apellido,
                entry_celular_reg,
                entry_dni_reg,
                entry_correo_reg,
                entry_contraseña_reg,
                ft.ElevatedButton("CREAR MI CUENTA", bgcolor="#007BFF", color="white", on_click=registrar_usuario),
            ],
            alignment="center",
            spacing=10
        )
    )

    # Formulario de Login
    frame_login = ft.Container(
        visible=True,
        content=ft.Column(
            [
                ft.Text("Iniciar Sesión", size=18, weight="bold"),
                entry_correo_login,
                entry_contraseña_login,
                ft.ElevatedButton("INGRESAR", bgcolor="#007BFF", color="white", on_click=iniciar_sesion_usuario)
            ],
            alignment="center",
            spacing=10
        )
    )

    # Contenedor principal
    page.add(ft.Row([panel_izquierdo, ft.Stack([frame_registro, frame_login])]))

ft.app(target=main)