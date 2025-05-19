import flet as ft
from datetime import datetime, timedelta
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scrip'))
from db import conectar_db

BG_COLOR = "#121212"
APP_BAR_COLOR = "#0D47A1"
PRIMARY_COLOR = "#1976D2"
TEXT_COLOR = "#BBDEFB"
CARD_COLOR = "#1E1E1E"
BUTTON_RADIUS = 10

def mostrar_formulario_nueva_cita(page: ft.Page):
    """Muestra el formulario para agendar una nueva cita en una nueva página con estilo mejorado."""

    fecha_picker = ft.TextField(label="Fecha", read_only=True, bgcolor="#2A2A2A", color="white")
    hora_picker = ft.TextField(label="Hora", read_only=True, bgcolor="#2A2A2A", color="white")
    cliente = ft.TextField(label="Cliente", bgcolor="#2A2A2A", color="white")
    celular = ft.TextField(label="Celular", bgcolor="#2A2A2A", color="white", max_length=9) 
    placa = ft.TextField(label="Placa", bgcolor="#2A2A2A", color="white")
    modelo = ft.TextField(label="Modelo de la moto", bgcolor="#2A2A2A", color="white")
    color = ft.TextField(label="Color", bgcolor="#2A2A2A", color="white")
    mensaje = ft.Text("", color=TEXT_COLOR)

    fecha_picker.value = datetime.now().strftime("%Y-%m-%d")
    hora_picker.value = datetime.now().strftime("%H:%M")

    def actualizar_fecha(e):
        fecha_picker.value = e.control.value.strftime("%Y-%m-%d")
        page.update()

    def retroceder_fecha(e):
        """Retrocede un día al hacer clic en el botón en la AppBar."""
        fecha_actual = datetime.strptime(fecha_picker.value, "%Y-%m-%d")
        nueva_fecha = fecha_actual - timedelta(days=1)
        fecha_picker.value = nueva_fecha.strftime("%Y-%m-%d")
        page.update()

    def actualizar_hora(e):
        hora_picker.value = e.control.value.strftime("%H:%M")
        page.update()

    date_picker = ft.DatePicker(on_change=actualizar_fecha)
    time_picker = ft.TimePicker(on_change=actualizar_hora)

    page.overlay.append(date_picker)
    page.overlay.append(time_picker)

    def abrir_fecha(e):
        date_picker.open = True
        page.update()

    def abrir_hora(e):
        time_picker.open = True
        page.update()

    def verificar_cita_existente(fecha, hora):
        """Verifica si ya existe una cita con la misma fecha y hora."""
        try:
            conn = conectar_db()
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM citas WHERE fecha = %s AND hora = %s",
                    (fecha, hora)
                )
                resultado = cursor.fetchone()
                return resultado[0] > 0
        except Exception as ex:
            mensaje.value = f"❌ Error al verificar cita: {str(ex)}"
            page.update()
            return False

    def mostrar_modal_errores(page, mensaje_error):
        """Muestra un modal con el mensaje de error y bloquea la interacción hasta que se cierre."""
        modal = ft.AlertDialog(
            title=ft.Text("Error: Cita ya agendada"),
            content=ft.Text(mensaje_error),
            actions=[ 
                ft.ElevatedButton("Aceptar", on_click=lambda e: cerrar_modal(page, modal))  
            ]
        )
        page.overlay.append(modal)
        modal.open = True
        page.update()

    def cerrar_modal(page, modal):
        """Cierra el modal y permite la interacción con la vista."""
        modal.open = False
        page.update()

    def reservar_cita(e):
        """Guarda la cita en la base de datos si no hay conflictos y retrocede a la página anterior automáticamente."""
        valores = [fecha_picker.value, hora_picker.value, cliente.value, celular.value, placa.value, modelo.value, color.value]
        if not all(valores):
            mensaje.value = "⚠ Debes completar todos los campos."
            page.update()
            return
        if not celular.value.isdigit() or len(celular.value) != 9:
            mensaje.value = "⚠ El número de celular debe ser de 9 dígitos."
            page.update()
            return

        if verificar_cita_existente(fecha_picker.value, hora_picker.value):
            mostrar_modal_errores(page, "La cita ya está agendada para esa fecha y hora. Elija otra fecha y hora.")
            return

        try:
            conn = conectar_db()
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO citas (fecha, hora, cliente, celular_cliente, placa, modelo_moto, color)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    valores
                )
                conn.commit()
            mensaje.value = "✅ Cita reservada con éxito."
            for campo in [fecha_picker, hora_picker, cliente, celular, placa, modelo, color]:
                campo.value = ""
        except Exception as ex:
            mensaje.value = f"❌ Error: {str(ex)}"
        finally:
            page.update()

            # Limpiar las vistas y redirigir a la vista de citas de forma clara
            page.views.clear()  # Limpiar cualquier vista previa
            from citas.citas import mostrar_citas  # Importar la función que muestra las citas
            mostrar_citas(page)  # Llamar la función que mostrará las citas en la página principal
            page.update()

    formulario = ft.Column([        
        ft.Row([fecha_picker, ft.IconButton(icon=ft.icons.CALENDAR_MONTH_OUTLINED, on_click=abrir_fecha)]),  
        ft.Row([hora_picker, ft.IconButton(icon=ft.icons.ACCESS_TIME_OUTLINED, on_click=abrir_hora)]),
        cliente, celular, placa, modelo, color,
        ft.Row([            
            ft.ElevatedButton(
                "Guardar Cita", 
                on_click=reservar_cita, 
                bgcolor=PRIMARY_COLOR, 
                color=TEXT_COLOR
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        mensaje
    ], spacing=10)

    # Flecha para regresar a la vista de citas
    app_bar_buttons = [
        ft.IconButton(
            icon=ft.icons.ARROW_BACK,
            on_click=lambda e: page.go("/citas"), 
            icon_color=TEXT_COLOR
        )
    ]

    # Agregar la vista de nueva cita
    page.views.append(ft.View("/nueva_cita", [
        ft.AppBar(
            title=ft.Text("Nueva Cita"), 
            bgcolor=APP_BAR_COLOR, 
            leading=app_bar_buttons[0] 
        ),
        ft.Container(content=formulario, padding=20)
    ]))
    page.update()
