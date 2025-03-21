import flet as ft

def crear_orden_servicio_ui(page: ft.Page, app_bar, footer):
    """Crea la interfaz para la orden de servicio con mejor diseño y scroll."""

    def crear_orden(e):
        print(f"Orden creada para {cliente.value}")
        print(f"Marca: {marca.value}, Modelo: {modelo.value}, Serie: {serie.value}, Kilometraje: {kilometraje.value}")
        print(f"Ingreso en grúa: {ingreso_en_grua.value}")

    def styled_textfield(label):
        return ft.TextField(
            label=label,
            color=ft.colors.WHITE,
            border_color=ft.colors.LIGHT_BLUE,
            bgcolor=ft.colors.BLUE_900,
            border_radius=10,
        )

    marca = styled_textfield("Marca de la Moto")
    modelo = styled_textfield("Modelo de la Moto")
    serie = styled_textfield("Número de Serie")
    kilometraje = styled_textfield("Kilometraje")
    ingreso_en_grua = ft.Dropdown(
        label="Ingreso en Grúa",
        options=[ft.dropdown.Option("Sí"), ft.dropdown.Option("No")],
        color=ft.colors.WHITE,
        border_color=ft.colors.LIGHT_BLUE,
        bgcolor=ft.colors.BLUE_900,
        border_radius=10,
    )
    cliente = styled_textfield("Nombre del Cliente")
    dni = styled_textfield("DNI del Cliente")
    telefono = styled_textfield("Teléfono del Cliente")
    descripcion_problema = styled_textfield("Descripción del Problema")
    estado_reparacion = ft.Dropdown(
        label="Estado de Reparación",
        options=[
            ft.dropdown.Option("Pendiente"),
            ft.dropdown.Option("En Progreso"),
            ft.dropdown.Option("Completado"),
        ],
        color=ft.colors.WHITE,
        border_color=ft.colors.LIGHT_BLUE,
        bgcolor=ft.colors.BLUE_900,
        border_radius=10,
    )

    boton_crear = ft.ElevatedButton(
        text="Crear Orden",
        on_click=crear_orden,
        style=ft.ButtonStyle(
            bgcolor=ft.colors.RED_ACCENT,
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
    )

    def mostrar_inicio(e):
        """Regresa a la pantalla principal."""
        page.go("/")  # ✅ Redirige a la pantalla de inicio sin importar `inicio.py`

    boton_retorno = ft.IconButton(
        icon=ft.icons.ARROW_BACK, 
        on_click=mostrar_inicio, 
        icon_color=ft.colors.WHITE
    )

    formulario = ft.Column(
        controls=[
            ft.Row([boton_retorno], alignment=ft.MainAxisAlignment.START),
            marca,
            modelo,
            serie,
            kilometraje,
            ingreso_en_grua,
            cliente,
            dni,
            telefono,
            descripcion_problema,
            estado_reparacion,
            boton_crear,
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return ft.Container(
        expand=True,
        alignment=ft.alignment.center,
        padding=20,
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Column(
                        [ft.Text("Orden de Servicio", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.LIGHT_BLUE)] +
                        formulario.controls,
                        spacing=10,
                    ),
                    padding=20,
                    border_radius=10,
                    bgcolor=ft.colors.BLACK,
                    shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.BLUE_700),
                ),
                ft.Container(height=20),  # Espacio para no tapar con el footer
                footer,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        ),
    )
