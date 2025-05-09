import flet as ft

def main(page: ft.Page):
    page.title = "Sticker de Cambio de Aceite"
    page.bgcolor = "#F0F4F8"  # Fondo más suave para la página

    # Contenido del sticker con la imagen de fondo
    sticker_content = ft.Stack(
        [
            ft.Container(
                ft.Image(
                    src="../iconos/1.ico",  # Ruta a la imagen
                    width=400,
                    height=400,
                    fit=ft.ImageFit.COVER,  # Ajustar la imagen para cubrir el contenedor
                    opacity=0.9,  # Ajustar la opacidad para que sea translúcida
                ),
                width=400,
                height=400,
                border_radius=100,  # Bordes redondeados para hacer la imagen circular
                alignment=ft.alignment.center,
                bgcolor=ft.colors.TRANSPARENT,  # Fondo transparente
            ),
            ft.Column(
                [
                    ft.Text("CAMBIO DE ACEITE", size=24, weight="bold", color=ft.colors.BLACK),
                    ft.Text("Aceite: __________", size=16, color=ft.colors.BLACK),
                    ft.Text("Fecha: __________", size=16, color=ft.colors.BLACK),
                    ft.Text("Ruta: __________", size=16, color=ft.colors.BLACK),
                    ft.Text("Próximo Cambio: __________", size=16, color=ft.colors.BLACK),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=14
            ),
        ],
        alignment=ft.alignment.center  # Alinear el contenido del Stack al centro
    )

    # Diseño del sticker con bordes suaves
    sticker = ft.Container(
        content=sticker_content,
        width=400,
        height=400,
        border_radius=200,
        alignment=ft.alignment.center,
        border=ft.border.all(3, ft.colors.CYAN_800),
    )

    # Agregar sombra usando Container con una nueva configuración
    inner_sticker = ft.Container(
        content=sticker,
        width=380,
        height=380,
        border_radius=190,
        bgcolor=ft.colors.WHITE,
        alignment=ft.alignment.center,
        border=ft.border.all(2, ft.colors.CYAN_400),
        padding=15,
    )

    # Agregar el sticker a la página
    page.add(inner_sticker)

ft.app(target=main)