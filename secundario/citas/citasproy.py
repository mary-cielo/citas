import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Usar backend sin GUI (evita errores de hilos)
import matplotlib.pyplot as plt
import io
import base64
import flet as ft
from datetime import timedelta
from sklearn.linear_model import LinearRegression
import os
import sys

# Agregar ruta al módulo de conexión
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scrip'))
from db import conectar_db

# ===================== QUERIES =====================
QUERIES = {
    'dia': """
        SELECT fecha, COUNT(*) AS cantidad
        FROM citas
        GROUP BY fecha
        ORDER BY fecha
    """,
    'semana': """
        SELECT DATE_TRUNC('week', fecha) AS fecha, COUNT(*) AS cantidad
        FROM citas
        GROUP BY DATE_TRUNC('week', fecha)
        ORDER BY fecha
    """,
    'mes': """
        SELECT DATE_TRUNC('month', fecha) AS fecha, COUNT(*) AS cantidad
        FROM citas
        WHERE EXTRACT(MONTH FROM fecha) = %s
        GROUP BY DATE_TRUNC('month', fecha)
        ORDER BY fecha
    """,
    'anio': """
        SELECT DATE_TRUNC('year', fecha) AS fecha, COUNT(*) AS cantidad
        FROM citas
        GROUP BY DATE_TRUNC('year', fecha)
        ORDER BY fecha
    """,
    'asistencias': """
        SELECT asistio, COUNT(*) AS cantidad
        FROM citas
        GROUP BY asistio
    """
}

# ===================== FUNCIONES AUXILIARES =====================

def obtener_datos_citas(agrupacion=None, mes=None):
    try:
        with conectar_db() as conn:
            if agrupacion == 'mes' and mes is not None:
                return pd.read_sql(QUERIES['mes'], conn, params=(mes,))
            elif agrupacion in QUERIES:
                return pd.read_sql(QUERIES[agrupacion], conn)
            else:
                return pd.read_sql(QUERIES['asistencias'], conn)
    except Exception as e:
        print(f"[Error DB] {e}")
        return pd.DataFrame()


def generar_prediccion(agrupacion, mes=None):
    datos = obtener_datos_citas(agrupacion, mes)
    if datos.empty or 'fecha' not in datos:
        return None, None

    datos['fecha'] = pd.to_datetime(datos['fecha'])
    datos['dias'] = (datos['fecha'] - datos['fecha'].min()).dt.days

    X = datos[['dias']]
    y = datos['cantidad']

    modelo = LinearRegression()
    modelo.fit(X, y)

    dias_futuros = np.arange(X['dias'].max() + 1, X['dias'].max() + 31).reshape(-1, 1)
    predicciones = modelo.predict(dias_futuros)

    paso = {'semana': 7, 'mes': 30, 'anio': 365}.get(agrupacion, 1)
    fechas_pred = [datos['fecha'].max() + timedelta(days=i * paso) for i in range(1, 31)]

    df_pred = pd.DataFrame({'fecha': fechas_pred, 'cantidad': predicciones})

    return datos, df_pred


def mostrar_proyecciones_citas(agrupacion, mes, page, img, resultado):
    datos, pred = generar_prediccion(agrupacion, mes)
    if datos is None:
        resultado.value = "No hay datos para mostrar."
        img.src_base64 = ""
        page.update()
        return

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(datos['fecha'], datos['cantidad'], label='Histórico', color='#00aaff')
    ax.bar(pred['fecha'], pred['cantidad'], label='Predicción', color='#b62dff', alpha=0.7)

    ax.set_title(f"Predicción de Citas ({agrupacion})", color='white')
    ax.set_xlabel("Fecha", color='white')
    ax.set_ylabel("Cantidad", color='white')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.xticks(rotation=45, color='white')
    plt.yticks(color='white')
    fig.patch.set_facecolor('#121212')
    ax.set_facecolor('#1e1e1e')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
    buf.seek(0)
    img.src_base64 = base64.b64encode(buf.read()).decode()

    resultado.value = ""
    page.update()


def crear_grafico_asistidas(tipo, page, img, resultado):
    datos = obtener_datos_citas()
    if datos.empty:
        resultado.value = "No se encontraron datos de citas."
        img.src_base64 = ""
        page.update()
        return

    asistidas = datos.loc[datos['asistio'] == True, 'cantidad'].sum()
    no_asistidas = datos.loc[datos['asistio'] == False, 'cantidad'].sum()

    etiquetas = ['Asistidas', 'No Asistidas']
    valores = [asistidas, no_asistidas]

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))

    if tipo == 'barras':
        ax.bar(etiquetas, valores, color=['#007BFF', '#6C757D'])
        ax.set_title("Citas Asistidas vs No Asistidas", color='white')
        for i, v in enumerate(valores):
            ax.text(i, v + 0.5, str(int(v)), ha='center', color='white')

    elif tipo == 'pastel':
        plt.pie(valores, labels=etiquetas, autopct='%1.1f%%', colors=['#007BFF', '#6C757D'])
        plt.title("Distribución de Asistencias", color='white')

    elif tipo == 'barras_apiladas':
        ax.bar('Citas', asistidas, label='Asistidas', color='#007BFF')
        ax.bar('Citas', no_asistidas, bottom=asistidas, label='No Asistidas', color='#6C757D')
        ax.set_title("Citas Apiladas por Estado", color='white')
        ax.legend()

    ax.set_facecolor('#1e1e1e')
    fig.patch.set_facecolor('#121212')
    plt.xticks(color='white')
    plt.yticks(color='white')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
    buf.seek(0)
    img.src_base64 = base64.b64encode(buf.read()).decode()
    resultado.value = ""
    page.update()


# ===================== UI EXPORTABLE =====================

def vista_proyecciones_citas(page: ft.Page):
    img = ft.Image()
    resultado = ft.Text("Seleccione las opciones y presione 'Generar Predicción'.", color="white", text_align="center")

    dropdown = ft.Dropdown(
        label="Agrupar por:",
        options=[
            ft.dropdown.Option("dia", "Por Día"),
            ft.dropdown.Option("semana", "Por Semana"),
            ft.dropdown.Option("mes", "Por Mes"),
            ft.dropdown.Option("anio", "Por Año"),
        ],
        value="mes",
    )

    month_dropdown = ft.Dropdown(
        label="Seleccionar Mes",
        options=[ft.dropdown.Option(str(i), m) for i, m in enumerate([
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ], start=1)],
        value="1",
        visible=True
    )

    grafico_dropdown = ft.Dropdown(
        label="Tipo de Gráfico de Asistencias",
        options=[
            ft.dropdown.Option("barras", "Gráfico de Barras"),
            ft.dropdown.Option("pastel", "Gráfico de Pastel"),
            ft.dropdown.Option("barras_apiladas", "Barras Apiladas"),
        ],
        value="barras",
    )

    def toggle_month_dropdown(e):
        month_dropdown.visible = (dropdown.value == 'mes')
        page.update()

    dropdown.on_change = toggle_month_dropdown

    def on_pred_click(e):
        mostrar_proyecciones_citas(dropdown.value, month_dropdown.value if dropdown.value == 'mes' else None, page, img, resultado)

    def on_grafico_change(e):
        crear_grafico_asistidas(grafico_dropdown.value, page, img, resultado)

    btn_prediccion = ft.ElevatedButton(
        text="Generar Predicción",
        on_click=on_pred_click,
        style=ft.ButtonStyle(color="white", bgcolor="#b62dff")
    )

    btn_grafico = ft.ElevatedButton(
        text="Mostrar Gráfico de Asistencias",
        on_click=on_grafico_change,
        style=ft.ButtonStyle(color="white", bgcolor="#007BFF")
    )

    titulo_pred = ft.Text("📈 Predicción de Citas", size=22, color="white", text_align="center", weight="bold")
    titulo_asist = ft.Text("📊 Estadísticas de Asistencia", size=22, color="white", text_align="center", weight="bold")

    content = ft.Column(
        controls=[
            titulo_pred,
            dropdown,
            month_dropdown,
            btn_prediccion,
            resultado,
            img,
            ft.Divider(color="gray"),
            titulo_asist,
            grafico_dropdown,
            btn_grafico
        ],
        scroll="auto",
        expand=True,
        spacing=20
    )

    return content
