import flet as ft

def mostrar_bienvenida(page, nombre, mostrar_inicio):
    """Muestra una ventana de bienvenida con mejor diseño."""
    page.clean()  # Limpiar la pantalla anterior

    # Contenedor de bienvenida con estilo
    contenedor_bienvenida = ft.Container(
        width=800,
        height=500,
        bgcolor="#28A745",  # Verde éxito
        border_radius=20,
        padding=50,
        content=ft.Column(
            [
                ft.Text(
                    f"🎉 ¡Bienvenido, {nombre}! 🎉",
                    size=28,
                    weight="bold",
                    color="white",
                    text_align="center"
                ),
                ft.Text(
                    "Tu cuenta ha sido creada con éxito.\nPuedes explorar la plataforma o volver a la pantalla de inicio.",
                    size=16,
                    color="white",
                    text_align="center"
                ),
                ft.ElevatedButton(
                    "Volver a Iniciar Sesión",
                    bgcolor="#007BFF",  # Azul primario
                    color="white",
                    on_click=lambda e: mostrar_inicio(),  # Llama a mostrar_inicio
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                    )
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        )
    )

    # Agregar el contenedor al diseño de la página
    page.add(
        ft.Row(
            [contenedor_bienvenida],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )

# Asegúrate de que `mostrar_inicio` esté definido en tu código principal.