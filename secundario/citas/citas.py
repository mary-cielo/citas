import flet as ft
from db import conectar_db  # Asegúrate de configurar correctamente la conexión
from citas.citas2 import mostrar_formulario_nueva_cita 
 # Importación de la función correcta

# Estilos y colores
BG_COLOR = "#121212"
APP_BAR_COLOR = "#0D47A1"
PRIMARY_COLOR = "#1976D2"
TEXT_COLOR = "#BBDEFB"
CARD_COLOR = "#1E1E1E"

def mostrar_citas(page: ft.Page):
    """Muestra la interfaz de citas con scroll y botón para añadir citas."""

    def obtener_citas():
        """Obtiene todas las citas de la base de datos ordenadas de más reciente a más antigua."""
        conn = conectar_db()
        with conn:
            cursor = conn.cursor()
            # Modificar la consulta para ordenar las citas por fecha y hora en orden descendente
            cursor.execute("SELECT id, fecha, hora, cliente, celular_cliente, placa, modelo_moto, color FROM citas ORDER BY fecha DESC, hora DESC")
            return cursor.fetchall()

    def actualizar_pagina():
        """Actualiza la lista de citas mostrando las más recientes primero."""
        citas = obtener_citas()
        lista_citas.controls.clear()  # Limpiar las citas actuales para evitar duplicados
        for cita in citas:
            lista_citas.controls.append(
                ft.Card(
                    elevation=5,
                    content=ft.Container(
                        padding=15,
                        bgcolor=CARD_COLOR,
                        border_radius=10,
                        content=ft.Row([  
                            ft.Column([
                                ft.Text(f"\ud83d\udcc5 {cita[1]} ⏰ {cita[2]}", color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                                ft.Text(f"\ud83d\udc64 Cliente: {cita[3]} \ud83d\udcde {cita[4]}", color=TEXT_COLOR),
                                ft.Text(f"\ud83d\ude97 Placa: {cita[5]} - Modelo: {cita[6]} \ud83c\udfa8 {cita[7]}", color=TEXT_COLOR),
                            ], expand=True),
                        ])
                    )
                )
            )
        page.update()

    # Botón para abrir el formulario de otra pantalla
    boton_agregar = ft.FloatingActionButton(
        text="Añadir Cita",
        icon=ft.icons.ADD,
        bgcolor=PRIMARY_COLOR,
        on_click=lambda e: mostrar_formulario_nueva_cita(page)  # Llama a la función del otro archivo
    )

    lista_citas = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    actualizar_pagina()

    footer = ft.Container(
        content=ft.Container(
            content=ft.Text("© 2025 Aplicación de Citas Rudolfs", color=TEXT_COLOR, size=12),
            alignment=ft.alignment.center
        ),
        padding=10,
        alignment=ft.alignment.center
    )

    return ft.Column([
        ft.Container(content=boton_agregar, alignment=ft.alignment.center, padding=10),
        ft.Container(content=lista_citas, height=500, expand=True),
        footer
    ], expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)