import flet as ft
import psycopg2
import os
import sys

# Agrega la ruta correcta para importar db.py
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scrip'))
from db import conectar_db  # Importa la conexión desde db.py

# 🎨 Colores personalizados
BG_COLOR = "#121212"
CARD_COLOR = "#1E1E1E"
TEXT_COLOR = "#BBDEFB"
HIGHLIGHT_COLOR = "#03A9F4"
APP_BAR_COLOR = "#0D47A1"

def obtener_clientes():
    """Obtiene la lista de clientes ordenados del último al primero."""
    conn = conectar_db()
    if conn is None:
        print("Error: No se pudo conectar a la base de datos.")
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT cliente_nombre, cliente_dni, cliente_telefono, 
                   vehiculo_marca, vehiculo_modelo
            FROM ordenes_servicio
            ORDER BY cliente_dni DESC;  -- 📌 Ordenamos del último al primero
        """)
        clientes = cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener clientes: {e}")
        clientes = []
    finally:
        conn.close()
    
    return clientes

def obtener_clientes_ui(page: ft.Page):
    """Genera la interfaz de clientes con tarjetas visuales y una tabla con opción de cambio."""
    clientes = obtener_clientes()
    
    vista_tabla = False  # Controlador de vista
    contenido = ft.Container(
        content=ft.Column(scroll=ft.ScrollMode.AUTO, expand=True),
        alignment=ft.alignment.center,  # Centrar el contenedor
        expand=True,
    )

    def actualizar_vista(e):
        """Cambia entre vista de tarjetas y tabla."""
        nonlocal vista_tabla
        vista_tabla = not vista_tabla
        renderizar_contenido()

    def renderizar_contenido():
        """Renderiza la vista seleccionada."""
        if vista_tabla:
            nuevo_contenido = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.DataTable(
                            columns=[
                                ft.DataColumn(ft.Text("Cliente")),
                                ft.DataColumn(ft.Text("DNI")),
                                ft.DataColumn(ft.Text("Teléfono")),
                                ft.DataColumn(ft.Text("Vehículo")),
                            ],
                            rows=[
                                ft.DataRow(
                                    cells=[
                                        ft.DataCell(ft.Text(cliente[0])),
                                        ft.DataCell(ft.Text(cliente[1])),
                                        ft.DataCell(ft.Text(cliente[2])),
                                        ft.DataCell(ft.Text(f"{cliente[3]} {cliente[4]}")),
                                    ]
                                ) for cliente in clientes
                            ]
                        )
                    ],
                    scroll=ft.ScrollMode.AUTO,  # Agregar scroll
                    alignment=ft.MainAxisAlignment.CENTER,  # Centrar la tabla
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
                expand=True
            )
        else:
            tarjetas = [
                ft.Container(
                    content=ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text(f"Cliente: {cliente[0]}", color=TEXT_COLOR, size=18, weight=ft.FontWeight.BOLD),
                                ft.Text(f"DNI: {cliente[1]}", color=TEXT_COLOR),
                                ft.Text(f"Teléfono: {cliente[2]}", color=TEXT_COLOR),
                                ft.Divider(color=HIGHLIGHT_COLOR),
                                ft.Text(f"Vehículo: {cliente[3]} {cliente[4]}", color=HIGHLIGHT_COLOR, size=16, italic=True)
                            ], spacing=10),
                            padding=20,
                            bgcolor=CARD_COLOR,
                            border_radius=15,
                        )
                    ),
                    alignment=ft.alignment.center  # Centrar tarjetas
                ) for cliente in clientes
            ]
            nuevo_contenido = ft.Column(
                controls=tarjetas,
                spacing=10,
                expand=True,
                scroll=ft.ScrollMode.AUTO  # Agregar scroll
            )

        contenido.content = nuevo_contenido
        page.update()

    boton_volver = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        icon_color=TEXT_COLOR,
        icon_size=30,
        tooltip="Regresar",
        on_click=lambda e: page.go("/")
    )

    boton_cambiar_vista = ft.IconButton(
        icon=ft.Icons.VIEW_LIST,
        icon_color=TEXT_COLOR,
        icon_size=30,
        tooltip="Cambiar Vista",
        on_click=actualizar_vista
    )

    renderizar_contenido()

    return ft.Container(
        bgcolor=BG_COLOR,
        expand=True,
        padding=20,
        content=ft.Column(
            [
                ft.Row(
                    [boton_volver, ft.Text("Lista de Clientes", size=24, color=TEXT_COLOR, weight=ft.FontWeight.BOLD), boton_cambiar_vista],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                contenido  # Ahora el contenido está centrado y tiene scroll
            ],
            spacing=20,
            alignment=ft.alignment.center  # Centrar todo
        ),
    )

# Corregir la sintaxis de esta línea:
if __name__ == "__main__":  # Faltaba el `:` en esta línea
    ft.app(target=obtener_clientes_ui)  # Ejecuta la aplicación Flet
ft.app(target=main)    
