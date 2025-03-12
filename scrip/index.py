import sys
import os

# Asegurar que Python pueda encontrar la carpeta raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ahora podemos importar estilos sin error
from estilos.stilos import aplicar_estilos, boton_estilizado
import tkinter as tk

# Crear ventana
ventana = tk.Tk()
ventana.title("BIENVENIDO A RUDOLFS")
ventana.geometry("400x500")
ventana.configure(bg="#e0e0e0")  # Color de fondo de la ventana

# Etiqueta de bienvenida
label = tk.Label(ventana, text="Bienvenido")
aplicar_estilos(label)
label.pack(pady=20)

# Botón Iniciar Sesión
boton_inicio = tk.Button(ventana, text="Iniciar Sesión", command=ventana.quit)
boton_estilizado(boton_inicio)
boton_inicio.pack(pady=10)

# Botón Crear Cuenta
boton_crear = tk.Button(ventana, text="Crear Cuenta", command=ventana.quit)
boton_estilizado(boton_crear)
boton_crear.pack(pady=10)

# Etiqueta "¿Quiénes somos?"
label_info = tk.Label(ventana, text="¿Quiénes somos?")
aplicar_estilos(label_info)
label_info.pack(pady=20)

# Iniciar ventana
ventana.mainloop()
