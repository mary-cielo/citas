def inicio_inicio(page):
    import sys
    import os
    import flet as ft

    # Agregar rutas adicionales
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrip'))

    # Importaciones de módulos
    from secundario.perfil.usuario import mostrar_perfil
    from secundario.citas.citas import mostrar_citas
    from secundario.citas.eventos import mostrar_reservas
    from secundario.citas.citasproy import vista_proyecciones_citas
    from secundario.servicio.ordenservicio import crear_orden_servicio
    from secundario.citas.totalproy import vista_proyecciones_ingresos
    from secundario.servicio.servicios import mostrar_servicios_app
    from secundario.mecanicos.mecanicos import mostrar_mecanicos


    # ============================
    # Constantes de Estilo
    # ============================
    BG_COLOR = "#121212"
    APP_BAR_COLOR = "#0D47A1"
    PRIMARY_COLOR = "#1976D2"
    SECONDARY_COLOR = "#1565C0"
    TEXT_COLOR = "#BBDEFB"

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    image_paths = [
        os.path.join(base_dir, "iconos", "logo.png"),
    ]

    # ============================
    # Función para mostrar el inicio
    # ============================
    def mostrar_inicio(page: ft.Page) -> ft.Container:
        welcome_text = ft.Text("Bienvenido al Tablero", size=30, color=TEXT_COLOR, weight=ft.FontWeight.BOLD)
        buttons = [
            ft.ElevatedButton("Crear Orden de Servicio", on_click=lambda e: page.go("/servicio/ordenservicio"), style=build_button_style(PRIMARY_COLOR)),
            ft.ElevatedButton("Ver Perfil", on_click=lambda e: page.go("/usuario"), style=build_button_style(PRIMARY_COLOR)),
            ft.ElevatedButton("Ver Proyección de Ingresos", on_click=lambda e: page.go("/citas/totalproy"), style=build_button_style(SECONDARY_COLOR)),
            ft.ElevatedButton("Ver Proyección de Citas", on_click=lambda e: page.go("/citas/citasproy"), style=build_button_style(PRIMARY_COLOR)),
        ]
        preview = ft.Container(
            content=ft.Text("📈 Próximas proyecciones disponibles. ¡Haz clic para más detalles!", size=16, color=TEXT_COLOR),
            padding=15, bgcolor="#1e1e1e", border_radius=12, alignment=ft.alignment.center,
        )
        return ft.Container(padding=40, border_radius=20, content=ft.Column(controls=[welcome_text, *buttons, preview], alignment=ft.MainAxisAlignment.CENTER, spacing=25))

    
    def main(page: ft.Page):
        page.title = "Tablero de Servicio"
        page.bgcolor = BG_COLOR
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.vertical_alignment = ft.MainAxisAlignment.CENTER

        def on_route_change(e):
            app_bar = build_app_bar(page)
            footer = build_footer(page)

            route_views = {
                "/": lambda: mostrar_inicio(page),
                "/usuario": lambda: mostrar_perfil(page),
                "/citas": lambda: mostrar_citas(page),
                "/citas/eventos": lambda: mostrar_reservas(page),
                "/citas/totalproy": lambda: vista_proyecciones_ingresos(page),
                "/citas/citasproy": lambda: vista_proyecciones_citas(page),
                "/servicio/ordenservicio": lambda: crear_orden_servicio(page),
                "/servicio/servicios": lambda: mostrar_servicios_app(page),
                "/mecanicos/mecanicos": lambda: mostrar_mecanicos(page),  # Ruta de mecánicos
            }

            content = route_views.get(page.route, lambda: mostrar_inicio(page))()
            view = ft.View(page.route, controls=[app_bar, content, footer])
            page.views.clear()
            page.views.append(view)
            page.update()

        page.on_route_change = on_route_change
        page.go("/")

    def build_app_bar(page: ft.Page) -> ft.AppBar:
        return ft.AppBar(
            bgcolor=APP_BAR_COLOR,
            leading=ft.IconButton(icon=ft.Icons.ACCOUNT_CIRCLE, icon_size=35, icon_color=TEXT_COLOR, on_click=lambda e: page.go("/usuario")),
            title=ft.Text("RUDOLF MOTOS", size=26, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
            center_title=True,
            actions=[build_menu_button(page)],
        )

    def build_footer(page: ft.Page) -> ft.Container:
        nav_buttons = [
            ("Inicio", ft.Icons.HOME, lambda e: page.go("/")),
            ("Servicios", ft.Icons.DESIGN_SERVICES, lambda e: page.go("/servicio/servicios")),
            ("Citas", ft.Icons.CALENDAR_TODAY, lambda e: page.go("/citas")),
            ("Mecánicos", ft.Icons.SETTINGS, lambda e: page.go("/mecanicos/mecanicos")),  # Agregado al footer
        ]
        return ft.Container(
            bgcolor=APP_BAR_COLOR,
            padding=15,
            alignment=ft.alignment.center,
            content=ft.Row(
                controls=[ft.ElevatedButton(text=label, icon=icon, on_click=callback, style=build_button_style(PRIMARY_COLOR))
                          for label, icon, callback in nav_buttons],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                spacing=15,
            ),
        )

    def build_menu_button(page: ft.Page) -> ft.PopupMenuButton:
        return ft.PopupMenuButton(
            icon=ft.Icons.MENU,
            icon_color=TEXT_COLOR,
            items=[
                ft.PopupMenuItem(text="Eventos", on_click=lambda e: page.go("/citas/eventos")),
                ft.PopupMenuItem(text="Mecánicos", on_click=lambda e: page.go("/mecanicos/mecanicos")),  
            ],
        )

    def build_button_style(bg_color: str) -> ft.ButtonStyle:
        return ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=bg_color,
            shape=ft.RoundedRectangleBorder(radius=15),
        )


    main(page)
