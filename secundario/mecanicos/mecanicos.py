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

# =========================== COLORES ===========================
COLOR_TEXTO = "#E3F2FD"
COLOR_FONDO_TARJETA = "#263238"
COLOR_BORDE_TARJETA = "#4FC3F7"
COLOR_BOTON = "#0288D1"
COLOR_SOMBRA = "#B3E5FC"
COLOR_ERROR = "#FF5252"
COLOR_SUCCESS = "#81C784"

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
            filters, params = [], []

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

            return pd.read_sql(query, conn, params=params)
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return pd.DataFrame()

def calcular_totales(df):
    return (
        df['repuestos_total'].sum(),
        df['trabajo_total'].sum(),
        df['total'].sum()
    )

# =========================== UI PRINCIPAL ===========================
def mostrar_mecanicos(page: ft.Page):
    page.title = "🔍 Reporte de Órdenes de Servicio"

    # Elementos UI
    select_mecanico = ft.Dropdown(
        label="👨‍🔧 Selecciona Mecánico",
        options=[ft.dropdown.Option(m) for m in obtener_opciones_mecanico()],
        width=300
    )

    dropdown_mes = ft.TextField(label="🗓️ Mes (YYYY-MM)", hint_text="Ej: 2025-05", width=160)
    input_desde = ft.TextField(label="📆 Desde (YYYY-MM-DD)", width=180)
    input_hasta = ft.TextField(label="📆 Hasta (YYYY-MM-DD)", width=180)
    password_input = ft.TextField(label="🔐 Contraseña para ver totales", password=True, can_reveal_password=True, width=300)

    result_container = ft.Column(spacing=10)
    total_container = ft.Column(spacing=10)

    def filtrar_ordenes(e=None):
        # Validaciones
        errores = []
        mecanico = select_mecanico.value
        mes = None

        # Validar mes
        if dropdown_mes.value:
            try:
                mes_fecha = datetime.strptime(dropdown_mes.value, "%Y-%m")
                mes = mes_fecha.month
            except ValueError:
                errores.append("❌ Mes inválido. Formato correcto: YYYY-MM.")

        # Validar fechas
        inicio, fin = input_desde.value.strip(), input_hasta.value.strip()
        try:
            if inicio and fin:
                datetime.strptime(inicio, "%Y-%m-%d")
                datetime.strptime(fin, "%Y-%m-%d")
        except ValueError:
            errores.append("❌ Fechas inválidas. Use el formato: YYYY-MM-DD.")

        # Limpiar contenedores
        result_container.controls.clear()
        total_container.controls.clear()

        if errores:
            for error in errores:
                result_container.controls.append(ft.Text(error, color=COLOR_ERROR, weight="bold"))
            page.update()
            return

        # Obtener datos
        df = obtener_datos_ordenes(mecanico, mes, inicio or None, fin or None)

        if df.empty:
            result_container.controls.append(ft.Text("📭 No se encontraron resultados.", color=COLOR_ERROR))
        else:
            for _, s in df.iterrows():
                tarjeta = ft.Container(
                    content=ft.Column([
                        ft.Text(f"🔧 Mecánico: {s['mecanico_nombre']}", color=COLOR_TEXTO, weight="bold"),
                        ft.Text(f"👤 Cliente: {s['cliente_nombre']} - 📞 {s['cliente_telefono']}", color=COLOR_TEXTO),
                        ft.Text(f"🚗 {s['vehiculo_marca']} {s['vehiculo_modelo']} - 🎨 {s['vehiculo_color']} - 🔢 {s['vehiculo_placa']}", color=COLOR_TEXTO),
                        ft.Text(f"📅 Ingreso: {s['fecha_ingreso']} - 📤 Salida: {s['fecha_salida']}", color=COLOR_TEXTO),
                        ft.Text(f"🛠️ Trabajo: {limpiar_descripciones(s['trabajo_descripcion'])}", color=COLOR_TEXTO),
                        ft.Text(f"🧾 Repuestos: {limpiar_descripciones(s['repuestos_descripcion'])}", color=COLOR_TEXTO),
                        ft.Text(f"💳 Pago: {'✅ Completado' if s['pago_completado'] else '❌ Pendiente'} - Método: {s['metodo_pago']}", color=COLOR_TEXTO),
                        ft.Text(f"📝 Observaciones: {s['observaciones']}", color=COLOR_TEXTO),
                    ]),
                    padding=10,
                    bgcolor=COLOR_FONDO_TARJETA,
                    border_radius=10,
                    border=ft.border.all(1, COLOR_BORDE_TARJETA),
                    width=1300,
                    margin=8
                )
                result_container.controls.append(tarjeta)

        # Mostrar totales si la contraseña es correcta
        if password_input.value == "12345":
            repuestos, mano_obra, total = calcular_totales(df)
            total_container.controls.extend([
                ft.Text(f"🧾 Total Repuestos: {repuestos}", color=COLOR_SUCCESS),
                ft.Text(f"🛠️ Mano de Obra: {mano_obra}", color="#FFB74D"),
                ft.Text(f"💰 Total General: {total}", weight="bold", color="#FFF176"),
            ])
        else:
            total_container.controls.append(ft.Text("🔒 Ingresa contraseña para ver los totales.", color="gray"))

        page.update()

    # Botón
    btn_filtrar = ft.ElevatedButton(
        text="🔎 Filtrar",
        on_click=filtrar_ordenes,
        style=ft.ButtonStyle(bgcolor=COLOR_BOTON, color="white")
    )

    # Layout principal
    return ft.Container(
        expand=True,
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("📋 Reporte por Mecánico", size=28, weight="bold", color=COLOR_BOTON),
                ft.Row([select_mecanico, dropdown_mes], spacing=20),
                ft.Row([input_desde, input_hasta], spacing=20),
                password_input,
                btn_filtrar,
                ft.Divider(height=2, thickness=1),
                total_container,
                result_container,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=15
        )
    )
