import flet as ft
import sys
import os
import asyncio  # Para manejar operaciones asíncronas

# Ajustar la ruta para importar db correctamente
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scrip'))
from db import conectar_db

async def obtener_usuario(usuario_id):
    """Obtiene los datos del usuario desde la base de datos."""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("SELECT nombre, apellido, correo, dni, celular FROM usuario WHERE id = %s", (usuario_id,))
        usuario = cursor.fetchone()

        cursor.close()
        conn.close()

        if usuario:
            return {
                "nombre": usuario[0],
                "apellido": usuario[1],
                "correo": usuario[2],
                "dni": usuario[3],
                "celular": usuario[4],
            }
        else:
            return None

    except Exception as e:
        print(f"❌ Error al obtener los datos del usuario: {e}")
        return None

def mostrar_perfil(page, usuario_id=1):
    """Muestra el perfil del usuario en la interfaz principal con un diseño moderno."""
    
    async def cargar_usuario():
        usuario = await obtener_usuario(usuario_id)
        
        # Limpiar la pantalla antes de mostrar la información
        page.views.clear()
        
        if usuario:
            # Crear la vista del perfil con diseño futurista
            perfil_view = ft.View(
                "/usuario",
                controls=[
                    ft.AppBar(
                        title=ft.Text("Perfil de Usuario", size=26, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                        bgcolor=ft.colors.BLUE_900,
                        center_title=True,
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Icon(name=ft.icons.ACCOUNT_CIRCLE, size=120, color=ft.colors.LIGHT_BLUE),
                                ft.Text(f"{usuario['nombre']} {usuario['apellido']}", size=26, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
                                ft.Divider(color=ft.colors.BLUE_ACCENT, thickness=2),
                                ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Row(
                                                [
                                                    ft.Icon(ft.icons.EMAIL, color=ft.colors.CYAN),
                                                    ft.Text(usuario['correo'], size=18, color=ft.colors.WHITE)
                                                ],
                                                alignment=ft.MainAxisAlignment.START,
                                            ),
                                            ft.Row(
                                                [
                                                    ft.Icon(ft.icons.CREDIT_CARD, color=ft.colors.CYAN),
                                                    ft.Text(usuario['dni'], size=18, color=ft.colors.WHITE)
                                                ],
                                                alignment=ft.MainAxisAlignment.START,
                                            ),
                                            ft.Row(
                                                [
                                                    ft.Icon(ft.icons.PHONE, color=ft.colors.CYAN),
                                                    ft.Text(usuario['celular'], size=18, color=ft.colors.WHITE)
                                                ],
                                                alignment=ft.MainAxisAlignment.START,
                                            ),
                                        ],
                                        spacing=10,
                                    ),
                                    padding=15,
                                    border_radius=12,
                                    bgcolor=ft.colors.GREY_800,
                                    shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.BLUE_700, spread_radius=2),
                                ),
                                ft.ElevatedButton(
                                    text="Volver",
                                    icon=ft.icons.ARROW_BACK,
                                    on_click=lambda e: page.go("/"),
                                    style=ft.ButtonStyle(
                                        color=ft.colors.WHITE, 
                                        bgcolor=ft.colors.BLUE_700,
                                        shape=ft.RoundedRectangleBorder(radius=10),
                                        elevation=3,
                                    ),
                                ),
                            ],
                            spacing=20,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        padding=30,
                        border_radius=20,
                        bgcolor=ft.colors.GREY_900,
                        margin=20,
                        shadow=ft.BoxShadow(blur_radius=20, color=ft.colors.BLUE_700, spread_radius=4),
                    )
                ]
            )
            page.views.append(perfil_view)
        else:
            page.views.append(ft.Text("⚠️ Usuario no encontrado", color=ft.colors.RED_400, size=18))

        page.update()

    # Ejecutar la función asíncrona para cargar datos del usuario
    asyncio.run(cargar_usuario())
