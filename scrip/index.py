import sys
import os
import tkinter as tk
import db

 # Asegurar que `db.py` tenga esta función

# Asegurar que Python encuentre la carpeta raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ---------- FUNCIONES AUXILIARES ----------
def aplicar_estilos(widget):
    widget.config(font=("Segoe UI", 12), bg="#e0e0e0", fg="#000000")

def boton_estilizado(boton):
    boton.config(font=("Segoe UI", 12), bg="#4CAF50", fg="#ffffff", padx=10, pady=5)

# ---------- FUNCIONES DE BASE DE DATOS ----------
def insertar_usuario(nombre, apellido, celular, dni, correo, contraseña):
    """Inserta un nuevo usuario en la base de datos."""
    conn = db.conectar_db() 
    if conn:
        cursor = conn.cursor()
        try:
            query = '''INSERT INTO usuario (nombre, apellido, celular, dni, correo, contraseña) 
                       VALUES (%s, %s, %s, %s, %s , %s)'''
            cursor.execute(query, (nombre, apellido, celular, dni, correo, contraseña))
            conn.commit()
            print("✅ Registro exitoso.")
        except Exception as e:
            print(f"❌ Error al insertar usuario: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

def crear_cuenta(nombre, apellido, celular, dni, correo, contraseña):
    """Maneja la creación de una cuenta con validaciones."""
    if not nombre or not apellido or not celular or not dni or not correo or not contraseña:
        print("⚠️ Todos los campos son obligatorios.")
        return
    if "@" not in correo:
        print("❌ Correo inválido.")
        return
    try:
        insertar_usuario(nombre, apellido, celular, dni, correo, contraseña)
        print("✅ Cuenta creada exitosamente.")
    except Exception as e:
        print(f"❌ Error al crear cuenta: {e}")

# ---------- FUNCIONES DE INTERFAZ ----------
def iniciar_sesion(usuario, contrasena):
    """Maneja el inicio de sesión."""
    print(f"Usuario: {usuario}, Contraseña: {contrasena}")
    # Aquí puedes agregar la lógica para verificar credenciales en la base de datos

def abrir_inicio_sesion():
    """Abre la ventana de inicio de sesión."""
    ventana_login = tk.Toplevel(ventana)
    ventana_login.title("Iniciar Sesión")
    ventana_login.geometry("300x350")
    ventana_login.configure(bg="#e0e0e0")

    label_login = tk.Label(ventana_login, text="Iniciar Sesión")
    aplicar_estilos(label_login)
    label_login.pack(pady=15)

    label_usuario = tk.Label(ventana_login, text="Usuario:")
    aplicar_estilos(label_usuario)
    label_usuario.pack(pady=(10, 0))

    entry_usuario = tk.Entry(ventana_login, font=("Segoe UI", 12))
    entry_usuario.pack(pady=5)

    label_contrasena = tk.Label(ventana_login, text="Contraseña:")
    aplicar_estilos(label_contrasena)
    label_contrasena.pack(pady=(10, 0))

    entry_contrasena = tk.Entry(ventana_login, font=("Segoe UI", 12), show="*")
    entry_contrasena.pack(pady=5)

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
    ventana_crear.geometry("300x600")
    ventana_crear.configure(bg="#e0e0e0")

    label_crear = tk.Label(ventana_crear, text="Crear Cuenta")
    aplicar_estilos(label_crear)
    label_crear.pack(pady=15)

    etiquetas = ["Nombre:", "Apellido:", "Celular:", "DNI:", "Correo:", "Contraseña:"]
    entradas = {}

    for etiqueta in etiquetas:
        label = tk.Label(ventana_crear, text=etiqueta)
        aplicar_estilos(label)
        label.pack(pady=(10, 0))

        entry = tk.Entry(ventana_crear, font=("Segoe UI", 12))
        entry.pack(pady=5)
        entradas[etiqueta] = entry

    boton_confirmar = tk.Button(
        ventana_crear, text="Crear Cuenta",
        command=lambda: crear_cuenta(
            entradas["Nombre:"].get(),
            entradas["Apellido:"].get(),
            entradas["Celular:"].get(),
            entradas["DNI:"].get(),
            entradas["Correo:"].get(),
            entradas["Contraseña:"].get()
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

    label = tk.Label(ventana, text="Bienvenido")
    aplicar_estilos(label)
    label.pack(pady=20)

    botones = [
        ("Iniciar Sesión", abrir_inicio_sesion),
        ("Crear Cuenta", abrir_crear_cuenta)
    ]

    for texto, comando in botones:
        boton = tk.Button(ventana, text=texto, command=comando)
        boton_estilizado(boton)
        boton.pack(pady=10)

    label_info = tk.Label(ventana, text="¿Quiénes somos?")
    aplicar_estilos(label_info)
    label_info.pack(pady=20)

    ventana.mainloop()

if __name__ == "__main__":
    main()
