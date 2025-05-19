import flet as ft
import os
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scrip'))
from db import conectar_db

def crear_orden_servicio(page: ft.Page):
    page.title = "Orden de Servicio"
    page.scroll = "adaptive"

    # Funciones auxiliares
    def extraer_numero(texto):
        try:
            return float(texto.split("S/. ")[1])  # Extrae el número después de "S/. "
        except (IndexError, ValueError):
            return 0.00  # Retorna 0 si hay un error

    def validar_fecha(fecha_texto):
        try:
            return datetime.strptime(fecha_texto, "%Y-%m-%d %H:%M")
        except ValueError:
            print(f"❌ Error en la fecha: {fecha_texto} (Formato incorrecto)")
            return None

    def obtener_ultimo_folio():
        try:
            with conectar_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT folio FROM ordenservicio ORDER BY id DESC LIMIT 1;")
                    ultimo_folio = cursor.fetchone()

            if ultimo_folio is not None and len(ultimo_folio) > 0:
                ultimo_folio = ultimo_folio[0]
                if ultimo_folio.startswith("F") and ultimo_folio[1:].isdigit():
                    nuevo_numero = int(ultimo_folio[1:]) + 1
                    return f"F{nuevo_numero:03d}"

            return "F001"  # Devuelve el primer folio si no hay registros
        except Exception as e:
            print(f"Error al obtener el último folio: {e}")
            return "F001"

    def calcular_repuestos_cantidad(repuestos_desc):
        """Extrae la cantidad total de repuestos desde la descripción."""
        try:
            # Divide la descripción por " - " para obtener cada repuesto
            repuestos_list = repuestos_desc.split(" - ")
            total_cantidad = 0

            for repuesto in repuestos_list:
                # Busca la cantidad en la forma "(X x S/.Y)"
                cantidad_part = repuesto.split("(")[1].split("x")[0].strip() if "(" in repuesto and "x" in repuesto else None
                if cantidad_part and cantidad_part.isdigit():
                    total_cantidad += int(cantidad_part)

            return total_cantidad
        except Exception as e:
            print(f"Error al calcular la cantidad de repuestos: {e}")
            return 0

    # Componentes de la UI
    folio_actual = obtener_ultimo_folio()
    folio_text = ft.Text(f"Folio: {folio_actual}", size=20, weight="bold", color=ft.Colors.BLUE)

    mecanico_dropdown = ft.Dropdown(
        label="Nombre del Mecánico",
        options=[ft.dropdown.Option(name) for name in ["Rodolfo", "Mijael", "Julio", "Salvador", "Dani", "Marvin", "Rusbel"]],
        width=400
    )
    nuevo_mecanico = ft.TextField(label="Agregar nuevo mecánico", width=300)
    btn_agregar_mecanico = ft.ElevatedButton("➕ Añadir", on_click=lambda e: agregar_mecanico())

    def agregar_mecanico():
        nombre = nuevo_mecanico.value.strip()
        if nombre and nombre not in [op.key for op in mecanico_dropdown.options]:
            mecanico_dropdown.options.append(ft.dropdown.Option(nombre))
            mecanico_dropdown.value = nombre  # Opcional: selecciona el nuevo nombre
            nuevo_mecanico.value = ""
            page.update()


    cliente_nombre = ft.TextField(label="Nombre", width=300)
    cliente_dni = ft.TextField(label="DNI", width=200)
    cliente_telefono = ft.TextField(label="Teléfono", width=200)

    vehiculo_marca = ft.TextField(label="Marca", width=200)
    vehiculo_modelo = ft.TextField(label="Modelo", width=200)
    vehiculo_kilometraje = ft.TextField(label="Kilometraje", width=200)
    vehiculo_placa = ft.TextField(label="Placa", width=200)
    vehiculo_color = ft.TextField(label="Color", width=200)
    vehiculo_numero_serie = ft.TextField(label="Número de Serie", width=300)
    ingreso_grua = ft.Checkbox(label="Ingreso por grúa")

    fecha_ingreso = ft.TextField(label="Fecha de Ingreso (YYYY-MM-DD HH:MM)", width=300)
    fecha_salida = ft.TextField(label="Fecha de Salida (YYYY-MM-DD HH:MM)", width=300)

    trabajos = ft.Column()
    repuestos = ft.Column()
    trabajos_terceros = ft.Column()

    def calcular_resumen(e=None):
        total_trabajos = sum(float(row.controls[1].value or 0) for row in trabajos.controls)
        total_repuestos = sum(float(row.controls[1].value or 0) * float(row.controls[2].value or 0) for row in repuestos.controls)
        total_trabajos_terceros = sum(float(row.controls[1].value or 0) for row in trabajos_terceros.controls)

        descuento_trabajos_valor = float(descuento_trabajos.value or 0)
        descuento_repuestos_valor = float(descuento_repuestos.value or 0)

        total_trabajos_con_descuento = max(0, total_trabajos - descuento_trabajos_valor)
        total_repuestos_con_descuento = max(0, total_repuestos - descuento_repuestos_valor)

        total_price_sin_igv = total_trabajos_con_descuento + total_repuestos_con_descuento + total_trabajos_terceros
        igv_valor = total_price_sin_igv * 0.18
        total_total = total_price_sin_igv - igv_valor
        total_price_con_igv = total_total

        subtotal.value = f"Subtotal: S/. {total_total:.2f}"
        igv.value = f"IGV (18%): S/. {igv_valor:.2f}"
        total.value = f"Total: S/. {total_price_sin_igv:.2f}"
        page.update()

    def agregar_trabajo(e):
        trabajos.controls.append(ft.Row([ft.TextField(label="Descripción", expand=2),
                                          ft.TextField(label="Precio", width=300, on_change=calcular_resumen)]))
        page.update()

    def agregar_repuesto(e):
        repuestos.controls.append(ft.Row([ft.TextField(label="Descripción", expand=2),
                                          ft.TextField(label="Cantidad", width=200, on_change=calcular_resumen),
                                          ft.TextField(label="Precio Unitario", width=200, on_change=calcular_resumen)]))
        page.update()

    def agregar_trabajo_tercero(e):
        trabajos_terceros.controls.append(ft.Row([ft.TextField(label="Descripción", expand=2),
                                                  ft.TextField(label="Precio", width=300, on_change=calcular_resumen)]))
        page.update()

    descuento_trabajos = ft.TextField(label="Descuento Trabajos", width=200, on_change=calcular_resumen)
    descuento_repuestos = ft.TextField(label="Descuento Repuestos", width=200, on_change=calcular_resumen)

    subtotal = ft.Text("Subtotal: S/. 0.00", size=16)
    igv = ft.Text("IGV (18%): S/. 0.00", size=16)
    total = ft.Text("Total: S/. 0.00", size=16)

    pago_completado = ft.RadioGroup(content=ft.Column([ft.Radio(value="si", label="Sí"),
                                                      ft.Radio(value="no", label="No")]),
                                    on_change=lambda e: actualizar_seccion_pago())
    pago_completado.value = "no"

    metodo_pago = ft.Dropdown(
        label="Método de Pago",
        options=[ft.dropdown.Option("Efectivo"),
                 ft.dropdown.Option("Tarjeta"),
                 ft.dropdown.Option("Yape"),
                 ft.dropdown.Option("Plin"),
                 ft.dropdown.Option("BBVA"),
                 ft.dropdown.Option("BCP"),
                 ft.dropdown.Option("Interbank")],
        value="Efectivo",  # Valor predeterminado
        width=200
    )

    pago_adelantado = ft.TextField(label="Monto Adelantado", width=200, on_change=lambda e: calcular_faltante())
    pago_faltante_display = ft.Text("Falta por pagar: S/. 0.00", size=16)

    def actualizar_seccion_pago():
        pago_adelantado.visible = pago_completado.value == "no"
        if pago_completado.value == "no":
            calcular_faltante()
        page.update()

    def calcular_faltante():
        total_amount = extraer_numero(total.value.strip())  # Obtener el total
        adelanto = float(pago_adelantado.value or 0)  # Obtener el monto adelantado
        if adelanto > total_amount:
            page.add(ft.Text("❌ El pago adelantado no puede ser mayor que el total.", color=ft.Colors.RED))
            return
        faltante = max(0, total_amount - adelanto)  # Calcular faltante

        pago_faltante_display.value = f"Falta por pagar: S/. {faltante:.2f}"
        page.update()

    observaciones = ft.TextField(label="Observaciones", multiline=True, width=400)

    def reiniciar_formulario(e):
        for control in [cliente_nombre, cliente_dni, cliente_telefono, vehiculo_marca, vehiculo_modelo,
                        vehiculo_kilometraje, vehiculo_placa, vehiculo_color, vehiculo_numero_serie,
                        fecha_ingreso, fecha_salida, descuento_trabajos, descuento_repuestos, pago_adelantado]:
            control.value = ""
        ingreso_grua.value = False
        trabajos.controls.clear()
        repuestos.controls.clear()
        trabajos_terceros.controls.clear()
        subtotal.value = "Subtotal: S/. 0.00"
        igv.value = "IGV (18%): S/. 0.00"
        total.value = "Total: S/. 0.00"
        pago_faltante_display.value = "Falta por pagar: S/. 0.00"  # Reiniciar el campo de pago faltante
        page.update()

    def guardar_en_db(e):
        fecha_ing_dt = validar_fecha(fecha_ingreso.value)
        fecha_sal_dt = validar_fecha(fecha_salida.value)

        if fecha_ing_dt is None or fecha_sal_dt is None:
            print("❌ Error: Fecha incorrecta.")
            return

        # Convertimos datetime a string para evitar errores en SQL
        fecha_ing = fecha_ing_dt.strftime("%Y-%m-%d %H:%M:%S")
        fecha_sal = fecha_sal_dt.strftime("%Y-%m-%d %H:%M:%S")

        trabajo_desc = " - ".join([f"{row.controls[0].value} (S/.{row.controls[1].value})" for row in trabajos.controls])
        repuestos_desc = " - ".join([f"{row.controls[0].value} ({row.controls[1].value} x S/.{row.controls[2].value})" for row in repuestos.controls])
        trabajos_terc_desc = " - ".join([f"{row.controls[0].value} (S/.{row.controls[1].value})" for row in trabajos_terceros.controls])

        folio = obtener_ultimo_folio()
        folio_text.value = f"Folio: {folio}"

        mecanico_nombre = mecanico_dropdown.value or ""
        cliente_nombre_value = cliente_nombre.value or ""
        cliente_dni_value = cliente_dni.value or ""
        cliente_telefono_value = cliente_telefono.value or ""
        vehiculo_marca_value = vehiculo_marca.value or ""
        vehiculo_modelo_value = vehiculo_modelo.value or ""
        vehiculo_kilometraje_value = int(vehiculo_kilometraje.value or 0)
        vehiculo_placa_value = vehiculo_placa.value or ""
        vehiculo_color_value = vehiculo_color.value or ""
        vehiculo_numero_serie_value = vehiculo_numero_serie.value or ""
        ingreso_grua_value = bool(ingreso_grua.value)  # ✅ asegurar booleano

        descuento_trabajos_value = float(descuento_trabajos.value or 0.00)
        descuento_repuestos_value = float(descuento_repuestos.value or 0.00)
        pago_adelantado_value = float(pago_adelantado.value or 0.00)
        metodo_pago_value = metodo_pago.value or "Efectivo"
        pago_completado_value = True if pago_completado.value == "si" else False

        total_trabajos = sum(float(row.controls[1].value or 0) for row in trabajos.controls)
        total_repuestos = sum(float(row.controls[1].value or 0) * float(row.controls[2].value or 0) for row in repuestos.controls)
        total_trabajos_terceros = sum(float(row.controls[1].value or 0) for row in trabajos_terceros.controls)

        total_trabajos_value = round(total_trabajos, 2)
        total_repuestos_value = round(total_repuestos, 2)
        total_trabajos_terceros_value = round(total_trabajos_terceros, 2)

        try:
            with conectar_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO ordenservicio 
                        (folio, mecanico_nombre, cliente_nombre, cliente_dni, cliente_telefono, 
                        vehiculo_marca, vehiculo_modelo, vehiculo_kilometraje, vehiculo_placa,
                        vehiculo_color, vehiculo_numero_serie, ingreso_grua, 
                        fecha_ingreso, fecha_salida, trabajo_descripcion, trabajo_total,
                        repuestos_descripcion, repuestos_cantidad, repuestos_precio_unitario, repuestos_total,
                        trabajo_terceros_descripcion, trabajo_terceros_precio,
                        subtotal, descuento, igv, total, observaciones, metodo_pago, 
                        pago_completado, pago_adelantado, pago_faltante, descuento_repuestos)
                        VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s);
                        """,
                        (
                            folio, mecanico_nombre, cliente_nombre_value, cliente_dni_value, cliente_telefono_value,
                            vehiculo_marca_value, vehiculo_modelo_value, vehiculo_kilometraje_value,
                            vehiculo_placa_value, vehiculo_color_value, vehiculo_numero_serie_value,
                            ingreso_grua_value, fecha_ing, fecha_sal, trabajo_desc, total_trabajos_value,
                            repuestos_desc, calcular_repuestos_cantidad(repuestos_desc),  # repuestos cantidad
                            0.00, total_repuestos_value,  # No tienes precio unitario promedio, así que 0
                            trabajos_terc_desc, total_trabajos_terceros_value,
                            total_trabajos_value + total_repuestos_value + total_trabajos_terceros_value,  # subtotal
                            descuento_trabajos_value + descuento_repuestos_value,
                            (total_trabajos_value + total_repuestos_value + total_trabajos_terceros_value) * 0.18,  # igv
                            total_trabajos_value + total_repuestos_value + total_trabajos_terceros_value,  # total
                            observaciones.value or "", metodo_pago_value, pago_completado_value,
                            pago_adelantado_value,
                            max(0, (total_trabajos_value + total_repuestos_value + total_trabajos_terceros_value) - pago_adelantado_value),
                            descuento_repuestos_value
                        )
                    )

                    conn.commit()

            print(f"✔️ Orden de servicio {folio} guardada correctamente.")
            reiniciar_formulario(e)  # Limpiar el formulario tras guardar
            page.go("/inicio")  # Redirige a la ruta /inicio


        except Exception as ex:
            print(f"❌ Error al guardar la orden de servicio: {ex}")


    # UI Layout
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("🛠️ Crear Orden de Servicio", size=24, weight="bold", color="white"),

                # Sección: Datos Generales
                ft.Container(
                    content=ft.Column([
                        ft.Text("📋 Datos Generales", size=18, weight="bold"),
                        ft.Row([nuevo_mecanico, btn_agregar_mecanico]),

                        ft.Row([folio_text, mecanico_dropdown]),
                        ft.Row([fecha_ingreso, fecha_salida]),
                    ]),
                    border=ft.border.all(2, "#2196F3"),
                    border_radius=8,
                    padding=10
                ),

                # Sección: Datos del Cliente
                ft.Container(
                    content=ft.Column([
                        ft.Text("👤 Datos del Cliente", size=18, weight="bold"),
                        ft.Row([cliente_nombre, cliente_dni]),
                        cliente_telefono,
                    ]),
                    border=ft.border.all(2, "#2196F3"),
                    border_radius=8,
                    padding=10
                ),

                # Sección: Datos del Vehículo
                ft.Container(
                    content=ft.Column([
                        ft.Text("🏍️ Datos del Vehículo", size=18, weight="bold"),
                        ft.Row([vehiculo_marca, vehiculo_modelo]),
                        ft.Row([vehiculo_kilometraje, vehiculo_placa]),
                        ft.Row([vehiculo_color, vehiculo_numero_serie]),
                        ingreso_grua,
                    ]),
                    border=ft.border.all(2, "#2196F3"),
                    border_radius=8,
                    padding=10
                ),

                # Sección: Trabajos realizados
                ft.Container(
                    content=ft.Column([
                        ft.ElevatedButton("Agregar Trabajo", on_click=agregar_trabajo),
                        trabajos,  # Aquí va el contenido de los trabajos
                    ]),
                    border=ft.border.all(2, "#2196F3"),
                    border_radius=8,
                    padding=10
                ),

                # Sección: Repuestos utilizados
                ft.Container(
                    content=ft.Column([
                        ft.ElevatedButton("Agregar Repuesto", on_click=agregar_repuesto),
                        repuestos,  # Aquí va el contenido de los repuestos
                    ]),
                    border=ft.border.all(2, "#2196F3"),
                    border_radius=8,
                    padding=10
                ),

                # Sección: Trabajos de terceros
                ft.Container(
                    content=ft.Column([
                        ft.ElevatedButton("Agregar Trabajo Tercero", on_click=agregar_trabajo_tercero),
                        trabajos_terceros,  # Aquí va el contenido de los trabajos de terceros
                    ]),
                    border=ft.border.all(2, "#2196F3"),
                    border_radius=8,
                    padding=10
                ),

                # Totales
                ft.Container(
                    content=ft.Column([
                        ft.Text("💵 Costos", size=18, weight="bold"),
                        ft.Row([subtotal, igv, total]),
                        ft.Row([pago_completado, metodo_pago]),
                        ft.Row([pago_adelantado, pago_faltante_display]),
                    ]),
                    border=ft.border.all(2, "#2196F3"),
                    border_radius=8,
                    padding=10
                ),

                # Observaciones
                observaciones,

                ft.Row([
                    ft.ElevatedButton("Guardar", on_click=guardar_en_db),
                
                ], alignment="spaceAround"),
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,  # ✅ Aquí debe ir
        ),
        padding=20,
        expand=True,
        bgcolor="#121212",
        alignment=ft.alignment.top_center
    )



        
