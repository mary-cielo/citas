import os
import sys
import flet as ft
import psycopg2
import bcrypt

sys.path.append(os.path.join(os.path.dirname(__file__), '..','..'))
from secundario.inicio import inicio_inicio
from scrip.db import conectar_db

# Ruta absoluta al logo
logo_path = os.path.abspath("../iconos/logo.png")

# --------- UTILIDADES ---------
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verificar_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def obtener_correos_usuarios():
    try:
        with conectar_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT correo FROM usuario")
                return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"❌ Error al obtener correos: {e}")
        return []

# --------- BASE DE DATOS ---------
def insertar_usuario(nombre_usuario, celular, correo, contraseña):
    try:
        hashed_password = hash_password(contraseña)
        with conectar_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM usuario WHERE correo = %s", (correo,))
                if cursor.fetchone():
                    return "⚠️ Este correo ya está registrado."
                cursor.execute(
                    "INSERT INTO usuario (nombre_usuario, celular, correo, contraseña) VALUES (%s, %s, %s, %s)",
                    (nombre_usuario, celular, correo, hashed_password)
                )
                conn.commit()
        return "✅ ¡Cuenta creada con éxito!"
    except psycopg2.Error as e:
        return f"❌ Error en la base de datos: {e.pgerror}"
    except Exception as e:
        return f"❌ Error inesperado: {e}"

def iniciar_sesion(correo, contraseña):
    try:
        with conectar_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT nombre_usuario, contraseña FROM usuario WHERE correo = %s", (correo,))
                resultado = cursor.fetchone()
                if not resultado:
                    return None, "⚠️ Este correo no está registrado."
                nombre, hashed_password = resultado
                if verificar_password(contraseña, hashed_password):
                    return nombre, "✅ Inicio de sesión exitoso."
                else:
                    return None, "❌ Contraseña incorrecta."
    except Exception as e:
        return None, f"❌ Error: {e}"

# --------- INTERFAZ ---------
def main(page: ft.Page):
    page.title = "Login y Registro"
    page.window_width = 900
    page.window_height = 500
    page.bgcolor = "#1E1E1E"
    logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..', 'iconos', 'logo.png'))
    logo = ft.Image(src=logo_path, width=180, height=180, visible=True)

    correos_disponibles = obtener_correos_usuarios()

    def mostrar_mensaje(texto, color):
        page.snack_bar = ft.SnackBar(content=ft.Text(texto), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def mostrar_login(e):
        frame_login.visible = True
        frame_registro.visible = False
        logo.visible = False  # Ocultar logo al entrar
        page.update()

    def mostrar_registro(e):
        frame_login.visible = False
        frame_registro.visible = True
        logo.visible = False  # Ocultar logo al entrar
        page.update()

    def registrar_usuario(e):
        nombre = entry_nombre.value.strip()
        celular = entry_celular.value.strip()
        correo = entry_correo.value.strip()
        contraseña = entry_contraseña.value.strip()

        resultado = insertar_usuario(nombre, celular, correo, contraseña)
        mostrar_mensaje(resultado, "green" if "✅" in resultado else "red")

        if "✅" in resultado:
            for field in [entry_nombre, entry_celular, entry_correo, entry_contraseña]:
                field.value = ""
            page.update()

    def iniciar_sesion_usuario(e):
        correo = entry_correo_login.value.strip()
        contraseña = entry_contraseña_login.value.strip()

        nombre, resultado = iniciar_sesion(correo, contraseña)
        mostrar_mensaje(resultado, "green" if "✅" in resultado else "red")

        if nombre:
            logo.visible = False
            page.views.clear()
            page.controls.clear()
            page.update()
            inicio_inicio(page)

    # ----------- AUTOCOMPLETADO DE CORREO -----------

    sugerencias_column = ft.Column(spacing=4, visible=False)

    def seleccionar_sugerencia(correo):
        entry_correo_login.value = correo
        sugerencias_column.visible = False
        page.update()

    def filtrar_sugerencias(valor):
        sugerencias_column.controls.clear()
        if valor:
            sugerencias = [c for c in correos_disponibles if c.lower().startswith(valor.lower())][:5]
            for correo in sugerencias:
                sugerencias_column.controls.append(
                    ft.GestureDetector(
                        content=ft.Text(correo, color="#00BFFF", size=14, tooltip="Haz clic para completar"),
                        on_tap=lambda e, correo=correo: seleccionar_sugerencia(correo)
                    )
                )
            sugerencias_column.visible = True
        else:
            sugerencias_column.visible = False
        page.update()

    # ----------- CAMPOS DE TEXTO -----------

    entry_correo_login = ft.TextField(label="Correo", bgcolor="#333", color="white", border_color="#006dff",
                                      on_change=lambda e: filtrar_sugerencias(e.control.value))
    entry_contraseña_login = ft.TextField(label="Contraseña", password=True, bgcolor="#333", color="white", border_color="#006dff")

    entry_nombre = ft.TextField(label="Nombre", bgcolor="#333", color="white", border_color="#006dff")
    entry_celular = ft.TextField(label="Celular", bgcolor="#333", color="white", border_color="#006dff")
    entry_correo = ft.TextField(label="Correo", bgcolor="#333", color="white", border_color="#006dff")
    entry_contraseña = ft.TextField(label="Contraseña", password=True, bgcolor="#333", color="white", border_color="#006dff")

    # ----------- LOGO SOLO AL INICIO -----------

    logo = ft.Image(src=logo_path, width=180, height=180, visible=True)

    # ----------- FRAMES -----------

    frame_login = ft.Container(
        visible=False,
        content=ft.Column(
            [
                ft.Text("Iniciar Sesión", size=20, weight="bold", color="white"),
                entry_correo_login,
                sugerencias_column,
                entry_contraseña_login,
                ft.ElevatedButton("INGRESAR", bgcolor="#006dff", color="white", on_click=iniciar_sesion_usuario)
            ],
            alignment="center",
            spacing=10
        )
    )

    frame_registro = ft.Container(
        visible=False,
        content=ft.Column(
            [
                ft.Text("Crear Cuenta", size=20, weight="bold", color="white"),
                entry_nombre, entry_celular, entry_correo, entry_contraseña,
                ft.ElevatedButton("CREAR CUENTA", bgcolor="#006dff", color="white", on_click=registrar_usuario)
            ],
            alignment="center",
            spacing=10
        )
    )

    # ----------- PANEL IZQUIERDO -----------

    panel_izquierdo = ft.Container(
        width=300, height=500, bgcolor="#000", border_radius=10, padding=30,
        content=ft.Column(
            [
                ft.Text("BIENVENIDOS A", size=18, weight="bold", color="white"),
                ft.Text("RUDOLF MOTOS", size=22, weight="bold", color="#006dff"),
                ft.Text("¿Ya tienes cuenta?", size=16, color="white"),
                ft.ElevatedButton("INICIAR SESIÓN", bgcolor="#006dff", color="white", on_click=mostrar_login),
                ft.Divider(color="white"),
                ft.Text("¿Eres nuevo?", size=16, color="white"),
                ft.ElevatedButton("REGISTRARSE", bgcolor="#28A745", color="white", on_click=mostrar_registro),
                ft.Divider(color="#555"),
                ft.Text("© 2025 Rudolf Motos", size=12, color="#BBBBBB", weight="bold"),
                ft.Text("Todos los derechos reservados.", size=12, color="#BBBBBB", italic=True),
                ft.Text("Creado por JMJ.", size=12, color="#BBBBBB", italic=True),
            ],
            alignment="center",
            spacing=15
        )
    )

    # ----------- CONTENIDO PRINCIPAL -----------

    stack_contenido = ft.Stack([frame_login, frame_registro])

    page.add(
        ft.Row(
            [
                panel_izquierdo,
                ft.Row(
                    [
                        stack_contenido,
                        ft.Container(logo, alignment=ft.alignment.center, padding=20)
                    ],
                    spacing=30,
                    alignment="center"
                )
            ],
            alignment="center",
            spacing=30
        )
    )

# Lanzar app
ft.app(target=main, view=ft.WEB_BROWSER, port=8080)

