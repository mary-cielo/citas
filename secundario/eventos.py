import flet as ft
import os
import sys
import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrip'))
from db import conectar_db

TIEMPO_RECORDATORIO = 15  # Tiempo antes de la cita para enviar recordatorio

def cargar_citas():
    """Carga las citas desde la base de datos."""
    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, fecha, hora, cliente, recordatorio_enviado FROM citas ORDER BY fecha, hora")
            return cursor.fetchall()
    except Exception as e:
        print(f"❌ Error al cargar las citas: {e}")
        return []

def eliminar_cita(cita_id, page):
    """Elimina una cita de la base de datos."""
    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM citas WHERE id = %s", (cita_id,))
            conn.commit()

        page.snack_bar = ft.SnackBar(content=ft.Text("✅ Cita eliminada correctamente."), bgcolor="green")
        page.snack_bar.open = True
    except Exception as e:
        print(f"❌ Error al eliminar la cita: {e}")

def actualizar_cita(cita_id, nueva_fecha, nueva_hora, page):
    """Actualiza la fecha y hora de una cita."""
    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE citas SET fecha = %s, hora = %s, reprogramada = TRUE WHERE id = %s", 
                           (nueva_fecha, nueva_hora, cita_id))
            conn.commit()

        page.snack_bar = ft.SnackBar(content=ft.Text("🔄 Cita reprogramada con éxito."), bgcolor="blue")
        page.snack_bar.open = True
    except Exception as e:
        print(f"❌ Error al actualizar la cita: {e}")

def confirmar_asistencia(cita_id, page):
    """Marca la cita como asistida antes de eliminarla."""
    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE citas SET asistio = TRUE WHERE id = %s", (cita_id,))
            conn.commit()
            cursor.execute("DELETE FROM citas WHERE id = %s", (cita_id,))
            conn.commit()

        page.snack_bar = ft.SnackBar(content=ft.Text("✅ Asistencia confirmada y cita eliminada."), bgcolor="green")
        page.snack_bar.open = True
    except Exception as e:
        print(f"❌ Error al confirmar asistencia: {e}")

def enviar_recordatorio(cita_id, cliente, page):
    """Envía un recordatorio si aún no ha sido enviado."""
    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT recordatorio_enviado FROM citas WHERE id = %s", (cita_id,))
            recordatorio_enviado = cursor.fetchone()[0]

            if not recordatorio_enviado:
                page.snack_bar = ft.SnackBar(content=ft.Text(f"⏳ {cliente} tiene una cita en 15 minutos."), bgcolor="orange")
                page.snack_bar.open = True
                cursor.execute("UPDATE citas SET recordatorio_enviado = TRUE WHERE id = %s", (cita_id,))
                conn.commit()
    except Exception as e:
        print(f"❌ Error al enviar recordatorio: {e}")

def abrir_modal_reagendar(cita_id, page):
    """Abre un modal para reagendar una cita."""
    nueva_fecha = ft.TextField(label="Nueva Fecha (YYYY-MM-DD)", bgcolor="#333333", color="white")
    nueva_hora = ft.TextField(label="Nueva Hora (HH:MM:SS)", bgcolor="#333333", color="white")

    def confirmar_reagendado(ev):
        if nueva_fecha.value and nueva_hora.value:
            actualizar_cita(cita_id, nueva_fecha.value, nueva_hora.value, page)
            page.dialog.open = False
            page.update()

    page.dialog = ft.AlertDialog(
        title=ft.Text("Reagendar Cita"),
        content=ft.Column([nueva_fecha, nueva_hora]),
        actions=[
            ft.TextButton("Confirmar", on_click=confirmar_reagendado),
            ft.TextButton("Cancelar", on_click=lambda e: setattr(page.dialog, 'open', False))
        ],
        open=True
    )
    page.update()

def main(page: ft.Page):
    page.title = "📅 Listado de Citas"
    page.bgcolor = "#1E1E1E"
    page.scroll = "adaptive"

    citas = cargar_citas()
    lista_citas = ft.Column([], scroll="auto", spacing=10)  # Activar el scroll automático
    ahora = datetime.datetime.now()

    for cita_id, fecha, hora, cliente, recordatorio_enviado in citas:
        fecha_hora_cita = datetime.datetime.combine(fecha, hora)
        tiempo_faltante = (fecha_hora_cita - ahora).total_seconds() / 60  # Diferencia en minutos

        if tiempo_faltante < 0:
            bgcolor = "#FF3B30"
        elif 0 <= tiempo_faltante <= TIEMPO_RECORDATORIO and not recordatorio_enviado:
            bgcolor = "#FFD60A"
            enviar_recordatorio(cita_id, cliente, page)
        else:
            bgcolor = "#2A2A2A"

        cita_text = ft.Text(f"{fecha} {hora} - {cliente}", color="white", size=16)

        cita_card = ft.Container(
            content=ft.Column([
                cita_text,
                ft.Row([
                    ft.ElevatedButton("✅ Asistió", bgcolor="#28A745", color="white", 
                                      on_click=lambda e, c=cita_id: confirmar_asistencia(c, page)),
                    ft.ElevatedButton("🔄 Reagendar", bgcolor="#007BFF", color="white", 
                                      on_click=lambda e, c=cita_id: abrir_modal_reagendar(c, page)),
                    ft.ElevatedButton("❌ Cancelar", bgcolor="#FF3B30", color="white", 
                                      on_click=lambda e, c=cita_id: eliminar_cita(c, page))
                ], alignment="center", spacing=5)
            ]),
            bgcolor=bgcolor,
            padding=10,
            margin=5,
            border_radius=8,
            border=ft.border.all(1, "#006dff")
        )
        lista_citas.controls.append(cita_card)

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("📅 Listado de Citas", color="white", size=24, weight="bold"),
                lista_citas
            ], alignment="center", spacing=10),
            expand=True  # Permite que la columna use todo el espacio disponible y active el scroll si es necesario
        )
    )

ft.app(target=main)