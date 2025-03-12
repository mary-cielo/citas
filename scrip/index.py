import sys
import os
import tkinter as tk

# Asegurar que Python pueda encontrar la carpeta raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ---------- FUNCIONES AUXILIARES DE ESTILO ----------
def aplicar_estilos(widget):
    widget.config(font=("Segoe UI", 12), bg="#e0e0e0", fg="#000000")

def boton_estilizado(boton):
    boton.config(font=("Segoe UI", 12), bg="#4CAF50", fg="#ffffff", padx=10, pady=5)

# ---------- FUNCIONES DE LÓGICA ----------
def iniciar_sesion(usuario, contrasena):
    """Maneja el inicio de sesión."""
    print(f"Usuario: {usuario}, Contraseña: {contrasena}")
    # Aquí puedes agregar la lógica para verificar credenciales en una base de datos

def crear_cuenta(nombre, apellido, celular, dni, correo):
    """Maneja la creación de una cuenta."""
    print(f"Nombre: {nombre}, Apellido: {apellido}, Celular: {celular}, DNI: {dni}, Correo: {correo}")
    # Aquí puedes agregar la lógica para guardar los datos en una base de datos

# ---------- VENTANAS ----------
def abrir_inicio_sesion():
    """Abre la ventana de inicio de sesión."""
    ventana_login = tk.Toplevel(ventana)
    ventana_login.title("Iniciar Sesión")
    ventana_login.geometry("300x350")
    ventana_login.configure(bg="#e0e0e0")

    # Etiqueta de bienvenida
    label_login = tk.Label(ventana_login, text="Iniciar Sesión")
    aplicar_estilos(label_login)
    label_login.pack(pady=15)

    # Campos de usuario y contraseña
    for texto in ["Usuario:", "Contraseña:"]:
        label = tk.Label(ventana_login, text=texto)
        aplicar_estilos(label)
        label.pack(pady=(10, 0))

        entry = tk.Entry(ventana_login, font=("Segoe UI", 12), show="*" if texto == "Contraseña:" else "")
        entry.pack(pady=5)
        
        if texto == "Usuario:":
            entry_usuario = entry
        else:
            entry_contrasena = entry

    # Botón de confirmación
    boton_confirmar = tk.Button(
        ventana_login, text="Confirmar",
        command=lambda: iniciar_sesion(entry_usuario.get(), entry_contrasena.get())
    )
    boton_estilizado(boton_confirmar)
    boton_confirmar.pack(pady=15)

def abrir_crear_cuenta():
    """Abre la ventana de creación de cuenta."""
    ventana_crear = tk.Toplevel(ventana)
    ventana_crear.title("Crear Cuenta")
    ventana_crear.geometry("300x400")
    ventana_crear.configure(bg="#e0e0e0")

    # Etiqueta de bienvenida
    label_crear = tk.Label(ventana_crear, text="Crear Cuenta")
    aplicar_estilos(label_crear)
    label_crear.pack(pady=15)

    # Campos de entrada
    etiquetas = ["Nombre:", "Apellido:", "Celular:", "DNI:", "Correo:"]
    entradas = {}

    for etiqueta in etiquetas:
        label = tk.Label(ventana_crear, text=etiqueta)
        aplicar_estilos(label)
        label.pack(pady=(10, 0))

        entry = tk.Entry(ventana_crear, font=("Segoe UI", 12))
        entry.pack(pady=5)
        entradas[etiqueta] = entry

    # Botón para confirmar la creación de cuenta
    boton_confirmar = tk.Button(
        ventana_crear, text="Crear Cuenta",
        command=lambda: crear_cuenta(
            entradas["Nombre:"].get(),
            entradas["Apellido:"].get(),
            entradas["Celular:"].get(),
            entradas["DNI:"].get(),
            entradas["Correo:"].get()
        )
    )
    boton_estilizado(boton_confirmar)
    boton_confirmar.pack(pady=15)

# ---------- VENTANA PRINCIPAL ----------
def main():
    """Función principal para iniciar la interfaz gráfica."""
    global ventana
    ventana = tk.Tk()
    ventana.title("BIENVENIDO A RUDOLFS")
    ventana.geometry("400x500")
    ventana.configure(bg="#e0e0e0")

    # Etiqueta de bienvenida
    label = tk.Label(ventana, text="Bienvenido")
    aplicar_estilos(label)
    label.pack(pady=20)

    # Botones de inicio de sesión y creación de cuenta
    botones = [
        ("Iniciar Sesión", abrir_inicio_sesion),
        ("Crear Cuenta", abrir_crear_cuenta)
    ]

    for texto, comando in botones:
        boton = tk.Button(ventana, text=texto, command=comando)
        boton_estilizado(boton)
        boton.pack(pady=10)

    # Etiqueta "¿Quiénes somos?"
    label_info = tk.Label(ventana, text="¿Quiénes somos?")
    aplicar_estilos(label_info)
    label_info.pack(pady=20)

    # Iniciar ventana
    ventana.mainloop()

if __name__ == "__main__":
    main()
