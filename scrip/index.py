import sys
import os
import flet as ft
import psycopg2
import bcrypt

# Añadir el directorio superior al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import conectar_db
from secundario.bienvenida import mostrar_bienvenida

# ---------- FUNCIONES DE BASE DE DATOS ----------
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verificar_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def insertar_usuario(nombre, apellido, celular, dni, correo, contraseña):
    try:
        hashed_password = hash_password(contraseña)
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
    except Exception as e:
        return None, f"❌ Error: {e}"

# ---------- INTERFAZ FLET ----------
def main(page: ft.Page):
    page.title = "Login y Registro"
    page.window_width = 900
    page.window_height = 500
    page.bgcolor = "#1E1E1E"

    # 📢 Función para mostrar mensajes en la UI
    def mostrar_mensaje(texto, color):
        page.snack_bar = ft.SnackBar(content=ft.Text(texto), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    # 📢 Función para mostrar Login y ocultar Imagen
    def mostrar_login(e):
        frame_login.visible = True
        imagen_bienvenida.visible = False
        frame_registro.visible = False
        page.update()

    # 📢 Función para mostrar Registro y ocultar Imagen
    def mostrar_registro(e):
        frame_login.visible = False
        imagen_bienvenida.visible = False
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

        # Limpiar campos después de registro exitoso
        if "✅" in resultado:
            entry_nombre.value = ""
            entry_apellido.value = ""
            entry_celular_reg.value = ""
            entry_dni_reg.value = ""
            entry_correo_reg.value = ""
            entry_contraseña_reg.value = ""
            page.update()

    def iniciar_sesion_usuario(e):
        correo = entry_correo_login.value.strip()
        contraseña = entry_contraseña_login.value.strip()

        nombre, resultado = iniciar_sesion(correo, contraseña)
        color = "green" if "✅" in resultado else "red"
        mostrar_mensaje(resultado, color)

        if nombre:
            mostrar_bienvenida(page, nombre, mostrar_inicio)

    def mostrar_inicio():
        frame_login.visible = False
        frame_registro.visible = False
        imagen_bienvenida.visible = True
        page.update()            

    # 📢 Formulario de Login
    entry_correo_login = ft.TextField(label="Correo", bgcolor="#333333", color="white", border_color="#006dff")
    entry_contraseña_login = ft.TextField(label="Contraseña", password=True, bgcolor="#333333", color="white", border_color="#006dff")

    frame_login = ft.Container(
        visible=False,  # 🔹 Oculto al inicio
        content=ft.Column(
            [
                ft.Text("Iniciar Sesión", size=20, weight="bold", color="white"),
                entry_correo_login,
                entry_contraseña_login,
                ft.ElevatedButton("INGRESAR", bgcolor="#006dff", color="white", on_click=iniciar_sesion_usuario)
            ],
            alignment="center",
            spacing=10
        )
    )

    # 📢 Formulario de Registro
    entry_nombre = ft.TextField(label="Nombre", bgcolor="#333333", color="white", border_color="#006dff")
    entry_apellido = ft.TextField(label="Apellido", bgcolor="#333333", color="white", border_color="#006dff")
    entry_celular_reg = ft.TextField(label="Celular", bgcolor="#333333", color="white", border_color="#006dff")
    entry_dni_reg = ft.TextField(label="DNI", bgcolor="#333333", color="white", border_color="#006dff")
    entry_correo_reg = ft.TextField(label="Correo", bgcolor="#333333", color="white", border_color="#006dff")
    entry_contraseña_reg = ft.TextField(label="Contraseña", password=True, bgcolor="#333333", color="white", border_color="#006dff")

    frame_registro = ft.Container(
        visible=False,  # 🔹 Oculto al inicio
        content=ft.Column(
            [
                ft.Text("Crear Cuenta", size=20, weight="bold", color="white"),
                entry_nombre,
                entry_apellido,
                entry_celular_reg,
                entry_dni_reg,
                entry_correo_reg,
                entry_contraseña_reg,
                ft.ElevatedButton("CREAR CUENTA", bgcolor="#006dff", color="white", on_click=registrar_usuario)
            ],
            alignment="center",
            spacing=10
        )
    )

    # 📢 Imagen que se mostrará antes de iniciar sesión
    imagen_bienvenida = ft.Container(
        visible=True,  # 🔹 Visible al inicio
        content=ft.Image(
            src="iconos/Imagen-de-WhatsApp-2025-01-22-a-las-12.47.46_9b08b1b1.ico",
            width=250,
            height=250,
            fit=ft.ImageFit.CONTAIN
        )
    )

    # 📢 Panel Izquierdo con Botones de Acceso
    panel_izquierdo = ft.Container(
        width=300,
        height=500,
        bgcolor="#000000",
        border_radius=10,
        padding=30,
        content=ft.Column(
            [
                ft.Text("BIENVENIDOS A", size=18, weight="bold", color="white"),
                ft.Text("RUDOLF MOTOS", size=22, weight="bold", color="#006dff"),  
                
                ft.Text("¿Ya tienes cuenta?", size=16, color="white"),
                ft.ElevatedButton(
                    "INICIAR SESIÓN",
                    bgcolor="#006dff",
                    color="white",
                    height=45,
                    width=200,
                    on_click=mostrar_login
                ),

                ft.Divider(color="white", thickness=1),

                ft.Text("¿Eres nuevo?", size=16, color="white"),
                ft.ElevatedButton(
                    "REGISTRARSE",
                    bgcolor="#28A745",
                    color="white",
                    height=45,
                    width=200,
                    on_click=mostrar_registro
                ),

                ft.Divider(color="#555555", thickness=1),
                ft.Text(
                    "© 2025 Rudolf Motos",
                    size=12,
                    color="#BBBBBB",
                    weight="bold",
                    text_align="center"
                ),
                ft.Text(
                    "Todos los derechos reservados.",
                    size=12,
                    color="#BBBBBB",
                    italic=True,
                    text_align="center"
                ),
            ],
            alignment="center",
            spacing=15
        )
    )

    # 📢 Sección de Formularios e Imagen (en una pila `Stack`)
    stack_contenido = ft.Stack([imagen_bienvenida, frame_login, frame_registro])

    # 📢 Contenedor Principal con el Panel Izquierdo y la Sección de Contenido
    page.add(
        ft.Row(
            [
                panel_izquierdo,
                stack_contenido  # 🔹 Imagen o Formulario según lo seleccionado
            ],
            alignment="center",
            spacing=30
        )
    )

ft.app(target=main)