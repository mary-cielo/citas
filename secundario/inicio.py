import sys
import os
import flet as ft
from servicio.orden import crear_orden_servicio_ui  # Importamos sin circularidad
from perfil.usuario import mostrar_perfil  # Importar la función para mostrar el perfil del usuario
from citas import mostrar_citas  # Importar la función para mostrar las citas

# Constantes para los estilos
BG_COLOR = "#121212"
APP_BAR_COLOR = "#0D47A1"
PRIMARY_COLOR = "#1976D2"
SECONDARY_COLOR = "#1565C0"
TEXT_COLOR = "#BBDEFB"

def main(page: ft.Page):
    """Función principal para configurar la interfaz futurista."""
    page.title = "Tablero de Servicio"
    page.bgcolor = BG_COLOR
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    def route_change(e):
        """Maneja el cambio de ruta en la aplicación."""
        page.views.clear()
        if page.route == "/":
            page.views.append(ft.View("/", controls=[app_bar, content, footer]))
        elif page.route == "/orden":
            page.views.append(ft.View("/orden", controls=[app_bar, crear_orden_servicio_ui(page, app_bar, footer)]))
        elif page.route == "/usuario":
            mostrar_perfil(page)
        elif page.route == "/citas":  
            page.views.append(ft.View("/citas", controls=[app_bar, mostrar_citas(page), footer]))  
        page.update()

    # Crear componentes de la interfaz
    app_bar = create_app_bar(page)
    content = create_content(page)  # Crea el contenido del tablero
    footer = create_footer(page)

    page.on_route_change = route_change
    # Al iniciar, redirige a la ruta del tablero
    page.go("/")

def create_app_bar(page: ft.Page) -> ft.AppBar:
    """Crea la barra de aplicación."""
    profile_icon = ft.IconButton(
        icon=ft.icons.ACCOUNT_CIRCLE, icon_size=35, icon_color="#2196F3",
        on_click=lambda e: page.go("/usuario"),
    )
    menu_button = create_menu_button()

    return ft.AppBar(
        bgcolor=APP_BAR_COLOR,
        leading=profile_icon,
        title=ft.Text("TABLERO", size=26, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
        center_title=True,
        actions=[menu_button],
    )

def create_content(page: ft.Page) -> ft.Container:
    """Crea el contenido principal de la aplicación."""
    return ft.Container(
        padding=40,
        border_radius=20,
        content=ft.Column(
            [
                ft.Text("Bienvenido al Tablero", size=30, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton(
                    text="Crear Orden de Servicio",
                    on_click=lambda e: page.go("/orden"),
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE,
                        bgcolor=PRIMARY_COLOR,
                        shape=ft.RoundedRectangleBorder(radius=15),
                    ),
                ),
                ft.ElevatedButton(
                    text="Ver Perfil",
                    on_click=lambda e: page.go("/usuario"),
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE,
                        bgcolor=SECONDARY_COLOR,
                        shape=ft.RoundedRectangleBorder(radius=15),
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=25,
        ),
    )

def create_footer(page: ft.Page) -> ft.Container:
    """Crea el pie de página de la aplicación."""
    return ft.Container(
        bgcolor=APP_BAR_COLOR,
        padding=15,
        alignment=ft.alignment.center,
        content=ft.Row(
            controls=[
                ft.ElevatedButton(
                    text="Inicio", icon=ft.icons.HOME,
                    on_click=lambda e: page.go("/"),
                    style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=PRIMARY_COLOR),
                ),
                ft.ElevatedButton(
                    text="Servicios", icon=ft.icons.DESIGN_SERVICES,
                    on_click=lambda e: print("Servicios"),
                    style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=PRIMARY_COLOR),
                ),
                ft.ElevatedButton(
                    text="Citas", icon=ft.icons.CALENDAR_TODAY,
                    on_click=lambda e: page.go("/citas"),
                    style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=PRIMARY_COLOR),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            spacing=15,
        ),
    )

def create_menu_button() -> ft.PopupMenuButton:
    """Crea un botón de menú con un ícono de hamburguesa futurista."""
    return ft.PopupMenuButton(
        icon=ft.icons.MENU,
        icon_color=TEXT_COLOR,
        items=[
            ft.PopupMenuItem(text="Eventos", on_click=lambda e: print("eventos")),
            ft.PopupMenuItem(text="Opción 2", on_click=lambda e: print("Seleccionaste Opción 2")),
            ft.PopupMenuItem(text="Opción 3", on_click=lambda e: print("Seleccionaste Opción 3")),
        ],
    )

ft.app(target=main)