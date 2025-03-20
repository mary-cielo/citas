import sys
import os
import flet as ft
import psycopg2
import re
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrip'))
from db import conectar_db

dias_seleccionados = []
mes_actual = datetime.now().month
año_actual = datetime.now().year

# Función para guardar cita en la base de datos
def guardar_cita(fecha, hora, cliente, modelo_moto, color):
    try:
        conn = conectar_db()
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM citas WHERE fecha = %s AND hora = %s", (fecha, hora))
            if cursor.fetchone():
                return "❌ La cita ya está ocupada."
            cursor.execute("INSERT INTO citas (fecha, hora, cliente, modelo_moto, color) VALUES (%s, %s, %s, %s, %s)", (fecha, hora, cliente, modelo_moto, color))
        return "✅ Cita reservada con éxito."
    except Exception as e:
        return f"❌ Error al guardar la cita: {e}"

# Función para obtener todas las citas
def obtener_citas():
    conn = conectar_db()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT fecha, hora, cliente, modelo_moto, color FROM citas ORDER BY fecha, hora")
        return cursor.fetchall()

# Función para generar el calendario
def generar_calendario(mes, año, page):
    dias = []
    primer_dia = datetime(año, mes, 1)
    primer_dia_semana = primer_dia.weekday()
    total_dias = (primer_dia + timedelta(days=32)).replace(day=1) - primer_dia
    total_dias = total_dias.days

    dias_de_la_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    dias.append(ft.Row([ft.Text(dia, color="white") for dia in dias_de_la_semana], alignment="center"))

    fila = []
    for _ in range(primer_dia_semana):
        fila.append(ft.TextButton("", disabled=True))

    for dia in range(1, total_dias + 1):
        fecha_actual = datetime(año, mes, dia)

        def _seleccionar_fecha(e, d=fecha_actual):
            seleccionar_fecha(d, page)

        dia_btn = ft.TextButton(
            str(dia),
            on_click=_seleccionar_fecha,
            style=ft.ButtonStyle(
                color={"bg": "#006dff" if fecha_actual in dias_seleccionados else "#2A2A2A", "text": "white"}
            )
        )
        fila.append(dia_btn)

        if len(fila) == 7:
            dias.append(ft.Row(fila, alignment="center"))
            fila = []

    if fila:
        while len(fila) < 7:
            fila.append(ft.TextButton("", disabled=True))
        dias.append(ft.Row(fila, alignment="center"))

    return dias

def seleccionar_fecha(fecha, page):
    if fecha in dias_seleccionados:
        dias_seleccionados.remove(fecha)
    else:
        dias_seleccionados.append(fecha)

    fecha_seleccionada.value = f"📅 {', '.join([d.strftime('%Y-%m-%d') for d in dias_seleccionados])}"
    actualizar_pagina(page)

def reservar_cita(e, page):
    fecha = fecha_seleccionada.value.replace("📅 ", "").strip()
    hora = entry_hora.value.strip()
    cliente = entry_cliente.value.strip()
    modelo_moto = entry_modelo_moto.value.strip()
    color = entry_color.value.strip()

    if not fecha or not hora or not cliente or not modelo_moto or not color:
        mensaje.value = "⚠️ Debes completar todos los campos."
        page.update()
        return

    if not re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", hora):
        mensaje.value = "⚠️ La hora debe estar en formato HH:MM (24h)."
        page.update()
        return

    resultado = guardar_cita(fecha, hora, cliente, modelo_moto, color)
    mensaje.value = resultado

    if "✅" in resultado:
        entry_cliente.value = ""
        entry_modelo_moto.value = ""
        entry_color.value = ""
        entry_hora.value = ""
        dias_seleccionados.clear()

    actualizar_pagina(page)

def cambiar_mes(cambio, page):
    global mes_actual, año_actual

    mes_actual += cambio
    if mes_actual < 1: 
        mes_actual = 12
        año_actual -= 1
    elif mes_actual > 12:
        mes_actual = 1
        año_actual += 1

    actualizar_pagina(page)

def actualizar_pagina(page):
    citas = obtener_citas()
    lista_citas.controls.clear()
    for fecha, hora, cliente, modelo_moto, color in citas:
        lista_citas.controls.append(ft.Text(f"📅 {fecha} - ⏰ {hora} - 👤 {cliente} - 🚗 {modelo_moto} - 🎨 {color}", color="white"))

    page.controls.clear()
    page.add(
        ft.Column(
            [
                ft.Row([
                    ft.ElevatedButton("<", on_click=lambda e: cambiar_mes(-1, page)),
                    ft.Text(f"{mes_actual}/{año_actual}", color="white", size=20),
                    ft.ElevatedButton(">", on_click=lambda e: cambiar_mes(1, page))  
                ], alignment="center"),

                fecha_seleccionada,
                *generar_calendario(mes_actual, año_actual, page),
                entry_hora,
                entry_cliente,
                entry_modelo_moto,
                entry_color,
                boton_reservar,
                mensaje,
                
            ],
            alignment="center",
            spacing=10
        )
    )
    page.update()

def main(page: ft.Page):
    global fecha_seleccionada, entry_hora, entry_cliente, entry_modelo_moto, entry_color, mensaje, boton_reservar, lista_citas

    page.title = "Reservar Citas"
    page.bgcolor = "#1E1E1E"

    fecha_seleccionada = ft.Text("📅 Selecciona una fecha", weight=400,color="white")
    entry_cliente = ft.TextField(label="Cliente", width=400, bgcolor="#2A2A2A", color="white", border_color="#006dff")
    entry_modelo_moto = ft.TextField(label="Modelo de la moto", width=400, bgcolor="#2A2A2A", color="white", border_color="#006dff")
    entry_color = ft.TextField(label="Color", width=400, bgcolor="#2A2A2A", color="white", border_color="#006dff")
    entry_hora = ft.TextField(label="Hora (HH:MM)", width=400, bgcolor="#2A2A2A", color="white", border_color="#006dff")
    mensaje = ft.Text("", color="white")
    lista_citas = ft.Column(spacing=5)

    boton_reservar = ft.ElevatedButton("Reservar Cita", bgcolor="#006dff", color="white", on_click=lambda e: reservar_cita(e, page))

    actualizar_pagina(page)

ft.app(target=main)