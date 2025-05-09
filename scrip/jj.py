import flet as ft
import os
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'scrip'))
from db import conectar_db  

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
        
        if ultimo_folio and len(ultimo_folio) > 0:
            ultimo_folio = ultimo_folio[0]
            if ultimo_folio.startswith("F") and ultimo_folio[1:].isdigit():
                nuevo_numero = int(ultimo_folio[1:]) + 1
                return f"F{nuevo_numero:03d}"
        
        return "F001"  # Devuelve el primer folio si no hay registros
    except Exception as e:
        print(f"Error al obtener el último folio: {e}")
        return "F001"

def main(page: ft.Page):
    page.title = "Orden de Servicio"
    page.scroll = "adaptive"

    folio_actual = obtener_ultimo_folio()
    folio_text = ft.Text(f"Folio: {folio_actual}", size=20, weight="bold", color=ft.Colors.BLUE)

    mecanico_dropdown = ft.Dropdown(
        label="Nombre del Mecánico",
        options=[ft.dropdown.Option(name) for name in ["Rodolfo", "Mijael", "Julio", "Dany"]],
        width=300
    )

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

    subtotal = ft.Text("Subtotal: S/. 0.00", size=16)
    igv = ft.Text("IGV (18%): S/. 0.00", size=16)
    total = ft.Text("Total: S/. 0.00", size=16)

    descuento_trabajos = ft.TextField(label="Descuento Trabajos", width=200, on_change=lambda e: calcular_resumen())
    descuento_repuestos = ft.TextField(label="Descuento Repuestos", width=200, on_change=lambda e: calcular_resumen())

    pago_completado = ft.RadioGroup(
        content=ft.Column([
            ft.Radio(value="si", label="Sí"),
            ft.Radio(value="no", label="No"),
        ]),
        on_change=lambda e: actualizar_seccion_pago()
    )
    pago_completado.value = "no"

    pago_adelantado = ft.TextField(label="Monto Adelantado", width=200, on_change=lambda e: calcular_faltante())
    pago_faltante_display = ft.Text("Falta por pagar: S/. 0.00", size=16)

    observaciones = ft.TextField(label="Observaciones", multiline=True, width=400)

    def calcular_resumen(e=None):
        total_trabajos = sum(float(row.controls[1].value or 0) for row in trabajos.controls)
        total_repuestos = sum(float(row.controls[1].value or 0) * float(row.controls[2].value or 0) for row in repuestos.controls)
        total_trabajos_terceros = sum(float(row.controls[1].value or 0) for row in trabajos_terceros.controls)

        subtotal.value = f"Subtotal: S/. {total_trabajos + total_repuestos + total_trabajos_terceros:.2f}"
        igv.value = f"IGV (18%): S/. {(total_trabajos + total_repuestos + total_trabajos_terceros) * 0.18:.2f}"
        total.value = f"Total: S/. {(total_trabajos + total_repuestos + total_trabajos_terceros) * 1.18:.2f}"
        page.update()

    def agregar_trabajo(e):
        trabajos.controls.append(ft.Row([
            ft.TextField(label="Descripción", expand=2),
            ft.TextField(label="Precio", width=100, on_change=calcular_resumen),
        ]))
        page.update()

    def agregar_repuesto(e):
        repuestos.controls.append(ft.Row([
            ft.TextField(label="Descripción", expand=2),
            ft.TextField(label="Cantidad", width=100, on_change=calcular_resumen),
            ft.TextField(label="Precio Unitario", width=100, on_change=calcular_resumen),
        ]))
        page.update()

    def agregar_trabajo_tercero(e):
        trabajos_terceros.controls.append(ft.Row([
            ft.TextField(label="Descripción", expand=2),
            ft.TextField(label="Precio", width=100, on_change=calcular_resumen),
        ]))
        page.update()

    def actualizar_seccion_pago():
        pago_adelantado.visible = pago_completado.value == "no"
        pago_faltante_display.visible = pago_completado.value == "no"
        calcular_faltante()
        page.update()

    def calcular_faltante():
        total_amount = float(total.value.replace("Total: S/. ", "") or 0)
        adelanto = float(pago_adelantado.value or 0)
        faltante = max(0, total_amount - adelanto)
        pago_faltante_display.value = f"Falta por pagar: S/. {faltante:.2f}"
        page.update()

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
        pago_faltante_display.value = "Falta por pagar: S/. 0.00"
        page.update()

    def guardar_en_db(e):
        fecha_ing = validar_fecha(fecha_ingreso.value)
        fecha_sal = validar_fecha(fecha_salida.value)

        if fecha_ing is None or fecha_sal is None:
            print("❌ Error: Fecha incorrecta.")
            return

        folio = obtener_ultimo_folio()
        folio_text.value = f"Folio: {folio}"

        trabajo_desc = " - ".join(
            [f"{row.controls[0].value} (S/.{row.controls[1].value})" for row in trabajos.controls]
        ) or "N/A"

        repuestos_desc = " - ".join(
            [f"{row.controls[0].value} (S/.{row.controls[2].value})" for row in repuestos.controls]
        ) or "N/A"

        trabajos_terc_desc = " - ".join(
            [f"{row.controls[0].value} (S/.{row.controls[1].value})" for row in trabajos_terceros.controls]
        ) or "N/A"

        total_trabajos = sum(float(row.controls[1].value or 0) for row in trabajos.controls)
        total_repuestos = sum(float(row.controls[1].value or 0) * float(row.controls[2].value or 0) for row in repuestos.controls)
        total_trabajos_terceros = sum(float(row.controls[1].value or 0) for row in trabajos_terceros.controls)

        subtotal_valor = total_trabajos + total_repuestos + total_trabajos_terceros
        igv_valor = subtotal_valor * 0.18
        total_valor = subtotal_valor + igv_valor

        pago_adelantado_valor = float(pago_adelantado.value or 0)
        pago_faltante_valor = max(0, total_valor - pago_adelantado_valor)

        repuesto_cantidad = sum(int(row.controls[1].value or 0) for row in repuestos.controls)

        try:
            with conectar_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO ordenservicio (
                            folio, mecanico_nombre, cliente_nombre, cliente_dni, cliente_telefono,
                            vehiculo_marca, vehiculo_modelo, vehiculo_kilometraje, vehiculo_placa,
                            vehiculo_color, vehiculo_numero_serie, ingreso_grua, fecha_ingreso,
                            fecha_salida, trabajo_descripcion, trabajo_total,
                            repuestos_descripcion, repuesto_precio_unitario, repuesto_cantidad, repuestos_total,
                            trabajo_terceros_descripcion, trabajo_terceros_precio, subtotal, 
                            descuento, igv, total, observaciones, metodo_pago, 
                            pago_completado, pago_adelantado, pago_faltante, descuento_repuestos
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        folio, mecanico_dropdown.value, cliente_nombre.value or "",
                        cliente_dni.value or "", cliente_telefono.value or "", vehiculo_marca.value or "",
                        vehiculo_modelo.value or "", int(vehiculo_kilometraje.value or 0), vehiculo_placa.value or "",
                        vehiculo_color.value or "", vehiculo_numero_serie.value or "", ingreso_grua.value,
                        fecha_ing, fecha_sal, trabajo_desc, total_trabajos or 0.00,
                        repuestos_desc, 0.00, repuesto_cantidad, total_repuestos or 0.00,
                        trabajos_terc_desc, total_trabajos_terceros or 0.00,
                        subtotal_valor, float(descuento_trabajos.value or 0),
                        igv_valor, total_valor, observaciones.value or "", 
                        "Efectivo", pago_completado.value == "si", pago_adelantado_valor,
                        pago_faltante_valor, float(descuento_repuestos.value or 0)
                    ))
                    conn.commit()
                print("✅ Datos guardados correctamente")
        except Exception as ex:
            print(f"❌ Error al guardar: {ex}")
            print("Valores que intentas insertar:")
            print(f"Folio: {folio}, Mecánico: {mecanico_dropdown.value}, Cliente Nombre: {cliente_nombre.value}, "
                f"DNI: {cliente_dni.value}, Teléfono: {cliente_telefono.value}, Marca: {vehiculo_marca.value}, "
                f"Modelo: {vehiculo_modelo.value}, Kilometraje: {vehiculo_kilometraje.value}, "
                f"Placa: {vehiculo_placa.value}, Color: {vehiculo_color.value}, "
                f"Número de Serie: {vehiculo_numero_serie.value}, Ingreso por Grúa: {ingreso_grua.value}, "
                f"Fecha Ingreso: {fecha_ing}, Fecha Salida: {fecha_sal}, "
                f"Trabajo Descripción: {trabajo_desc}, Total: {total_valor}, "
                f"Repuestos Descripción: {repuestos_desc}, "
                f"Subtotal: {subtotal_valor}, Descuento: {float(descuento_trabajos.value or 0)}, "
                f"IGV: {igv_valor}, Observaciones: {observaciones.value}, "
                f"Método de Pago: Efectivo, Pago Completado: {pago_completado.value == 'si'}, "
                f"Monto Adelantado: {pago_adelantado_valor}, "
                f"Pago Faltante: {pago_faltante_valor}, "
                f"Descuento Repuestos: {float(descuento_repuestos.value or 0)}")

    page.add(
        ft.Column([
            folio_text,
            ft.Text("Orden de Servicio", size=24, weight="bold"),
            mecanico_dropdown,
            cliente_nombre, cliente_dni, cliente_telefono,
            vehiculo_marca, vehiculo_modelo, vehiculo_kilometraje,
            vehiculo_placa, vehiculo_color, vehiculo_numero_serie,
            ingreso_grua, fecha_ingreso, fecha_salida,
            ft.Text("Trabajos", weight="bold"),
            trabajos,
            ft.ElevatedButton("Agregar Trabajo", on_click=agregar_trabajo),
            descuento_trabajos,
            ft.Text("Repuestos", weight="bold"),
            repuestos,
            ft.ElevatedButton("Agregar Repuesto", on_click=agregar_repuesto),
            descuento_repuestos,
            ft.Text("Trabajos de Terceros", weight="bold"),
            trabajos_terceros,
            ft.ElevatedButton("Agregar Trabajo Tercero", on_click=agregar_trabajo_tercero),
            subtotal, igv, total,
            ft.Text("Pago Completado", size=18, weight="bold"),
            pago_completado, pago_adelantado, pago_faltante_display,
            observaciones,
            ft.ElevatedButton("Reiniciar Formulario", on_click=reiniciar_formulario, bgcolor=ft.Colors.RED),
            ft.ElevatedButton("Guardar", on_click=guardar_en_db)
        ])
    )

ft.app(target=main)