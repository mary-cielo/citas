import flet as ft
import os
import sys
from datetime import datetime, date, time

# Configuración
NUMERO_COLUMNAS = 2  

# Rutas
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scrip'))
from db import conectar_db

# Colores
COLOR_BOTON_ASISTIO = "#28A745"
COLOR_BOTON_REAGENDAR = "#007BFF"
COLOR_BOTON_CANCELAR = "#FF3B30"
COLOR_BOTON_NO_ASISTIO = "#FFA500"
COLOR_FONDO_TARJETA = "#2A2A2A"
COLOR_FONDO_PAGINA = "#1E1E1E"
COLOR_TEXTO = "white"
COLOR_BORDE_TARJETA = "#007BFF"

# ========================== FUNCIONES BASE DE DATOS ==========================

def cargar_citas():
    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, cliente, fecha, hora, reprogramada_fecha, reprogramada_hora,
                       modelo_moto, color, placa, celular_cliente
                FROM citas 
                WHERE asistio = false
                ORDER BY fecha, hora
            """)
            citas_raw = cursor.fetchall()
            citas = []
            for c in citas_raw:
                c = list(c)
                c[3] = c[3].strftime('%H:%M') if c[3] else "00:00"
                c[5] = c[5].strftime('%H:%M') if c[5] else "00:00"
                citas.append(c)
            return citas
    except Exception as e:
        print(f"❌ Error al cargar citas: {e}")
        return []

def actualizar_estado_asistencia(id: int, asistio: bool, page: ft.Page):
    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE citas SET asistio = %s WHERE id = %s", (asistio, id))
            conn.commit()
        print(f"✅ Cita {id} actualizada: {'Asistió' if asistio else 'No asistió'}")
        recargar_pagina(page)
    except Exception as e:
        print(f"❌ Error al actualizar asistencia: {e}")

def actualizar_cita(id: int, nueva_fecha: str, nueva_hora: str, page: ft.Page):
    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE citas 
                SET reprogramada_fecha = %s, reprogramada_hora = %s 
                WHERE id = %s
            """, (nueva_fecha, nueva_hora, id))
            conn.commit()
        print(f"✅ Cita {id} reagendada para {nueva_fecha} a las {nueva_hora}")
        recargar_pagina(page)
    except Exception as e:
        print(f"❌ Error al reagendar: {e}")

def recargar_pagina(page: ft.Page):
    page.clean()
    page.add(mostrar_reservas(page))

# ========================== UI: REAGENDAR ==========================

def abrir_pestana_reagendar(id: int, page: ft.Page):
    citas = cargar_citas()
    cita_actual = next((c for c in citas if c[0] == id), None)

    fecha_actual = str(cita_actual[2]) if cita_actual else datetime.now().strftime("%Y-%m-%d")
    hora_actual = str(cita_actual[3]) if cita_actual else datetime.now().strftime("%H:%M")

    mensaje = ft.Text("", color=COLOR_TEXTO)
    fecha_picker = ft.TextField(label="Fecha", value=fecha_actual, read_only=True, bgcolor="#2A2A2A", color="white")
    hora_picker = ft.TextField(label="Hora", value=hora_actual, read_only=True, bgcolor="#2A2A2A", color="white")

    def actualizar_fecha(e):
        fecha_picker.value = e.control.value.strftime("%Y-%m-%d")
        page.update()

    def actualizar_hora(e):
        hora_picker.value = e.control.value.strftime("%H:%M")
        page.update()

    def confirmar_reagendado(e):
        if not fecha_picker.value or not hora_picker.value:
            mensaje.value = "⚠️ Debes seleccionar fecha y hora."
            page.update()
            return

        try:
            nueva_fecha = datetime.strptime(fecha_picker.value, "%Y-%m-%d").date()
            nueva_hora = datetime.strptime(hora_picker.value, "%H:%M").time()
            ahora = datetime.now()

            if datetime.combine(nueva_fecha, nueva_hora) < ahora:
                mensaje.value = "⚠️ No puedes reagendar a una fecha y hora pasada."
                page.update()
                return

            actualizar_cita(id, fecha_picker.value, hora_picker.value, page)
            page.views.pop()
        except Exception as ex:
            mensaje.value = f"❌ Error: {ex}"
            page.update()

    def cancelar_reagendar(e):
        page.views.pop()
        recargar_pagina(page)

    date_picker = ft.DatePicker(on_change=actualizar_fecha, first_date=date.today())
    time_picker = ft.TimePicker(on_change=actualizar_hora)

    page.overlay.extend([date_picker, time_picker])

    page.views.append(
        ft.View(
            route=f"/reagendar/{id}",
            controls=[ft.Container(
                content=ft.Column([  
                    ft.Text("🔄 Reagendar Cita", size=26, weight="bold", color=COLOR_TEXTO),
                    ft.Row([fecha_picker, ft.IconButton(icon=ft.icons.CALENDAR_MONTH, on_click=lambda _: abrir_fecha(), icon_color=COLOR_TEXTO)]),
                    ft.Row([hora_picker, ft.IconButton(icon=ft.icons.ACCESS_TIME, on_click=lambda _: abrir_hora(), icon_color=COLOR_TEXTO)]),
                    ft.Row([  
                        ft.ElevatedButton("Confirmar", bgcolor=COLOR_BOTON_REAGENDAR, color=COLOR_TEXTO, on_click=confirmar_reagendado),
                        ft.ElevatedButton("Cancelar", bgcolor=COLOR_BOTON_CANCELAR, color=COLOR_TEXTO, on_click=cancelar_reagendar)
                    ], alignment="center", spacing=10),
                    mensaje
                ], spacing=20, alignment="center"),
                bgcolor=COLOR_FONDO_PAGINA,
                padding=20,
                border_radius=12
            )],
            bgcolor=COLOR_FONDO_PAGINA
        )
    )
    page.update()

    def abrir_fecha(): date_picker.open = True; page.update()
    def abrir_hora(): time_picker.open = True; page.update()

# ========================== UI: MOSTRAR CITAS ==========================

def mostrar_reservas(page: ft.Page):
    citas = cargar_citas()
    if not citas:
        return ft.Container(
            content=ft.Text("📭 No hay citas pendientes", color=COLOR_TEXTO, size=20),
            alignment=ft.alignment.center,
            padding=30
        )

    columnas = [[] for _ in range(NUMERO_COLUMNAS)]

    for index, cita in enumerate(citas):
        id, cliente, fecha, hora, rep_fecha, rep_hora, modelo, color, placa, celular = cita

        fue_reprogramada = str(rep_fecha) != str(fecha) or str(rep_hora) != str(hora)
        fecha_mostrar = rep_fecha if fue_reprogramada else fecha
        hora_mostrar = rep_hora if fue_reprogramada else hora
        info_reprogramada = f"🔁 Reprogramado de {fecha} {hora}" if fue_reprogramada else ""

        botones = ft.Row([
            ft.ElevatedButton("Asistió", icon=ft.icons.CHECK, bgcolor=COLOR_BOTON_ASISTIO, color=COLOR_TEXTO,
                              on_click=lambda e, id=id: actualizar_estado_asistencia(id, True, page)),
            ft.ElevatedButton("No Asistió", icon=ft.icons.BLOCK, bgcolor=COLOR_BOTON_NO_ASISTIO, color=COLOR_TEXTO,
                              on_click=lambda e, id=id: actualizar_estado_asistencia(id, False, page)),
            ft.ElevatedButton("Reagendar", icon=ft.icons.UPDATE, bgcolor=COLOR_BOTON_REAGENDAR, color=COLOR_TEXTO,
                              on_click=lambda e, id=id: abrir_pestana_reagendar(id, page))
        ], alignment="center", spacing=10)

        tarjeta = ft.Container(
            content=ft.Column([
                ft.Text(f"👤 Cliente: {cliente}", color=COLOR_TEXTO),
                ft.Text(f"📅 Fecha: {fecha_mostrar} - 🕒 Hora: {hora_mostrar}", color=COLOR_TEXTO),
                ft.Text(info_reprogramada, color="#AAAAAA"),
                ft.Text(f"🏍️ Moto: {modelo} | 🎨 Color: {color} | 🔢 Placa: {placa}", color=COLOR_TEXTO),
                ft.Text(f"📞 Celular: {celular}", color=COLOR_TEXTO),
                botones
            ], spacing=8),
            bgcolor=COLOR_FONDO_TARJETA,
            padding=15,
            border_radius=10,
            border=ft.border.all(2, COLOR_BORDE_TARJETA),
            shadow=ft.BoxShadow(blur_radius=8, spread_radius=1, color=ft.colors.with_opacity(0.3, COLOR_BOTON_REAGENDAR)),
        )

        columnas[index % NUMERO_COLUMNAS].append(tarjeta)

    return ft.Column(
        controls=[
            ft.Text("📋 Citas Pendientes", size=24, weight="bold", color=COLOR_TEXTO),
            ft.Row(
                controls=[ft.Column(col, spacing=15, expand=True) for col in columnas],
                alignment="spaceEvenly",
                tight=True
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=25
    )

# ========================== MAIN ==========================

def main(page: ft.Page):
    page.scroll = "adaptive"
    page.bgcolor = COLOR_FONDO_PAGINA
    page.title = "Gestión de Citas"
    page.add(mostrar_reservas(page))

if __name__ == "__main__":
    ft.app(target=main)
