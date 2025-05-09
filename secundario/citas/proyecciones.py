import flet as ft
import pandas as pd
import numpy as np
import io
import os
import sys
import base64
from sklearn.linear_model import LinearRegression
from datetime import timedelta
import matplotlib.pyplot as plt
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scrip'))
from db import conectar_db

# Función para obtener los ingresos por agrupación
def obtener_ingresos(agrupacion=None):
    try:
        with conectar_db() as conn:
            query_dict = {
                'dia': """
                    SELECT fecha_ingreso::date AS fecha, 
                           SUM(trabajo_total + repuestos_total + trabajo_terceros_precio) AS total
                    FROM ordenes_servicio 
                    GROUP BY fecha_ingreso::date 
                    ORDER BY fecha_ingreso::date
                """,
                'semana': """
                    SELECT DATE_TRUNC('week', fecha_ingreso) AS fecha, 
                           SUM(trabajo_total + repuestos_total + trabajo_terceros_precio) AS total
                    FROM ordenes_servicio
                    GROUP BY DATE_TRUNC('week', fecha_ingreso)
                    ORDER BY fecha
                """,
                'mes': """
                    SELECT DATE_TRUNC('month', fecha_ingreso) AS fecha, 
                           SUM(trabajo_total + repuestos_total + trabajo_terceros_precio) AS total
                    FROM ordenes_servicio
                    GROUP BY DATE_TRUNC('month', fecha_ingreso)
                    ORDER BY fecha
                """,
                'anio': """
                    SELECT DATE_TRUNC('year', fecha_ingreso) AS fecha, 
                           SUM(trabajo_total + repuestos_total + trabajo_terceros_precio) AS total
                    FROM ordenes_servicio
                    GROUP BY DATE_TRUNC('year', fecha_ingreso)
                    ORDER BY fecha
                """
            }

            query = query_dict.get(agrupacion, '')
            if query:
                return pd.read_sql_query(query, conn)
            else:
                return pd.DataFrame(columns=['fecha', 'total'])
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return pd.DataFrame(columns=['fecha', 'total'])  # Retorna un DataFrame vacío en caso de error

# Función para crear el gráfico
def crear_grafico(agrupacion, page):
    datos = obtener_ingresos(agrupacion)

    if datos.empty:
        return "No se encontraron datos."

    # Convertir la columna de fecha a tipo datetime
    datos['fecha'] = pd.to_datetime(datos['fecha'], errors='coerce')

    if datos['fecha'].isnull().any():
        return "Algunos datos de fecha son inválidos."

    # Visualizar los datos
    categorias = datos['fecha'].dt.strftime('%Y-%m-%d').tolist()
    cantidades = datos['total'].tolist()

    plt.style.use('dark_background')
    plt.figure(figsize=(10, 6))
    plt.plot(categorias, cantidades, marker='o', linestyle='-', color='#00aaff', linewidth=2)
    plt.title(f'Ingresos por Fecha ({agrupacion.capitalize()})', fontsize=16)
    plt.xlabel('Fecha', fontsize=12)
    plt.ylabel('Ingresos', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Convertir gráfico a imagen en base64 para flet
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()
    buf.close()
    return img_base64

# Función para la predicción de ingresos futuros
def actualizar_prediccion(e, page):
    tipo_agrupacion = dropdown.value
    datos = obtener_ingresos(tipo_agrupacion)

    if datos.empty:
        resultado.value = "No se encontraron datos."
        img.src_base64 = ""
        page.update()
        return

    # Convertir la columna de fecha a tipo datetime
    datos['fecha'] = pd.to_datetime(datos['fecha'], errors='coerce')

    if datos['fecha'].isnull().any():
        resultado.value = "Algunos datos de fecha son inválidos."
        img.src_base64 = ""
        page.update()
        return

    # Calcular los días desde el primer registro
    datos['dias'] = (datos['fecha'] - datos['fecha'].min()).dt.days
    X = datos[['dias']]
    y = datos['total']
    
    # Crear y entrenar el modelo de regresión lineal
    modelo = LinearRegression()
    modelo.fit(X, y)

    # Proyección de los próximos 30 días
    dias_futuros = np.array(range(datos['dias'].max() + 1, datos['dias'].max() + 31)).reshape(-1, 1)
    predicciones = modelo.predict(dias_futuros)

    # Fechas futuras
    fechas_futuras = [datos['fecha'].max() + timedelta(days=i) for i in range(1, 31)]
    
    # Visualizar las predicciones
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(datos['fecha'], datos['total'], color='blue', label="Ingresos Históricos")
    ax.bar(fechas_futuras, predicciones, color='red', label="Proyección de Ingresos", alpha=0.7)
    ax.set_title(f"Proyección de Ingresos ({tipo_agrupacion.capitalize()})")
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Ingresos')
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Convertir el gráfico de predicción a imagen en base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()
    buf.close()

    resultado.value = ""
    img.src_base64 = img_base64
    page.update()

# Función de manejo de eventos de los botones de gráfico
def on_button_click(e, page):
    tipo_grafico = e.control.data
    img_base64 = crear_grafico(tipo_grafico, page)
    img.src_base64 = img_base64
    page.update()

# Función principal de la app en Flet
def main(page: ft.Page):
    page.title = "Proyección de Ingresos"
    page.bgcolor = "#121212"  # Fondo oscuro

    global img, resultado, dropdown
    img = ft.Image()

    # Dropdown para selección de agrupación
    dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option("dia"),
            ft.dropdown.Option("semana"),
            ft.dropdown.Option("mes"),
            ft.dropdown.Option("anio")
        ],
        value="mes",
        on_change=lambda e: actualizar_prediccion(e, page),
    )

    resultado = ft.Text("Seleccione una opción para ver la predicción", color='white')

    # Botones para gráfic

    # Agregar elementos a la página
    page.add(ft.Text("", color='white', size=20), dropdown, img, resultado)

# Ejecutar la aplicación
ft.app(target=main)
