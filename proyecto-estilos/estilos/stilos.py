import tkinter as tk

class RoundedButton(tk.Canvas):
    """Crea un botón redondeado con colores personalizados."""
    def __init__(self, parent, text, command=None, color_base="#007BFF", color_hover="#0056b3"):
        super().__init__(parent, width=250, height=50, bg=parent["bg"], highlightthickness=0)
        self.command = command
        self.color_base = color_base
        self.color_hover = color_hover
        self.text = text

        # Crear botón redondeado
        self.create_oval(2, 2, 48, 48, fill=color_base, outline=color_base)  # Esquina izquierda
        self.create_oval(202, 2, 250, 48, fill=color_base, outline=color_base)  # Esquina derecha
        self.create_rectangle(25, 2, 225, 48, fill=color_base, outline=color_base)  # Cuerpo del botón

        self.text_id = self.create_text(125, 25, text=text, font=("Segoe UI", 14, "bold"), fill="white")

        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)

    def on_click(self, event):
        if self.command:
            self.command()

    def on_hover(self, event):
        self.itemconfig(self.find_all()[0], fill=self.color_hover)  # Cambia color al hacer hover

    def on_leave(self, event):
        self.itemconfig(self.find_all()[0], fill=self.color_base)  # Vuelve al color original

def aplicar_estilos(widget):
    """Aplica estilos personalizados a etiquetas y textos."""
    widget.configure(bg="#f5f7fa", fg="#333", font=("Segoe UI", 16, "bold"), padx=10, pady=5)

# Crear ventana
ventana = tk.Tk()
ventana.title("BIENVENIDO A RUDOLFS")
ventana.geometry("450x550")
ventana.configure(bg="#e8ecf1")  # Fondo gris claro

# Contenedor principal
frame = tk.Frame(ventana, bg="#f5f7fa", padx=20, pady=20)
frame.pack(expand=True, fill="both")

# Etiqueta de bienvenida
label = tk.Label(frame, text="✨ Bienvenido a Rudolfs ✨")
aplicar_estilos(label)
label.pack(pady=20)

# Botón Iniciar Sesión
boton_inicio = RoundedButton(frame, "🔵 Iniciar Sesión", color_base="#007BFF", color_hover="#0056b3")
boton_inicio.pack(pady=15)

# Botón Crear Cuenta
boton_crear = RoundedButton(frame, "🟢 Crear Cuenta", color_base="#007BFF", color_hover="#0056b3")
boton_crear.pack(pady=15)

# Línea divisoria
separator = tk.Frame(frame, height=2, width=300, bg="#007BFF")
separator.pack(pady=20)

# Etiqueta "¿Quiénes somos?"
label_info = tk.Label(frame, text="💡 ¿Quiénes somos?")
aplicar_estilos(label_info)
label_info.pack(pady=10)

# Footer con información adicional
footer = tk.Label(frame, text="© 2025 Rudolfs. Todos los derechos reservados.", bg="#f5f7fa", font=("Segoe UI", 10))
footer.pack(side="bottom", pady=10)

# Iniciar ventana
ventana.mainloop()