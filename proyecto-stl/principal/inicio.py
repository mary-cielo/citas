import tkinter as tk
from tkinter import ttk

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Tablero")
ventana.geometry("400x600")
ventana.configure(bg="#2E2E2E")

# Título
titulo = tk.Label(ventana, text="Tablero", fg="white", bg="#2E2E2E", font=("Arial", 24))
titulo.pack(pady=20)

# Botón para crear orden de servicio
boton_crear_orden = tk.Button(ventana, text="CREAR ORDEN DE SERVICIO", bg="#4CAF50", fg="white", font=("Arial", 14), padx=10, pady=5)
boton_crear_orden.pack(pady=10)

# Progreso de punto de equilibrio
label_progreso = tk.Label(ventana, text="Progreso de punto de equilibrio (Hrs)", fg="white", bg="#2E2E2E")
label_progreso.pack(pady=5)

progreso = ttk.Progressbar(ventana, length=300, mode='determinate')
progreso['value'] = 4
progreso.pack(pady=5)

# Citas para hoy
label_citas = tk.Label(ventana, text="Citas para hoy: 0", fg="white", bg="#2E2E2E", font=("Arial", 12))
label_citas.pack(pady=10)

# Ranking
label_ranking = tk.Label(ventana, text="Ranking: 174/2933", fg="white", bg="#2E2E2E", font=("Arial", 12))
label_ranking.pack(pady=10)

# NPS
label_nps = tk.Label(ventana, text="NPS: +95 ★★★★", fg="white", bg="#2E2E2E", font=("Arial", 12))
label_nps.pack(pady=10)

# Garantías
label_garantias = tk.Label(ventana, text="Garantías: 0%", fg="white", bg="#2E2E2E", font=("Arial", 12))
label_garantias.pack(pady=10)

# Capacidad Productiva
label_capacidad = tk.Label(ventana, text="Capacidad Productiva: 6/300 Hrs", fg="white", bg="#2E2E2E", font=("Arial", 12))
label_capacidad.pack(pady=10)

# Órdenes en proceso
label_ordenes = tk.Label(ventana, text="Órdenes en proceso: 37", fg="white", bg="#2E2E2E", font=("Arial", 12))
label_ordenes.pack(pady=10)

# Barra de navegación inferior
navbar = tk.Frame(ventana, bg="#2E2E2E")
navbar.pack(side=tk.BOTTOM, fill=tk.X)

boton_inicio = tk.Button(navbar, text="Inicio", bg="#4CAF50", fg="white")
boton_inicio.pack(side=tk.LEFT, padx=5)

boton_servicios = tk.Button(navbar, text="Servicios", bg="#4CAF50", fg="white")
boton_servicios.pack(side=tk.LEFT, padx=5)

boton_citas = tk.Button(navbar, text="Citas", bg="#4CAF50", fg="white")
boton_citas.pack(side=tk.LEFT, padx=5)

# Iniciar la aplicación
ventana.mainloop()