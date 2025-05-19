import os
import sys
import re
import flet as ft

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scrip'))
from db import conectar_db

# 🎨 Colores
COLOR_TEXTO = "#BBDEFB"
COLOR_FONDO_TARJETA = "#1E1E1E"
COLOR_BORDE_TARJETA = "#90CAF9"
COLOR_BOTON = "#1976D2"
COLOR_SOMBRA = "#BBDEFB"
NUMERO_COLUMNAS = 1


def limpiar_descripciones(texto):
    if not texto:
        return ""
    return re.sub(r'\s*\(.*?\)', '', texto).strip()


def obtener_todos_los_servicios(mes=None, mecanico=None, pago=None, desde=None, hasta=None):
    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            query = """
                SELECT 
                    id, fecha_ingreso, fecha_salida, mecanico_nombre,
                    cliente_nombre, cliente_dni, cliente_telefono,
                    vehiculo_marca, vehiculo_modelo, vehiculo_color,
                    vehiculo_placa, vehiculo_numero_serie, vehiculo_kilometraje,
                    trabajo_descripcion, trabajo_total,
                    repuestos_descripcion, repuestos_total,
                    trabajo_terceros_descripcion, trabajo_terceros_precio,
                    subtotal, descuento, igv, total,
                    metodo_pago, pago_completado, observaciones
                FROM ordenes_servicio
                WHERE fecha_ingreso IS NOT NULL
            """
            if mes and mes != "Todos":
                query += f" AND TO_CHAR(fecha_ingreso, 'YYYY-MM') = '{mes}'"
            if desde:
                query += f" AND fecha_ingreso >= '{desde}'"
            if hasta:
                query += f" AND fecha_ingreso <= '{hasta}'"
            if mecanico and mecanico != "Todos":
                query += f" AND mecanico_nombre = '{mecanico}'"
            if pago and pago != "Todos":
                query += " AND pago_completado = TRUE" if pago == "Completado" else " AND pago_completado = FALSE"
            query += " ORDER BY fecha_ingreso"
            cursor.execute(query)
            columnas = [desc[0] for desc in cursor.description]
            return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
    except Exception as e:
        print(f"Error al obtener los datos: {e}")
        return []


def obtener_lista_mecanicos():
    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT mecanico_nombre FROM ordenes_servicio WHERE mecanico_nombre IS NOT NULL ORDER BY mecanico_nombre")
            return [fila[0] for fila in cursor.fetchall()]
    except Exception as e:
        print(f"Error al obtener mecánicos: {e}")
        return []


def mostrar_servicios_app(page: ft.Page):
    contenedor_resultado = ft.Column(expand=True, spacing=10)

    mecanicos = obtener_lista_mecanicos()
    opciones_mecanico = [ft.dropdown.Option("Todos")] + [ft.dropdown.Option(m) for m in mecanicos]
    opciones_pago = [ft.dropdown.Option("Todos"), ft.dropdown.Option("Completado"), ft.dropdown.Option("Incompleto")]

    dropdown_mecanico = ft.Dropdown(label="🔍 Mecánico", options=opciones_mecanico, value="Todos", width=200)
    dropdown_pago = ft.Dropdown(label="💳 Pago", options=opciones_pago, value="Todos", width=150)
    dropdown_mes = ft.TextField(label="🗓️ Mes (YYYY-MM)", hint_text="Ej: 2025-05", width=150)
    input_desde = ft.TextField(label="📆 Desde (YYYY-MM-DD)", width=180)
    input_hasta = ft.TextField(label="📆 Hasta (YYYY-MM-DD)", width=180)

    def actualizar_servicios():
        contenedor_resultado.controls.clear()
        servicios = obtener_todos_los_servicios(
            mes=dropdown_mes.value.strip(),
            mecanico=dropdown_mecanico.value,
            pago=dropdown_pago.value,
            desde=input_desde.value.strip(),
            hasta=input_hasta.value.strip()
        )

        if not servicios:
            contenedor_resultado.controls.append(
                ft.Container(
                    content=ft.Text("📭 No hay servicios registrados", color=COLOR_TEXTO, size=20),
                    alignment=ft.alignment.center,
                    padding=30
                )
            )
        else:
            columnas = [[] for _ in range(NUMERO_COLUMNAS)]
            for index, servicio in enumerate(servicios):
                col_index = index % NUMERO_COLUMNAS
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
                    ], spacing=6),
                    bgcolor=COLOR_FONDO_TARJETA,
                    padding=18,
                    width=1300,
                    border_radius=12,
                    border=ft.border.all(1, COLOR_BORDE_TARJETA),
                    shadow=ft.BoxShadow(blur_radius=12, color=COLOR_SOMBRA),
                    margin=10
                )

                columnas[col_index].append(tarjeta)

            filas = ft.Row([ft.Column(col, expand=True, spacing=10) for col in columnas], spacing=10)
            contenedor_resultado.controls.append(ft.Container(content=filas, padding=20))

        page.update()

    boton_filtrar = ft.ElevatedButton(
        text="🔎 Filtrar",
        bgcolor=COLOR_BOTON,
        color="white",
        on_click=lambda e: actualizar_servicios()
    )

    filtros_row = ft.Container(
        content=ft.Column([
            ft.Row([dropdown_mecanico, dropdown_mes, dropdown_pago], spacing=15),
            ft.Row([input_desde, input_hasta, boton_filtrar], spacing=15),
        ], spacing=10),
        padding=20
    )

    return ft.Container(
        expand=True,
        content=ft.Column(
            controls=[
                ft.Text("📋 Historial de Servicios", size=24, weight="bold", color="white"),
                filtros_row,
                ft.Divider(),
                contenedor_resultado
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=15
        )
    )

