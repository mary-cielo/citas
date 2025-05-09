import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import flet as ft

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scrip'))
from db import conectar_db  

# Conexión a la base de datos y extracción de datos
def obtener_datos_citas():
    try:
        with conectar_db() as conn:
            # Consulta para contar citas asistidas y no asistidas
            query = """
                SELECT asistio, COUNT(*) as cantidad 
                FROM citas 
                GROUP BY asistio
            """
            datos = pd.read_sql(query, conn)
            return datos
    except Exception as e:
        print(f"Error al obtener datos de la base de datos: {e}")
        return pd.DataFrame(columns=['asistio', 'cantidad'])  # Retornar DataFrame vacío en caso de error

# Función para crear el gráfico
def crear_grafico(tipo_grafico):
    datos = obtener_datos_citas()

    if datos.empty:
        return "No se encontraron datos de citas."

    asistido = datos[datos['asistio'] == True]['cantidad'].values[0] if True in datos['asistio'].values else 0
    no_asistido = datos[datos['asistio'] == False]['cantidad'].values[0] if False in datos['asistio'].values else 0
    
    categorias = ['Asistidos', 'No Asistidos']
    cantidades = [asistido, no_asistido]

    plt.style.use('dark_background')
    plt.figure(figsize=(10, 6))
    
    if tipo_grafico == 'barras':
        bars = plt.bar(categorias, cantidades, color=['#007BFF', '#6C757D'])
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, int(yval), ha='center', va='bottom')
        plt.title('Comparación de Citas Asistidas y No Asistidas', fontsize=16)
        plt.xlabel('Estado de Citas', fontsize=12)
        plt.ylabel('Cantidad de Citas', fontsize=12)

    elif tipo_grafico == 'pastel':
        plt.pie(cantidades, labels=categorias, autopct='%1.1f%%', colors=['#007BFF', '#6C757D'])
        plt.title('Porcentaje de Citas Asistidas y No Asistidas', fontsize=16)

    elif tipo_grafico == 'lineal':
        plt.plot(categorias, cantidades, marker='o', linestyle='-', color='#007BFF', linewidth=2)
        plt.title('Comparación de Citas Asistidas y No Asistidas (Gráfico Lineal)', fontsize=16)
        plt.xlabel('Estado de Citas', fontsize=12)
        plt.ylabel('Cantidad de Citas', fontsize=12)
        for i, v in enumerate(cantidades):
            plt.text(i, v + 0.5, str(v), ha='center', va='bottom')

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()          
    plt.show()

# Función para manejar el evento del botón
def on_button_click(e):
    tipo_grafico = e.control.data
    crear_grafico(tipo_grafico)

# Crear la aplicación Flet
def main(page: ft.Page):
    page.title = "Seleccionador de Gráficos"
    
    btn_barras = ft.ElevatedButton("Gráfico de Barras", data='barras', on_click=on_button_click)
    btn_pastel = ft.ElevatedButton("Gráfico de Pastel", data='pastel', on_click=on_button_click)
    btn_lineal = ft.ElevatedButton("Gráfico Lineal", data='lineal', on_click=on_button_click)

    page.add(btn_barras, btn_pastel, btn_lineal)

# Ejecutar la aplicación
ft.app(target=main)