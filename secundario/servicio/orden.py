import flet as ft
from datetime import datetime
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scrip'))
from db import conectar_db  

def obtener_ultimo_folio():
    """Obtiene el último folio registrado en la base de datos y genera el siguiente en la secuencia."""
    try:
        with conectar_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT folio FROM ordenes_servicio ORDER BY id DESC LIMIT 1;")
                ultimo_folio = cursor.fetchone()

        if ultimo_folio:
            ultimo_folio = ultimo_folio[0]
            if ultimo_folio.startswith("F") and ultimo_folio[1:].isdigit():
                nuevo_numero = int(ultimo_folio[1:]) + 1
                return f"F{nuevo_numero:03d}"

        return "F001"
    except Exception as e:
        print(f"Error al obtener el último folio: {e}")
        return "F001"

def styled_textfield(label, initial_value=""):
    """Crea un campo de texto estilizado."""
    return ft.TextField(
        label=label,
        color=ft.colors.WHITE,
        border_color=ft.colors.LIGHT_BLUE,
        bgcolor=ft.colors.BLUE_900,
        border_radius=10,
        value=initial_value,
        expand=True
    )

def calcular_totales(precios_servicios, precios_repuestos, precios_terceros, descuento, descuento_repuestos):
    """Calcula y retorna el Total, IGV y Subtotal."""
    try:
        total_servicios = sum(precios_servicios) - float(descuento)
        total_repuestos = sum(cantidad * precio for cantidad, precio in precios_repuestos) - float(descuento_repuestos)
        total_general = total_servicios + total_repuestos + sum(precios_terceros)
        igv = total_general * 0.18
        subtotal = total_general - igv
        return total_general, igv, subtotal
    except Exception as e:
        print(f"Error al calcular totales: {e}")
        return 0, 0, 0

def crear_orden_servicio_ui(page: ft.Page, app_bar, footer):
    """Crea la interfaz para la orden de servicio."""
    
    folio_inicial = obtener_ultimo_folio()
    trabajo_precios = []
    repuestos_precios = []
    trabajo_terceros_precios = []
    descuento_servicio = 0
    descuento_repuestos = 0

    # Definir campos
    folio = styled_textfield("Folio", folio_inicial)
    cliente_nombre = styled_textfield("Nombre del Cliente")
    cliente_dni = styled_textfield("DNI del Cliente")
    fecha_ingreso = styled_textfield("Ingrese Ingreso")
    fecha_salida = styled_textfield("Ingrese Salida")
    cliente_telefono = styled_textfield("Teléfono del Cliente")
    ingreso_grua = ft.Dropdown(
        label="Ingreso en Grúa",
        options=[ft.dropdown.Option("Sí"), ft.dropdown.Option("No")],
        color=ft.colors.WHITE,
        border_color=ft.colors.LIGHT_BLUE,
        bgcolor=ft.colors.BLUE_900,
        border_radius=10,
    )
    vehiculo_marca = styled_textfield("Marca de la Moto")
    vehiculo_modelo = styled_textfield("Modelo de la Moto")
    vehiculo_numero_serie = styled_textfield("Número de Serie")
    vehiculo_kilometraje = styled_textfield("Kilometraje")
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
    mecanico_nombre = styled_textfield("Nombre del Mecánico")
    vehiculo_color = styled_textfield("Color del Vehículo")
    vehiculo_placa = styled_textfield("Placa del Vehículo")    
    observaciones = styled_textfield("Observaciones...")

    # Texto para totales
    total_text = ft.Text("Total: S/. 0.00", color=ft.colors.WHITE, size=18, weight=ft.FontWeight.BOLD)
    igv_text = ft.Text("IGV (18%): S/. 0.00", color=ft.colors.WHITE, size=18)
    subtotal_text = ft.Text("Subtotal: S/. 0.00", color=ft.colors.WHITE, size=18)
    totales = ft.Column([total_text, igv_text, subtotal_text], spacing=5)

    def agregar_fila(tabla, lista_precios, columnas):
        """Agrega una fila a la tabla y actualiza los totales."""
        inputs = [styled_textfield(col) for col in columnas]
        lista_precios.append((0, 0) if "Cantidad" in columnas else 0)

        def on_change(e, idx=len(lista_precios)-1):
            try:
                if "Cantidad" in columnas:
                    cantidad = int(inputs[columnas.index("Cantidad")].value) if inputs[columnas.index("Cantidad")].value else 0
                    precio = float(inputs[columnas.index("Precio")].value) if inputs[columnas.index("Precio")].value else 0
                    lista_precios[idx] = (cantidad, precio)
                else:
                    lista_precios[idx] = float(inputs[columnas.index("Precio")].value) if inputs[columnas.index("Precio")].value else 0
                total_general, igv, subtotal = calcular_totales(trabajo_precios, repuestos_precios, trabajo_terceros_precios, descuento_servicio_field.value, descuento_repuestos_field.value)
                total_text.value = f"Total: S/. {total_general:.2f}"
                igv_text.value = f"IGV (18%): S/. {igv:.2f}"
                subtotal_text.value = f"Subtotal: S/. {subtotal:.2f}"
                page.update()
            except ValueError:
                print("Error en el valor ingresado")

        for input_field in inputs:
            input_field.on_change = on_change

        fila = ft.Row(inputs, alignment=ft.MainAxisAlignment.SPACE_AROUND)
        tabla.controls.append(fila)
        page.update()

    def crear_tabla(nombre, lista_precios, columnas):
        """Crea una tabla dinámica con un botón '+'."""
        titulo = ft.Text(nombre, color=ft.colors.WHITE, size=20, weight=ft.FontWeight.BOLD)
        tabla = ft.Column(spacing=10)
        boton_agregar = ft.IconButton(
            icon=ft.icons.ADD_CIRCLE_OUTLINE,
            icon_color=ft.colors.LIGHT_BLUE,
            on_click=lambda e: agregar_fila(tabla, lista_precios, columnas)
        )
        return ft.Column([ft.Row([titulo, boton_agregar], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), tabla], spacing=10)

    # Crear tablas
    tabla_servicios = crear_tabla("Servicios", trabajo_precios, ["Descripción", "Precio"])
    descuento_servicio_field = styled_textfield("Descuento en Servicio", "0")
    tabla_repuestos = crear_tabla("Repuestos", repuestos_precios, ["Descripción", "Cantidad", "Precio Unitario"])
    descuento_repuestos_field = styled_textfield("Descuento en Repuestos", "0")
    tabla_terceros = crear_tabla("Trabajos de Terceros", trabajo_terceros_precios, ["Descripción", "Precio"])
    # Organizar los campos y tablas en la interfaz
    formulario = ft.Column(
        controls=[
            ft.Row([folio, mecanico_nombre]),
            ft.Row([vehiculo_marca, vehiculo_modelo]),
            ft.Row([vehiculo_numero_serie, vehiculo_kilometraje]),
            ft.Row([ingreso_grua, estado_reparacion]),
            ft.Row([cliente_nombre, cliente_dni]),
            ft.Row([cliente_telefono, vehiculo_color]),
            ft.Row([fecha_ingreso, fecha_salida]),
            ft.Row([vehiculo_placa]),
            tabla_servicios,
            ft.Row([descuento_servicio_field]),
            tabla_repuestos,
            ft.Row([descuento_repuestos_field]),
            tabla_terceros,
            totales,
            ft.Row([observaciones]),
            ft.ElevatedButton(
                text="Crear Orden",
                on_click=lambda e: crear_orden(),
                style=ft.ButtonStyle(bgcolor=ft.colors.RED_ACCENT, shape=ft.RoundedRectangleBorder(radius=10)),
            ),
        ],
        spacing=15,
        scroll=ft.ScrollMode.AUTO
    )

    def crear_orden():
        try:
            # Obtener valores de los campos
            datos = {
                "folio": folio.value,
                "mecanico_nombre": mecanico_nombre.value,
                "cliente_nombre": cliente_nombre.value,
                "cliente_dni": cliente_dni.value,
                "cliente_telefono": cliente_telefono.value,
                "vehiculo_marca": vehiculo_marca.value,
                "vehiculo_modelo": vehiculo_modelo.value,
                "vehiculo_color": vehiculo_color.value,
                "vehiculo_placa": vehiculo_placa.value,
                "vehiculo_numero_serie": vehiculo_numero_serie.value,
                "vehiculo_kilometraje": int(vehiculo_kilometraje.value) if vehiculo_kilometraje.value.isdigit() else 0,
                "ingreso_grua": ingreso_grua.value == "Sí",
                "fecha_ingreso": datetime.strptime(fecha_ingreso.value, "%Y-%m-%d") if fecha_ingreso.value else None,
                "fecha_salida": datetime.strptime(fecha_salida.value, "%Y-%m-%d") if fecha_salida.value else None,
                "estado_reparacion": estado_reparacion.value,
                "observaciones": observaciones.value
            }

            # Insertar datos en la base de datos
            with conectar_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO ordenes_servicio (
                            folio, mecanico_nombre, cliente_nombre, cliente_dni, cliente_telefono,
                            vehiculo_marca, vehiculo_modelo, vehiculo_color, vehiculo_placa,
                            vehiculo_numero_serie, vehiculo_kilometraje, ingreso_grua,
                            fecha_ingreso, fecha_salida, estado_reparacion, observaciones
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, tuple(datos.values()))
                    conn.commit()
            
            print("✅ Orden de servicio guardada correctamente")
            page.snack_bar = ft.SnackBar(content=ft.Text("Orden guardada exitosamente"), bgcolor=ft.colors.GREEN)
            page.snack_bar.open = True
            page.update()

        except Exception as e:
            print(f"❌ Error al guardar la orden: {e}")
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {e}"), bgcolor=ft.colors.RED)
            page.snack_bar.open = True
            page.update()

    boton_guardar = ft.ElevatedButton(text="Guardar Orden", on_click= crear_orden, bgcolor=ft.colors.RED_ACCENT)

    # Estructura de la UI
    formulario = ft.Column([
        folio, mecanico_nombre, cliente_nombre, cliente_dni, cliente_telefono,
        vehiculo_marca, vehiculo_modelo, vehiculo_color, vehiculo_placa,
        vehiculo_numero_serie, vehiculo_kilometraje, ingreso_grua,
        fecha_ingreso, fecha_salida, estado_reparacion, observaciones,
        boton_guardar
    ], spacing=10)


    return ft.Container(expand=True, alignment=ft.alignment.center, padding=20, content=formulario)

if __name__ == "__main__":
    ft.app(target=crear_orden_servicio_ui)