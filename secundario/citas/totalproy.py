import flet as ft
import pandas as pd
import numpy as np
import io
import os
import sys
import base64
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Ruta al módulo de conexión
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scrip'))
from db import conectar_db

# === Funciones auxiliares ===

def obtener_datos(agrupacion="mes", mes=None, mecanico=None):
    try:
        with conectar_db() as conn:
            campo_fecha, formato = {
                "dia": ("fecha_ingreso::date", "YYYY-MM-DD"),
                "semana": ("DATE_TRUNC('week', fecha_ingreso)", "IYYY-IW"),
                "anio": ("DATE_TRUNC('year', fecha_ingreso)", "YYYY"),
                "mes": ("DATE_TRUNC('month', fecha_ingreso)", "YYYY-MM")
            }.get(agrupacion, ("DATE_TRUNC('month', fecha_ingreso)", "YYYY-MM"))

            query = f"""
                SELECT 
                    TO_CHAR({campo_fecha}, '{formato}') AS periodo,
                    SUM(trabajo_total + repuestos_total + trabajo_terceros_precio) AS total
                FROM ordenes_servicio
                WHERE total IS NOT NULL AND fecha_ingreso IS NOT NULL
            """

            if agrupacion == "dia" and mes and mes != "Todos":
                query += f" AND TO_CHAR(DATE_TRUNC('month', fecha_ingreso), 'YYYY-MM') = '{mes}'"
            if mecanico and mecanico != "Todos":
                query += f" AND mecanico_nombre = '{mecanico}'"

            query += " GROUP BY periodo ORDER BY periodo"

            return pd.read_sql(query, conn)
    except Exception as e:
        print(f"❌ Error: {e}")
        return pd.DataFrame(columns=["periodo", "total"])

def crear_grafico(df, incluir_prediccion=False, agrupacion="mes"):
    if df.empty:
        return None, "⚠️ No hay datos para mostrar."

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(df['periodo'], df['total'], color='#4fc3f7', label='Ingresos')

    if incluir_prediccion and len(df) >= 2:
        X = np.arange(len(df)).reshape(-1, 1)
        y = df['total'].values
        modelo = LinearRegression()
        modelo.fit(X, y)
        X_future = np.arange(len(df) + 4).reshape(-1, 1)
        y_pred = modelo.predict(X_future)
        future_labels = list(df['periodo']) + [f"F{i+1}" for i in range(4)]
        ax.plot(future_labels, y_pred, color='orange', linestyle='--', label='Proyección')

    ax.set_title(f"Ingresos por {agrupacion.capitalize()}")
    ax.set_xlabel("Periodo")
    ax.set_ylabel("Total (S/.)")
    ax.legend()
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()
    plt.close()
    return img_base64, None

def obtener_opciones_mes():
    try:
        with conectar_db() as conn:
            df = pd.read_sql("""
                SELECT DISTINCT TO_CHAR(DATE_TRUNC('month', fecha_ingreso), 'YYYY-MM') AS mes
                FROM ordenes_servicio
                ORDER BY mes
            """, conn)
            return ["Todos"] + df['mes'].dropna().tolist()
    except:
        return ["Todos"]

def obtener_opciones_mecanico():
    try:
        with conectar_db() as conn:
            df = pd.read_sql("SELECT DISTINCT mecanico_nombre FROM ordenes_servicio WHERE mecanico_nombre IS NOT NULL", conn)
            return ["Todos"] + df['mecanico_nombre'].dropna().tolist()
    except:
        return ["Todos"]

# === Vista Principal para proyecciones de ingresos ===

def vista_proyecciones_ingresos(page: ft.Page) -> ft.Container:
    page.bgcolor = "#1c1c1c"
    page.scroll = "auto"

    img = ft.Image(width=800, height=400)
    resultado = ft.Text(color="white", size=14)

    agrupacion_dropdown = ft.Dropdown(
        label="Agrupar por",
        value="dia",
        options=[ft.dropdown.Option(a) for a in ["dia", "semana", "mes", "anio"]]
    )
    mes_dropdown = ft.Dropdown(label="Mes", value="Todos", options=[ft.dropdown.Option(m) for m in obtener_opciones_mes()])
    mecanico_dropdown = ft.Dropdown(label="Mecánico", value="Todos", options=[ft.dropdown.Option(m) for m in obtener_opciones_mecanico()])
    sw_prediccion = ft.Switch(label="Incluir Proyección", value=False)

    def actualizar_visibilidad_mes():
        mes_dropdown.visible = agrupacion_dropdown.value == "dia"
        page.update()

    def actualizar_grafico(_=None):
        agrupacion = agrupacion_dropdown.value
        mes = mes_dropdown.value if agrupacion == "dia" else None
        mecanico = mecanico_dropdown.value
        incluir = sw_prediccion.value

        df = obtener_datos(agrupacion, mes, mecanico)
        grafico, error = crear_grafico(df, incluir_prediccion=incluir, agrupacion=agrupacion)

        if error:
            resultado.value = error
            img.src_base64 = ""
        else:
            resultado.value = ""
            img.src_base64 = grafico
        page.update()

    def exportar_csv(e):
        agrupacion = agrupacion_dropdown.value
        mes = mes_dropdown.value if agrupacion == "dia" else None
        mecanico = mecanico_dropdown.value
        df = obtener_datos(agrupacion, mes, mecanico)
        if df.empty:
            resultado.value = "⚠️ No hay datos para exportar."
            return
        df.to_csv("export_ingresos.csv", index=False)
        resultado.value = "✅ Datos exportados a export_ingresos.csv"

    agrupacion_dropdown.on_change = lambda e: (actualizar_visibilidad_mes(), actualizar_grafico())
    mes_dropdown.on_change = actualizar_grafico
    mecanico_dropdown.on_change = actualizar_grafico
    sw_prediccion.on_change = actualizar_grafico

    export_button = ft.ElevatedButton("Exportar CSV", icon=ft.icons.DOWNLOAD, on_click=exportar_csv)

    actualizar_visibilidad_mes()
    actualizar_grafico()

    return ft.Container(
        padding=20,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Text("📈 Dashboard Ingresos Agrupados", size=24, weight="bold", color="white"),
                ft.Row([agrupacion_dropdown, mes_dropdown, mecanico_dropdown, sw_prediccion, export_button], alignment="spaceBetween"),
                img,
                resultado
            ]
        )
    )

    page.update()
