import flet as ft
import pandas as pd
import re
import sys
import os
from datetime import datetime

# Rutas e importaciones
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scrip'))
from db import conectar_db

# =========================== UTILIDADES ===========================
def limpiar_descripciones(texto):
    if not texto:
        return ""
    return re.sub(r'\s*\(.*?\)', '', texto).strip()

COLOR_TEXTO = "#BBDEFB"
COLOR_FONDO_TARJETA = "#1E1E1E"
COLOR_BORDE_TARJETA = "#90CAF9"
COLOR_BOTON = "#1976D2"
COLOR_SOMBRA = "#BBDEFB"

# =========================== DATOS ===========================
def obtener_opciones_mecanico():
    try:
        with conectar_db() as conn:
            df = pd.read_sql("SELECT DISTINCT mecanico_nombre FROM ordenes_servicio WHERE mecanico_nombre IS NOT NULL", conn)
            return ["Todos"] + df['mecanico_nombre'].dropna().tolist()
    except Exception as e:
        print(f"Error al obtener los mecánicos: {e}")
        return ["Todos"]

def obtener_datos_ordenes(mecanico, mes=None, fecha_inicio=None, fecha_fin=None):
    try:
        with conectar_db() as conn:
            query = "SELECT * FROM ordenes_servicio WHERE mecanico_nombre IS NOT NULL"
            filters = []
            params = []

            if mecanico and mecanico != "Todos":
                filters.append("mecanico_nombre = %s")
                params.append(mecanico)

            if mes:
                filters.append("EXTRACT(MONTH FROM fecha_ingreso) = %s")
                params.append(mes)

            if fecha_inicio and fecha_fin:
                filters.append("fecha_ingreso BETWEEN %s AND %s")
                params.extend([fecha_inicio, fecha_fin])

            if filters:
                query += " AND " + " AND ".join(filters)

            df = pd.read_sql(query, conn, params=params)
            return df
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return pd.DataFrame()

def calcular_totales(df):
    total_repuestos = df['repuestos_total'].sum()
    total_mano_obra = df['trabajo_total'].sum()
    total_general = df['total'].sum()
    return total_repuestos, total_mano_obra, total_general

# =========================== UI PRINCIPAL ===========================
def mostrar_mecanicos(page: ft.Page):
    page.title = "Reporte de Órdenes de Servicio"

    opciones_mecanico = obtener_opciones_mecanico()

    select_mecanico = ft.Dropdown(
        label="Selecciona Mecánico",
        options=[ft.dropdown.Option(m) for m in opciones_mecanico],
        width=300
    )

    dropdown_mes = ft.TextField(label="🗓️ Mes (YYYY-MM)", hint_text="Ej: 2025-05", width=150)
    input_desde = ft.TextField(label="📆 Desde (YYYY-MM-DD)", width=180)
    input_hasta = ft.TextField(label="📆 Hasta (YYYY-MM-DD)", width=180)
    password_input = ft.TextField(label="Contraseña para ver totales", password=True, can_reveal_password=True, width=300)

    result_container = ft.Column(spacing=10)
    total_container = ft.Column(spacing=10)

    def filtrar_ordenes(e=None):
        mecanico = select_mecanico.value
        mes = None
        errores = []

        if dropdown_mes.value:
            try:
                mes_fecha = datetime.strptime(dropdown_mes.value, "%Y-%m")
                mes = mes_fecha.month
            except:
                errores.append("❌ Formato de mes inválido (use YYYY-MM)")

        inicio = input_desde.value.strip()
        fin = input_hasta.value.strip()

        if inicio and fin:
            try:
                datetime.strptime(inicio, "%Y-%m-%d")
                datetime.strptime(fin, "%Y-%m-%d")
            except:
                errores.append("❌ Fechas inválidas (use YYYY-MM-DD)")

        result_container.controls.clear()
        total_container.controls.clear()

        if errores:
            for error in errores:
                result_container.controls.append(ft.Text(error, color="red"))
            page.update()
            return

        df = obtener_datos_ordenes(mecanico, mes, inicio or None, fin or None)

        if not df.empty:
            for _, servicio in df.iterrows():
                trabajo_limpio = limpiar_descripciones(servicio['trabajo_descripcion'])
                repuestos_limpio = limpiar_descripciones(servicio['repuestos_descripcion'])

                tarjeta = ft.Container(
                    content=ft.Column([
                        ft.Text(f"🔧 Mecánico: {servicio['mecanico_nombre']}", color=COLOR_TEXTO, weight="bold"),
                        ft.Text(f"👤 Cliente: {servicio['cliente_nombre']} - 📞 {servicio['cliente_telefono']}", color=COLOR_TEXTO),
                        ft.Text(f"🚗 Vehículo: {servicio['vehiculo_marca']} {servicio['vehiculo_modelo']} - 🎨 {servicio['vehiculo_color']} - 🔢 Placa: {servicio['vehiculo_placa']}", color=COLOR_TEXTO),
                        ft.Text(f"📅 Ingreso: {servicio['fecha_ingreso']} - 📤 Salida: {servicio['fecha_salida']}", color=COLOR_TEXTO),
                        ft.Text(f"🛠️ Trabajo: {trabajo_limpio}", color=COLOR_TEXTO),
                        ft.Text(f"🧾 Repuestos: {repuestos_limpio}", color=COLOR_TEXTO),
                        ft.Text(f"💳 Pago: {'✅ Completado' if servicio['pago_completado'] else '❌ Pendiente'} - Método: {servicio['metodo_pago']}", color=COLOR_TEXTO),
                        ft.Text(f"📝 Observaciones: {servicio['observaciones']}", color=COLOR_TEXTO),
                    ]),
                    padding=10,
                    bgcolor=COLOR_FONDO_TARJETA,
                    border_radius=10,
                    width=1300,
                    border=ft.border.all(1, COLOR_BORDE_TARJETA),
                    margin=8
                )
                result_container.controls.append(tarjeta)
        else:
            result_container.controls.append(ft.Text("📭 No se encontraron resultados"))

        if password_input.value == "12345":
            total_repuestos, total_mano_obra, total_general = calcular_totales(df)
            total_container.controls.append(ft.Text(f"🧾 Total Repuestos: {total_repuestos}", color="green"))
            total_container.controls.append(ft.Text(f"🛠️ Mano de Obra: {total_mano_obra}", color="orange"))
            total_container.controls.append(ft.Text(f"💰 Total General: {total_general}", weight="bold"))
        else:
            total_container.controls.append(ft.Text("🔒 Ingresa contraseña para ver totales."))

        page.update()

    btn_filtrar = ft.ElevatedButton("Filtrar", on_click=filtrar_ordenes)

    # SCROLL ACTIVO
    return ft.Container(
        expand=True,
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("📋 Reporte por Mecánico", size=24, weight="bold"),
                ft.Row([select_mecanico, dropdown_mes], spacing=20),
                ft.Row([input_desde, input_hasta], spacing=20),
                password_input,
                btn_filtrar,
                ft.Divider(),
                total_container,
                result_container
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=15
        )
    )
