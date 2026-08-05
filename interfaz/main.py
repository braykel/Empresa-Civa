import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import hashlib
import json
from datetime import datetime
import subprocess
import tempfile

# ==============================================
# CONSULTA RENIEC - BASE DE DATOS LOCAL
# ==============================================

BASE_DATOS_PRUEBA = {
    "12345678": {
        "nombre_completo": "JUAN CARLOS PEREZ GOMEZ",
        "nombres": "JUAN CARLOS",
        "apellido_paterno": "PEREZ",
        "apellido_materno": "GOMEZ"
    },
    "87654321": {
        "nombre_completo": "MARIA ELENA LOPEZ FLORES",
        "nombres": "MARIA ELENA",
        "apellido_paterno": "LOPEZ",
        "apellido_materno": "FLORES"
    },
    "45678912": {
        "nombre_completo": "PEDRO ANTONIO RAMIREZ SANCHEZ",
        "nombres": "PEDRO ANTONIO",
        "apellido_paterno": "RAMIREZ",
        "apellido_materno": "SANCHEZ"
    },
    "78912345": {
        "nombre_completo": "ANA MARIA TORRES VEGA",
        "nombres": "ANA MARIA",
        "apellido_paterno": "TORRES",
        "apellido_materno": "VEGA"
    },
    "32165498": {
        "nombre_completo": "CARLOS ALBERTO MENDOZA RUIZ",
        "nombres": "CARLOS ALBERTO",
        "apellido_paterno": "MENDOZA",
        "apellido_materno": "RUIZ"
    },
    "65498732": {
        "nombre_completo": "LAURA PATRICIA CASTRO DIAZ",
        "nombres": "LAURA PATRICIA",
        "apellido_paterno": "CASTRO",
        "apellido_materno": "DIAZ"
    },
    "98765432": {
        "nombre_completo": "JORGE LUIS NAVARRO ROMERO",
        "nombres": "JORGE LUIS",
        "apellido_paterno": "NAVARRO",
        "apellido_materno": "ROMERO"
    },
    "11223344": {
        "nombre_completo": "CARMEN ROSA SILVA PAZ",
        "nombres": "CARMEN ROSA",
        "apellido_paterno": "SILVA",
        "apellido_materno": "PAZ"
    }
}

def consultar_dni_reniec(dni):
    """Consulta datos personales por DNI en base de datos local"""
    if len(dni) != 8 or not dni.isdigit():
        return {"error": "El DNI debe tener 8 dígitos", "success": False}
    
    if dni in BASE_DATOS_PRUEBA:
        datos = BASE_DATOS_PRUEBA[dni].copy()
        datos["success"] = True
        datos["fuente"] = "Base de datos de prueba"
        return datos
    else:
        return {
            "error": f"DNI {dni} no encontrado en la base de datos",
            "success": False,
            "disponibles": list(BASE_DATOS_PRUEBA.keys())
        }

# ==============================================
# CONFIGURACIÓN DE LA EMPRESA
# ==============================================

EMPRESA = {
    "nombre": "CIVA TRANSPORTES S.A.C.",
    "ruc": "20567890123",
    "direccion": "Av. Colonial 123, Lima - Perú",
    "telefono": "(01) 555-1234",
    "email": "ventas@civa.com.pe",
    "igv": 0.18
}

PRECIOS_DESTINO = {
    "Lima": 0,
    "Huaral": 45.00,
    "Ica": 65.00,
    "Nazca": 85.00,
    "Arequipa": 120.00,
    "Trujillo": 95.00,
    "Chiclayo": 110.00
}

ARCHIVO_CORRELATIVO = "correlativo_factura.json"

def obtener_correlativo():
    """Obtiene el siguiente número de factura"""
    if os.path.exists(ARCHIVO_CORRELATIVO):
        try:
            with open(ARCHIVO_CORRELATIVO, "r") as f:
                datos = json.load(f)
                correlativo = datos.get("correlativo", 1)
                datos["correlativo"] = correlativo + 1
                with open(ARCHIVO_CORRELATIVO, "w") as f2:
                    json.dump(datos, f2)
                return correlativo
        except:
            return 1
    else:
        with open(ARCHIVO_CORRELATIVO, "w") as f:
            json.dump({"correlativo": 2}, f)
        return 1

def calcular_precio_viaje(origen, destino, tipo_servicio="Económico"):
    """Calcula el precio según origen y destino"""
    precio_base = PRECIOS_DESTINO.get(destino, 50.00)
    
    if origen != "Lima":
        precio_base = precio_base * 0.9
    
    if tipo_servicio.lower() == "premium":
        precio_base = precio_base * 1.3
    
    return precio_base

# ==============================================
# FUNCIONES DE IMPRESIÓN
# ==============================================

def imprimir_directo(contenido_texto, titulo="Impresión"):
    """Imprime directamente usando el diálogo de impresión"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(contenido_texto)
            archivo_temp = f.name
        
        if os.name == 'nt':
            subprocess.run(['notepad', '/p', archivo_temp], check=True)
        else:
            subprocess.run(['lp', archivo_temp], check=True)
        
        os.unlink(archivo_temp)
        return True, "Documento enviado a la impresora"
        
    except Exception as e:
        return False, str(e)

def imprimir_boleta(pasajero, origen="Lima", destino="", fecha_viaje=None):
    """Genera y guarda un boleto en archivo de texto"""
    if not fecha_viaje:
        fecha_viaje = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    num_boleta = f"B-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    filename = f"boleto_{pasajero.dni}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    contenido = f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                  🚌 CIVA TRANSPORTES 🚌                      ║
║              TRANSPORTE INTERPROVINCIAL                      ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  🎫 BOLETO DE VIAJE N°: {num_boleta}                            ║
║                                                              ║
║  ─── DATOS DEL PASAJERO ───                                  ║
║  👤 NOMBRE: {pasajero.nombre:<40} ║
║  📋 DNI:    {pasajero.dni:<40} ║
║  📞 TELÉFONO: {pasajero.telefono if pasajero.telefono else 'No registrado':<40} ║
║                                                              ║
║  ─── DATOS DEL VIAJE ───                                    ║
║  🚌 ORIGEN:   {origen:<40} ║
║  🏁 DESTINO:  {destino:<40} ║
║  💺 ASIENTO:  {pasajero.asiento if pasajero.asiento else 'No asignado':<40} ║
║  📅 FECHA:    {fecha_viaje:<40} ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  ✨ ¡GRACIAS POR VIAJAR CON NOSOTROS! ✨                    ║
║                                                              ║
║  📌 Presenta este boleto al abordar el bus                  ║
║  ⏰ Llegar con 30 minutos de anticipación                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(contenido)
    
    return filename, contenido

def mostrar_boleta(pasajero, origen="Lima", destino="", fecha_viaje=None):
    """Muestra el boleto en una ventana emergente con opciones de impresión"""
    from datetime import datetime
    
    if not fecha_viaje:
        fecha_viaje = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    ventana = tk.Toplevel()
    ventana.title(f"🎫 Boleto - {pasajero.nombre}")
    ventana.geometry("600x750")
    ventana.resizable(False, False)
    ventana.configure(bg="#1E293B")
    
    tk.Label(ventana, text="🎫 BOLETO DE VIAJE", 
             font=("Segoe UI", 18, "bold"), fg="#F8FAFC", bg="#1E293B").pack(pady=15)
    
    tk.Frame(ventana, bg="#2563EB", height=2, width=500).pack(pady=5)
    
    marco_boleta = tk.Frame(ventana, bg="#0F172A", relief="solid", bd=2)
    marco_boleta.pack(padx=20, pady=10, fill="both", expand=True)
    
    num_boleta = f"B-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    tk.Label(marco_boleta, text=f"N° BOLETO: {num_boleta}",
             font=("Segoe UI", 11, "bold"), fg="#60A5FA", bg="#0F172A").pack(pady=10)
    
    tk.Frame(marco_boleta, bg="#334155", height=1, width=500).pack(pady=5)
    
    tk.Label(marco_boleta, text="👤 DATOS DEL PASAJERO",
             font=("Segoe UI", 12, "bold"), fg="#FCD34D", bg="#0F172A").pack(anchor="w", padx=20, pady=5)
    
    tk.Label(marco_boleta, text=f"Nombre: {pasajero.nombre}",
             font=("Segoe UI", 11), fg="#F8FAFC", bg="#0F172A").pack(anchor="w", padx=40)
    tk.Label(marco_boleta, text=f"DNI: {pasajero.dni}",
             font=("Segoe UI", 11), fg="#F8FAFC", bg="#0F172A").pack(anchor="w", padx=40)
    tk.Label(marco_boleta, text=f"Teléfono: {pasajero.telefono if pasajero.telefono else 'No registrado'}",
             font=("Segoe UI", 11), fg="#F8FAFC", bg="#0F172A").pack(anchor="w", padx=40)
    
    tk.Frame(marco_boleta, bg="#334155", height=1, width=500).pack(pady=5)
    
    tk.Label(marco_boleta, text="🚌 DATOS DEL VIAJE",
             font=("Segoe UI", 12, "bold"), fg="#FCD34D", bg="#0F172A").pack(anchor="w", padx=20, pady=5)
    
    tk.Label(marco_boleta, text=f"Origen: {origen}",
             font=("Segoe UI", 11), fg="#F8FAFC", bg="#0F172A").pack(anchor="w", padx=40)
    tk.Label(marco_boleta, text=f"Destino: {destino}",
             font=("Segoe UI", 11), fg="#F8FAFC", bg="#0F172A").pack(anchor="w", padx=40)
    tk.Label(marco_boleta, text=f"Asiento: {pasajero.asiento if pasajero.asiento else 'No asignado'}",
             font=("Segoe UI", 11), fg="#F8FAFC", bg="#0F172A").pack(anchor="w", padx=40)
    tk.Label(marco_boleta, text=f"Fecha/Hora: {fecha_viaje}",
             font=("Segoe UI", 11), fg="#F8FAFC", bg="#0F172A").pack(anchor="w", padx=40)
    
    tk.Frame(marco_boleta, bg="#334155", height=1, width=500).pack(pady=5)
    
    tk.Label(marco_boleta, text="✨ ¡GRACIAS POR VIAJAR CON NOSOTROS! ✨",
             font=("Segoe UI", 12, "bold"), fg="#10B981", bg="#0F172A").pack(pady=10)
    tk.Label(marco_boleta, text="📌 Presenta este boleto al abordar el bus",
             font=("Segoe UI", 10), fg="#94A3B8", bg="#0F172A").pack()
    tk.Label(marco_boleta, text="⏰ Llegar con 30 minutos de anticipación",
             font=("Segoe UI", 10), fg="#94A3B8", bg="#0F172A").pack(pady=5)
    
    # ===== BOTONES DE IMPRESIÓN =====
    frame_botones = tk.Frame(ventana, bg="#1E293B")
    frame_botones.pack(pady=15)
    
    def guardar_boleta():
        filename, _ = imprimir_boleta(pasajero, origen, destino, fecha_viaje)
        messagebox.showinfo("✅ Éxito", f"Boleto guardado como:\n{filename}")
    
    def imprimir_fisico():
        filename, contenido = imprimir_boleta(pasajero, origen, destino, fecha_viaje)
        exito, mensaje = imprimir_directo(contenido)
        if exito:
            messagebox.showinfo("🖨️ Éxito", mensaje)
        else:
            messagebox.showwarning("Aviso", 
                f"No se pudo imprimir automáticamente.\n\n"
                f"El boleto se guardó como:\n{filename}\n\n"
                f"¿Deseas abrirlo para imprimirlo manualmente?")
            try:
                if os.name == 'nt':
                    os.startfile(filename)
                else:
                    subprocess.run(['xdg-open', filename])
            except:
                pass
    
    def abrir_archivo():
        filename, _ = imprimir_boleta(pasajero, origen, destino, fecha_viaje)
        try:
            if os.name == 'nt':
                os.startfile(filename)
            else:
                subprocess.run(['xdg-open', filename])
        except:
            messagebox.showinfo("Aviso", f"No se pudo abrir el archivo:\n{filename}")
    
    def cerrar():
        ventana.destroy()
    
    tk.Button(frame_botones, text="💾 Guardar", 
              command=guardar_boleta,
              bg="#2563EB", fg="white", font=("Segoe UI", 10, "bold"), 
              padx=20, pady=8).pack(side="left", padx=10)
    
    tk.Button(frame_botones, text="🖨️ Imprimir", 
              command=imprimir_fisico,
              bg="#10B981", fg="white", font=("Segoe UI", 10, "bold"), 
              padx=20, pady=8).pack(side="left", padx=10)
    
    tk.Button(frame_botones, text="📂 Abrir", 
              command=abrir_archivo,
              bg="#8B5CF6", fg="white", font=("Segoe UI", 10, "bold"), 
              padx=20, pady=8).pack(side="left", padx=10)
    
    tk.Button(frame_botones, text="❌ Cerrar", 
              command=cerrar,
              bg="#EF4444", fg="white", font=("Segoe UI", 10, "bold"), 
              padx=20, pady=8).pack(side="left", padx=10)

# ==============================================
# FUNCIONES DE FACTURACIÓN
# ==============================================

def generar_factura(pasajero, origen="Lima", destino="", asiento="", 
                    fecha_viaje=None, tipo_servicio="Económico", metodo_pago="Efectivo"):
    """Genera una factura completa para el pasajero"""
    if not fecha_viaje:
        fecha_viaje = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    num_factura = obtener_correlativo()
    factura_num = f"F001-{num_factura:08d}"
    
    precio_unitario = calcular_precio_viaje(origen, destino, tipo_servicio)
    
    subtotal = precio_unitario
    igv = subtotal * EMPRESA["igv"]
    total = subtotal + igv
    
    factura = {
        "numero": factura_num,
        "fecha_emision": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "fecha_viaje": fecha_viaje,
        "empresa": EMPRESA,
        "cliente": {
            "nombre": pasajero.nombre,
            "dni": pasajero.dni,
            "telefono": pasajero.telefono or "No registrado"
        },
        "viaje": {
            "origen": origen,
            "destino": destino,
            "asiento": asiento or pasajero.asiento or "No asignado",
            "tipo_servicio": tipo_servicio
        },
        "detalle": [
            {
                "descripcion": f"Pasaje {origen} → {destino} ({tipo_servicio})",
                "cantidad": 1,
                "precio_unitario": precio_unitario,
                "subtotal": subtotal
            }
        ],
        "subtotal": subtotal,
        "igv": igv,
        "total": total,
        "metodo_pago": metodo_pago
    }
    
    return factura

def imprimir_factura(factura):
    """Genera el archivo de texto de la factura"""
    num_factura = factura["numero"]
    filename = f"factura_{num_factura}.txt"
    
    contenido = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║                      🧾 FACTURA ELECTRÓNICA                             ║
║                                                                          ║
║  {EMPRESA['nombre']:<70} ║
║  RUC: {EMPRESA['ruc']:<65} ║
║  {EMPRESA['direccion']:<70} ║
║  Tel: {EMPRESA['telefono']:<65} ║
║  Email: {EMPRESA['email']:<65} ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  FACTURA N°: {factura['numero']:<58} ║
║  FECHA EMISIÓN: {factura['fecha_emision']:<56} ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║  ─── DATOS DEL CLIENTE ───                                              ║
║  NOMBRE: {factura['cliente']['nombre']:<62} ║
║  DNI:    {factura['cliente']['dni']:<62} ║
║  TELÉFONO: {factura['cliente']['telefono']:<60} ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║  ─── DATOS DEL VIAJE ───                                               ║
║  ORIGEN:   {factura['viaje']['origen']:<60} ║
║  DESTINO:  {factura['viaje']['destino']:<60} ║
║  ASIENTO:  {factura['viaje']['asiento']:<60} ║
║  SERVICIO: {factura['viaje']['tipo_servicio']:<60} ║
║  FECHA:    {factura['fecha_viaje']:<60} ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║  ─── DETALLE DE PAGO ───                                               ║
║                                                                          ║
║  {'DESCRIPCIÓN':<40} {'CANT':<8} {'P.UNIT':<12} {'SUBTOTAL':<12} ║
║  {'-'*40} {'-'*8} {'-'*12} {'-'*12} ║
"""
    
    for item in factura["detalle"]:
        contenido += f"""║  {item['descripcion']:<40} {str(item['cantidad']):<8} S/{item['precio_unitario']:>8.2f}  S/{item['subtotal']:>8.2f}  ║
"""
    
    contenido += f"""║                                                                          ║
║  {'SUBTOTAL':<40} {'':<8} {'':<12} S/{factura['subtotal']:>8.2f}  ║
║  {'IGV (18%)':<40} {'':<8} {'':<12} S/{factura['igv']:>8.2f}  ║
║  {'TOTAL':<40} {'':<8} {'':<12} S/{factura['total']:>8.2f}  ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  MÉTODO DE PAGO: {factura['metodo_pago']:<61} ║
║                                                                          ║
║  ✨ ¡GRACIAS POR VIAJAR CON NOSOTROS! ✨                               ║
║                                                                          ║
║  📌 Esta factura es un comprobante de pago válido                      ║
║  ⚠️  Conservar para cualquier reclamo o consulta                      ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
    """
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(contenido)
    
    return filename, contenido

def mostrar_factura(pasajero, origen="Lima", destino="", asiento="", 
                    fecha_viaje=None, servicio="Económico"):
    """Muestra la factura en una ventana emergente con opciones de impresión"""
    if not fecha_viaje:
        fecha_viaje = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    factura = generar_factura(pasajero, origen, destino, asiento, fecha_viaje, servicio)
    
    ventana = tk.Toplevel()
    ventana.title(f"🧾 Factura - {pasajero.nombre}")
    ventana.geometry("750x850")
    ventana.resizable(False, False)
    ventana.configure(bg="#1E293B")
    
    canvas = tk.Canvas(ventana, bg="#1E293B", highlightthickness=0)
    scrollbar = tk.Scrollbar(ventana, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#1E293B")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar.pack(side="right", fill="y")
    
    tk.Label(scrollable_frame, text="🧾 FACTURA ELECTRÓNICA", 
             font=("Segoe UI", 20, "bold"), fg="#F8FAFC", bg="#1E293B").pack(pady=15)
    
    tk.Frame(scrollable_frame, bg="#2563EB", height=2, width=600).pack(pady=5)
    
    marco_factura = tk.Frame(scrollable_frame, bg="#0F172A", relief="solid", bd=2)
    marco_factura.pack(padx=20, pady=10, fill="both", expand=True)
    
    tk.Label(marco_factura, text=EMPRESA["nombre"],
             font=("Segoe UI", 14, "bold"), fg="#60A5FA", bg="#0F172A").pack(pady=5)
    tk.Label(marco_factura, text=f"RUC: {EMPRESA['ruc']}",
             font=("Segoe UI", 10), fg="#94A3B8", bg="#0F172A").pack()
    tk.Label(marco_factura, text=EMPRESA["direccion"],
             font=("Segoe UI", 10), fg="#94A3B8", bg="#0F172A").pack()
    tk.Label(marco_factura, text=f"Tel: {EMPRESA['telefono']} | Email: {EMPRESA['email']}",
             font=("Segoe UI", 10), fg="#94A3B8", bg="#0F172A").pack(pady=(0, 10))
    
    tk.Frame(marco_factura, bg="#334155", height=1, width=550).pack(pady=5)
    
    tk.Label(marco_factura, text=f"N° FACTURA: {factura['numero']}",
             font=("Segoe UI", 12, "bold"), fg="#FCD34D", bg="#0F172A").pack(anchor="w", padx=20, pady=5)
    tk.Label(marco_factura, text=f"Fecha Emisión: {factura['fecha_emision']}",
             font=("Segoe UI", 10), fg="#94A3B8", bg="#0F172A").pack(anchor="w", padx=20, pady=2)
    
    tk.Frame(marco_factura, bg="#334155", height=1, width=550).pack(pady=5)
    
    tk.Label(marco_factura, text="📋 DATOS DEL CLIENTE",
             font=("Segoe UI", 12, "bold"), fg="#FCD34D", bg="#0F172A").pack(anchor="w", padx=20, pady=5)
    
    tk.Label(marco_factura, text=f"Nombre: {factura['cliente']['nombre']}",
             font=("Segoe UI", 11), fg="#F8FAFC", bg="#0F172A").pack(anchor="w", padx=40)
    tk.Label(marco_factura, text=f"DNI: {factura['cliente']['dni']}",
             font=("Segoe UI", 11), fg="#F8FAFC", bg="#0F172A").pack(anchor="w", padx=40)
    tk.Label(marco_factura, text=f"Teléfono: {factura['cliente']['telefono']}",
             font=("Segoe UI", 11), fg="#F8FAFC", bg="#0F172A").pack(anchor="w", padx=40)
    
    tk.Frame(marco_factura, bg="#334155", height=1, width=550).pack(pady=5)
    
    tk.Label(marco_factura, text="🚌 DATOS DEL VIAJE",
             font=("Segoe UI", 12, "bold"), fg="#FCD34D", bg="#0F172A").pack(anchor="w", padx=20, pady=5)
    
    tk.Label(marco_factura, text=f"Origen: {factura['viaje']['origen']}",
             font=("Segoe UI", 11), fg="#F8FAFC", bg="#0F172A").pack(anchor="w", padx=40)
    tk.Label(marco_factura, text=f"Destino: {factura['viaje']['destino']}",
             font=("Segoe UI", 11), fg="#F8FAFC", bg="#0F172A").pack(anchor="w", padx=40)
    tk.Label(marco_factura, text=f"Asiento: {factura['viaje']['asiento']}",
             font=("Segoe UI", 11), fg="#F8FAFC", bg="#0F172A").pack(anchor="w", padx=40)
    tk.Label(marco_factura, text=f"Servicio: {factura['viaje']['tipo_servicio']}",
             font=("Segoe UI", 11), fg="#F8FAFC", bg="#0F172A").pack(anchor="w", padx=40)
    tk.Label(marco_factura, text=f"Fecha Viaje: {factura['fecha_viaje']}",
             font=("Segoe UI", 11), fg="#F8FAFC", bg="#0F172A").pack(anchor="w", padx=40)
    
    tk.Frame(marco_factura, bg="#334155", height=1, width=550).pack(pady=5)
    
    tk.Label(marco_factura, text="💰 DETALLE DE PAGO",
             font=("Segoe UI", 12, "bold"), fg="#FCD34D", bg="#0F172A").pack(anchor="w", padx=20, pady=5)
    
    header_frame = tk.Frame(marco_factura, bg="#0F172A")
    header_frame.pack(fill="x", padx=40)
    
    tk.Label(header_frame, text="Descripción", font=("Segoe UI", 10, "bold"), 
             fg="#94A3B8", bg="#0F172A", width=30).grid(row=0, column=0, sticky="w")
    tk.Label(header_frame, text="Cant", font=("Segoe UI", 10, "bold"), 
             fg="#94A3B8", bg="#0F172A", width=8).grid(row=0, column=1)
    tk.Label(header_frame, text="P.Unit", font=("Segoe UI", 10, "bold"), 
             fg="#94A3B8", bg="#0F172A", width=10).grid(row=0, column=2)
    tk.Label(header_frame, text="Subtotal", font=("Segoe UI", 10, "bold"), 
             fg="#94A3B8", bg="#0F172A", width=10).grid(row=0, column=3)
    
    for item in factura["detalle"]:
        row_frame = tk.Frame(marco_factura, bg="#0F172A")
        row_frame.pack(fill="x", padx=40)
        
        tk.Label(row_frame, text=item["descripcion"], font=("Segoe UI", 10), 
                 fg="#F8FAFC", bg="#0F172A", width=30).grid(row=0, column=0, sticky="w")
        tk.Label(row_frame, text=str(item["cantidad"]), font=("Segoe UI", 10), 
                 fg="#F8FAFC", bg="#0F172A", width=8).grid(row=0, column=1)
        tk.Label(row_frame, text=f"S/{item['precio_unitario']:.2f}", font=("Segoe UI", 10), 
                 fg="#F8FAFC", bg="#0F172A", width=10).grid(row=0, column=2)
        tk.Label(row_frame, text=f"S/{item['subtotal']:.2f}", font=("Segoe UI", 10), 
                 fg="#F8FAFC", bg="#0F172A", width=10).grid(row=0, column=3)
    
    tk.Frame(marco_factura, bg="#334155", height=1, width=550).pack(pady=5)
    
    total_frame = tk.Frame(marco_factura, bg="#0F172A")
    total_frame.pack(fill="x", padx=40, pady=5)
    
    tk.Label(total_frame, text=f"SUBTOTAL:  S/{factura['subtotal']:.2f}", 
             font=("Segoe UI", 11, "bold"), fg="#F8FAFC", bg="#0F172A").pack(anchor="e")
    tk.Label(total_frame, text=f"IGV (18%):  S/{factura['igv']:.2f}", 
             font=("Segoe UI", 11, "bold"), fg="#F8FAFC", bg="#0F172A").pack(anchor="e")
    tk.Label(total_frame, text=f"TOTAL:      S/{factura['total']:.2f}", 
             font=("Segoe UI", 14, "bold"), fg="#10B981", bg="#0F172A").pack(anchor="e")
    
    tk.Frame(marco_factura, bg="#334155", height=1, width=550).pack(pady=5)
    
    tk.Label(marco_factura, text=f"MÉTODO DE PAGO: {factura['metodo_pago']}",
             font=("Segoe UI", 11), fg="#F8FAFC", bg="#0F172A").pack(pady=5)
    
    tk.Label(marco_factura, text="✨ ¡GRACIAS POR VIAJAR CON NOSOTROS! ✨",
             font=("Segoe UI", 12, "bold"), fg="#10B981", bg="#0F172A").pack(pady=10)
    
    # ============================================================
    # ===== BOTONES DE IMPRESIÓN (AGREGAR ESTA PARTE) =====
    # ============================================================
    frame_botones = tk.Frame(scrollable_frame, bg="#1E293B")
    frame_botones.pack(pady=15)
    
    def guardar_factura():
        filename, _ = imprimir_factura(factura)
        messagebox.showinfo("✅ Éxito", f"Factura guardada como:\n{filename}")
    
    def imprimir_fisico():
        filename, contenido = imprimir_factura(factura)
        exito, mensaje = imprimir_directo(contenido)
        if exito:
            messagebox.showinfo("🖨️ Éxito", mensaje)
        else:
            messagebox.showwarning("Aviso", 
                f"No se pudo imprimir automáticamente.\n\n"
                f"La factura se guardó como:\n{filename}\n\n"
                f"¿Deseas abrirla para imprimirla manualmente?")
            try:
                if os.name == 'nt':
                    os.startfile(filename)
                else:
                    subprocess.run(['xdg-open', filename])
            except:
                pass
    
    def abrir_archivo():
        filename, _ = imprimir_factura(factura)
        try:
            if os.name == 'nt':
                os.startfile(filename)
            else:
                subprocess.run(['xdg-open', filename])
        except:
            messagebox.showinfo("Aviso", f"No se pudo abrir el archivo:\n{filename}")
    
    def cerrar():
        ventana.destroy()
    
    # Botones
    tk.Button(frame_botones, text="💾 Guardar", 
              command=guardar_factura,
              bg="#2563EB", fg="white", font=("Segoe UI", 10, "bold"), 
              padx=20, pady=8).pack(side="left", padx=10)
    
    tk.Button(frame_botones, text="🖨️ Imprimir",   # <--- BOTÓN IMPRIMIR
              command=imprimir_fisico,
              bg="#10B981", fg="white", font=("Segoe UI", 10, "bold"), 
              padx=20, pady=8).pack(side="left", padx=10)
    
    tk.Button(frame_botones, text="📂 Abrir", 
              command=abrir_archivo,
              bg="#8B5CF6", fg="white", font=("Segoe UI", 10, "bold"), 
              padx=20, pady=8).pack(side="left", padx=10)
    
    tk.Button(frame_botones, text="❌ Cerrar", 
              command=cerrar,
              bg="#EF4444", fg="white", font=("Segoe UI", 10, "bold"), 
              padx=20, pady=8).pack(side="left", padx=10)

# ==============================================
# SISTEMA DE USUARIOS
# ==============================================

USUARIOS = {
    "admin@civa.com": {
        "nombre": "Administrador",
        "rol": "Administrador",
        "clave_hash": "e10adc3949ba59abbe56e057f20f883e"
    },
    "empleado@civa.com": {
        "nombre": "Empleado Civa",
        "rol": "Empleado",
        "clave_hash": "827ccb0eea8a706c4c34a16891f84e7b"
    }
}

ARCHIVO_RECORDAR = "recordar_usuario.json"

def cifrar_clave(clave):
    return hashlib.md5(clave.encode()).hexdigest()

def guardar_usuario_recordar(correo):
    with open(ARCHIVO_RECORDAR, "w") as f:
        json.dump({"correo": correo}, f)

def cargar_usuario_recordar():
    if os.path.exists(ARCHIVO_RECORDAR):
        try:
            with open(ARCHIVO_RECORDAR, "r") as f:
                datos = json.load(f)
                return datos.get("correo", "")
        except:
            return ""
    return ""

def cambiar_contraseña(ventana_padre, correo_actual):
    ventana = tk.Toplevel(ventana_padre)
    ventana.title("Cambiar Contraseña")
    ventana.geometry("400x300")
    ventana.resizable(False, False)
    ventana.transient(ventana_padre)
    ventana.grab_set()

    tk.Label(ventana, text="Cambiar Contraseña", font=("Arial", 14, "bold")).pack(pady=15)
    marco = tk.Frame(ventana)
    marco.pack(pady=10)

    tk.Label(marco, text="Contraseña actual:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
    entrada_actual = tk.Entry(marco, width=30, show="•", font=("Arial", 10))
    entrada_actual.grid(row=1, column=0, pady=5)

    tk.Label(marco, text="Nueva contraseña:", font=("Arial", 10)).grid(row=2, column=0, sticky="w", pady=5)
    entrada_nueva = tk.Entry(marco, width=30, show="•", font=("Arial", 10))
    entrada_nueva.grid(row=3, column=0, pady=5)

    tk.Label(marco, text="Repetir contraseña:", font=("Arial", 10)).grid(row=4, column=0, sticky="w", pady=5)
    entrada_repetir = tk.Entry(marco, width=30, show="•", font=("Arial", 10))
    entrada_repetir.grid(row=5, column=0, pady=5)

    def confirmar():
        actual = entrada_actual.get().strip()
        nueva = entrada_nueva.get().strip()
        repetida = entrada_repetir.get().strip()

        if USUARIOS[correo_actual]["clave_hash"] != cifrar_clave(actual):
            messagebox.showerror("Error", "Contraseña actual incorrecta")
            return
        if len(nueva) < 4:
            messagebox.showwarning("Aviso", "La contraseña debe tener al menos 4 caracteres")
            return
        if nueva != repetida:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return

        USUARIOS[correo_actual]["clave_hash"] = cifrar_clave(nueva)
        messagebox.showinfo("✅ Éxito", "Contraseña cambiada correctamente")
        ventana.destroy()

    tk.Button(ventana, text="Guardar", command=confirmar,
              font=("Arial", 10, "bold"), bg="#28a745", fg="white",
              padx=20, pady=8, relief="flat").pack(pady=15)

def mostrar_pantalla_login(al_ingresar):
    ventana_login = tk.Tk()
    ventana_login.title("Inicio de Sesión - Sistema Logístico Civa")
    ventana_login.geometry("400x420")
    ventana_login.resizable(False, False)

    ancho, alto = 400, 420
    x = (ventana_login.winfo_screenwidth() // 2) - (ancho // 2)
    y = (ventana_login.winfo_screenheight() // 2) - (alto // 2)
    ventana_login.geometry(f"{ancho}x{alto}+{x}+{y}")

    tk.Label(ventana_login, text="Sistema Logístico Civa", 
             font=("Arial", 16, "bold")).pack(pady=(40, 10))
    tk.Label(ventana_login, text="Inicia sesión para continuar", 
             font=("Arial", 10)).pack(pady=(0, 30))

    marco = tk.Frame(ventana_login)
    marco.pack(pady=10)

    tk.Label(marco, text="Correo electrónico:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
    correo_guardado = cargar_usuario_recordar()
    entrada_correo = tk.Entry(marco, width=35, font=("Arial", 11))
    entrada_correo.grid(row=1, column=0, pady=5)
    if correo_guardado:
        entrada_correo.insert(0, correo_guardado)

    tk.Label(marco, text="Contraseña:", font=("Arial", 10)).grid(row=2, column=0, sticky="w", pady=(15, 5))
    entrada_contraseña = tk.Entry(marco, width=35, show="•", font=("Arial", 11))
    entrada_contraseña.grid(row=3, column=0, pady=5)

    recordar_var = tk.BooleanVar(value=bool(correo_guardado))
    tk.Checkbutton(marco, text="Recordar mi correo", variable=recordar_var, 
                   font=("Arial", 9)).grid(row=4, column=0, sticky="w", pady=10)

    def verificar():
        correo = entrada_correo.get().strip()
        clave = entrada_contraseña.get().strip()

        if correo not in USUARIOS:
            messagebox.showerror("Error", "Correo o contraseña incorrectos")
            return

        if USUARIOS[correo]["clave_hash"] == cifrar_clave(clave):
            ventana_login.destroy()
            if recordar_var.get():
                guardar_usuario_recordar(correo)
            elif os.path.exists(ARCHIVO_RECORDAR):
                os.remove(ARCHIVO_RECORDAR)

            nombre = USUARIOS[correo]["nombre"]
            rol = USUARIOS[correo]["rol"]
            respuesta = messagebox.askyesno("✅ Bienvenido", 
                f"¡Hola {nombre}!\nRol: {rol}\n\n¿Deseas cambiar tu contraseña ahora?")

            if respuesta:
                def continuar():
                    cambiar_contraseña(None, correo)
                    al_ingresar()
                ventana_login.after(100, continuar)
            else:
                al_ingresar()
        else:
            messagebox.showerror("Error", "Correo o contraseña incorrectos")

    tk.Button(ventana_login, text="Iniciar Sesión", command=verificar,
              font=("Arial", 11, "bold"), bg="#0056b3", fg="white",
              padx=30, pady=10, relief="flat").pack(pady=20)

    ventana_login.mainloop()

# ==============================================
# IMPORTACIONES DE MÓDULOS
# ==============================================

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:
    from estructuras.cola import Cola
    from modelos.chofer import Chofer
    from modelos.bus import Bus
    from modelos.ruta import Ruta
    from modelos.asiento import Asiento
    from algoritmos.asignacion_choferes import asignar_chofer, enviar_a_descanso, liberar_de_descanso
    from algoritmos.asignacion_buses import registrar_bus, asignar_bus
    from algoritmos.dijkstra import calcular_ruta_mas_corta
    print("✅ Módulos importados correctamente")
except Exception as e:
    print(f"⚠️ Error al importar módulos: {e}")
    Cola = None
    Chofer = Bus = Ruta = Asiento = None
    asignar_chofer = enviar_a_descanso = liberar_de_descanso = None
    registrar_bus = asignar_bus = calcular_ruta_mas_corta = None

# ==============================================
# CLASE PASAJERO
# ==============================================

class Pasajero:
    def __init__(self, dni, nombre, telefono="", destino="", asiento=0, fecha_registro=None):
        self.dni = dni
        self.nombre = nombre
        self.telefono = telefono
        self.destino = destino
        self.asiento = asiento
        self.fecha_registro = fecha_registro or datetime.now().strftime("%d/%m/%Y %H:%M")

    def __str__(self):
        return f"DNI: {self.dni} | {self.nombre} | Asiento: {self.asiento}"

# ==============================================
# SISTEMA PRINCIPAL
# ==============================================

class SistemaLogisticoCiva:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema Logístico Civa - Transporte Interprovincial")
        self.root.geometry("1050x800")
        self.root.resizable(True, True)

        self.color_fondo = "#0F172A"
        self.color_pestaña = "#1E293B"
        self.color_destacado = "#2563EB"
        self.color_texto = "#F8FAFC"
        self.color_borde = "#334155"
        self.color_exito = "#10B981"
        self.color_advertencia = "#F59E0B"
        self.color_peligro = "#EF4444"
        self.color_info = "#3B82F6"
        self.root.configure(bg=self.color_fondo)

        if Cola:
            self.cola_choferes_disponibles = Cola()
            self.cola_choferes_descanso = Cola()
            self.cola_buses = Cola()
        self.asientos = []
        self.historial = []
        self.pasajeros = []
        self.botones_asientos = {}
        self.caja_mensajes = None
        self.marco_lista_pasajeros = None
        self.pasajero_seleccionado = None
        self.entrada_dni = None
        self.entrada_nombre = None
        self.entrada_telefono = None
        self.entrada_asiento = None
        self.var_destino = None

        self.ciudades = ["Lima", "Huaral", "Ica", "Nazca", "Arequipa", "Trujillo", "Chiclayo"]

        self.grafo_rutas = {
            "Lima": [("Huaral", 120), ("Ica", 306), ("Trujillo", 555)],
            "Huaral": [("Lima", 120)],
            "Ica": [("Lima", 306), ("Nazca", 210)],
            "Nazca": [("Ica", 210), ("Arequipa", 450)],
            "Trujillo": [("Lima", 555), ("Chiclayo", 208)],
            "Chiclayo": [("Trujillo", 208)],
            "Arequipa": [("Nazca", 450)]
        }

        marco_titulo = tk.Frame(self.root, bg=self.color_destacado, height=80)
        marco_titulo.pack(fill="x")
        marco_titulo.pack_propagate(False)

        tk.Label(marco_titulo, text="🏢 SISTEMA LOGÍSTICO CIVA",
                 font=("Segoe UI", 22, "bold"),
                 bg=self.color_destacado, fg="white").pack(pady=(15, 2))
        tk.Label(marco_titulo, text="Gestión Integral de Transporte Interprovincial",
                 font=("Segoe UI", 10, "italic"),
                 bg=self.color_destacado, fg="#BFDBFE").pack()

        self.crear_pestañas()
        self.area_principal = tk.Frame(self.root, bg=self.color_pestaña, width=980, height=540)
        self.area_principal.pack(pady=15)
        self.area_principal.pack_propagate(False)

        self.cargar_pantalla_inicio()
        self.cargar_datos_prueba()

    def crear_pestañas(self):
        frame_tabs = tk.Frame(self.root, bg=self.color_fondo)
        frame_tabs.pack(pady=(0, 5))
        pestañas = [
            ("🏠 Inicio", self.cargar_pantalla_inicio),
            ("🗺️ Rutas", self.cargar_pantalla_rutas),
            ("🚌 Buses", self.cargar_pantalla_buses),
            ("👨‍✈️ Choferes", self.cargar_pantalla_choferes),
            ("💺 Asientos", self.cargar_pantalla_asientos),
            ("👤 Pasajeros", self.cargar_pantalla_pasajeros),
            ("📊 Reportes", self.cargar_pantalla_reportes),
            ("📜 Historial", self.cargar_pantalla_historial)
        ]
        for i, (nombre, funcion) in enumerate(pestañas):
            btn = tk.Button(frame_tabs, text=nombre, font=("Segoe UI", 10, "bold"),
                            bg=self.color_pestaña, fg=self.color_texto,
                            padx=18, pady=8, relief="flat", cursor="hand2",
                            activebackground=self.color_destacado,
                            command=lambda f=funcion: f())
            btn.grid(row=0, column=i, padx=3)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.color_destacado))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.color_pestaña))

    def limpiar_area_principal(self):
        for widget in self.area_principal.winfo_children():
            widget.destroy()

    def cargar_pantalla_inicio(self):
        self.limpiar_area_principal()
        self.area_principal.config(bg="#0F172A")
        
        frame_central = tk.Frame(self.area_principal, bg="#0F172A")
        frame_central.pack(expand=True, fill="both")
        
        tk.Label(frame_central, text="SISTEMA LOGÍSTICO CIVA",
                 font=("Segoe UI", 36, "bold"), 
                 fg="#F8FAFC", 
                 bg="#0F172A").pack(pady=(80, 10))
        
        tk.Label(frame_central, text="Gestión Integral de Transporte Interprovincial",
                 font=("Segoe UI", 16), 
                 fg="#94A3B8", 
                 bg="#0F172A").pack(pady=(0, 30))
        
        tk.Frame(frame_central, bg="#2563EB", height=3, width=400).pack(pady=20)
        
        tk.Label(frame_central, 
                 text="🏢 Sistema diseñado para la gestión eficiente de:\n\n"
                      "• 🗺️ Rutas y distancias entre ciudades\n"
                      "• 🚌 Flota de buses y asignaciones\n"
                      "• 👨‍✈️ Gestión de choferes\n"
                      "• 💺 Control de asientos\n"
                      "• 👤 Registro de pasajeros\n"
                      "• 📊 Reportes y estadísticas\n\n"
                      "🔹 Selecciona una opción en la barra de navegación para comenzar",
                 font=("Segoe UI", 12),
                 fg="#CBD5E1",
                 bg="#0F172A",
                 justify="center").pack(pady=10)
        
        tk.Label(frame_central, 
                 text="v2.1 | Civa Transportes Interprovinciales",
                 font=("Segoe UI", 9),
                 fg="#64748B",
                 bg="#0F172A").pack(side="bottom", pady=20)

    def cargar_pantalla_rutas(self):
        self.limpiar_area_principal()
        tk.Label(self.area_principal, text="🗺️ CÁLCULO DE RUTA MÁS CORTA",
                 font=("Arial", 20, "bold"), fg="white", bg=self.color_pestaña).pack(pady=20)

        frame = tk.Frame(self.area_principal, bg=self.color_pestaña)
        frame.pack(pady=10)

        tk.Label(frame, text="Origen:", fg="white", bg=self.color_pestaña, font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=10)
        origen_var = tk.StringVar()
        origen_var.set("Lima")
        origen_combo = ttk.Combobox(frame, textvariable=origen_var, values=self.ciudades, state="readonly", font=("Arial", 12))
        origen_combo.grid(row=0, column=1, padx=5, pady=10)

        tk.Label(frame, text="Destino:", fg="white", bg=self.color_pestaña, font=("Arial", 12)).grid(row=0, column=2, padx=5, pady=10)
        destino_var = tk.StringVar()
        destino_var.set("Arequipa")
        destino_combo = ttk.Combobox(frame, textvariable=destino_var, values=self.ciudades, state="readonly", font=("Arial", 12))
        destino_combo.grid(row=0, column=3, padx=5, pady=10)

        resultado = tk.Label(self.area_principal, text="", font=("Arial", 14), fg="white", bg=self.color_pestaña)
        resultado.pack(pady=20)

        def calcular():
            if not calcular_ruta_mas_corta:
                messagebox.showinfo("Aviso", "Módulo de rutas no disponible")
                return
            o = origen_var.get()
            d = destino_var.get()
            ruta, dist = calcular_ruta_mas_corta(self.grafo_rutas, o, d)
            if ruta:
                resultado.config(text=f"Ruta: {' → '.join(ruta)}\nDistancia: {dist} km", fg="#00ff88")
                self.historial.append(f"🗺️ Ruta calculada: {o} → {d} | {dist} km")
            else:
                resultado.config(text="❌ No se encontró ruta", fg="#ff6666")
                self.historial.append(f"❌ Intento de ruta: {o} → {d} (sin éxito)")

        tk.Button(self.area_principal, text="Calcular Ruta", command=calcular,
                  bg="#2ecc71", fg="white", font=("Arial", 12, "bold"), padx=20, pady=8).pack(pady=10)

    def cargar_pantalla_buses(self):
        self.limpiar_area_principal()
        tk.Label(self.area_principal, text="🚌 GESTIÓN DE BUSES",
                 font=("Arial", 20, "bold"), fg="white", bg=self.color_pestaña).pack(pady=20)
        frame = tk.Frame(self.area_principal, bg=self.color_pestaña)
        frame.pack(pady=10)
        tk.Label(frame, text="Código:", fg="white", bg=self.color_pestaña).grid(row=0, column=0, padx=5, pady=5)
        cod_entry = tk.Entry(frame)
        cod_entry.insert(0, "BUS006")
        cod_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(frame, text="Placa:", fg="white", bg=self.color_pestaña).grid(row=0, column=2, padx=5, pady=5)
        placa_entry = tk.Entry(frame)
        placa_entry.insert(0, "XYZ-789")
        placa_entry.grid(row=0, column=3, padx=5, pady=5)
        tk.Label(frame, text="Capacidad:", fg="white", bg=self.color_pestaña).grid(row=1, column=0, padx=5, pady=5)
        cap_entry = tk.Entry(frame)
        cap_entry.insert(0, "45")
        cap_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(frame, text="Servicio:", fg="white", bg=self.color_pestaña).grid(row=1, column=2, padx=5, pady=5)
        servicio_var = tk.StringVar()
        servicio_var.set("economico")
        servicio_combo = ttk.Combobox(frame, textvariable=servicio_var, values=["economico", "premium"], state="readonly")
        servicio_combo.grid(row=1, column=3, padx=5, pady=5)
        lista = tk.Text(self.area_principal, width=80, height=10, font=("Arial", 10))
        lista.pack(pady=10)

        def actualizar_lista():
            lista.delete("1.0", tk.END)
            if not Cola or not self.cola_buses:
                lista.insert(tk.END, "⚠️ Archivos de buses no disponibles\n")
                return
            lista.insert(tk.END, "=== Buses Registrados ===\n")
            temp = Cola()
            while not self.cola_buses.esta_vacia():
                bus = self.cola_buses.desencolar()
                lista.insert(tk.END, f"{bus.codigo} | {bus.placa} | {bus.tipo_servicio} | {bus.estado}\n")
                temp.encolar(bus)
            while not temp.esta_vacia():
                self.cola_buses.encolar(temp.desencolar())

        def registrar():
            if not Bus or not registrar_bus:
                messagebox.showinfo("Aviso", "Módulo de buses no disponible")
                return
            bus = Bus(cod_entry.get(), placa_entry.get(), int(cap_entry.get()), servicio_var.get())
            registrar_bus(self.cola_buses, bus)
            self.historial.append(f"✅ Bus registrado: {bus.codigo} | Placa: {bus.placa}")
            messagebox.showinfo("✅", f"Bus {bus.codigo} registrado")
            actualizar_lista()

        def asignar():
            if not asignar_bus:
                messagebox.showinfo("Aviso", "Módulo de buses no disponible")
                return
            bus = asignar_bus(self.cola_buses, servicio_var.get())
            if bus:
                self.historial.append(f"🚌 Bus asignado: {bus.codigo} para servicio {bus.tipo_servicio}")
                messagebox.showinfo("✅", f"Asignado: {bus.codigo}")
            else:
                self.historial.append(f"⚠️ Intento asignar bus: sin disponibilidad")
                messagebox.showinfo("Aviso", "No hay buses disponibles")
            actualizar_lista()

        tk.Button(frame, text="Registrar Bus", command=registrar, bg="#3498db", fg="white", padx=10, pady=5).grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(frame, text="Asignar Bus", command=asignar, bg="#f39c12", fg="white", padx=10, pady=5).grid(row=2, column=2, columnspan=2, pady=10)
        actualizar_lista()

    def cargar_pantalla_choferes(self):
        self.limpiar_area_principal()
        tk.Label(self.area_principal, text="👨‍✈️ GESTIÓN DE CHOFERES",
                 font=("Arial", 20, "bold"), fg="white", bg=self.color_pestaña).pack(pady=20)
        frame = tk.Frame(self.area_principal, bg=self.color_pestaña)
        frame.pack(pady=10)
        tk.Label(frame, text="DNI:", fg="white", bg=self.color_pestaña).grid(row=0, column=0, padx=5, pady=5)
        dni_entry = tk.Entry(frame)
        dni_entry.insert(0, "72345678")
        dni_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(frame, text="Nombre:", fg="white", bg=self.color_pestaña).grid(row=0, column=2, padx=5, pady=5)
        nom_entry = tk.Entry(frame)
        nom_entry.insert(0, "Carlos Perez")
        nom_entry.grid(row=0, column=3, padx=5, pady=5)
        tk.Label(frame, text="Licencia:", fg="white", bg=self.color_pestaña).grid(row=1, column=0, padx=5, pady=5)
        licencia_var = tk.StringVar()
        licencia_var.set("A1")
        licencia_combo = ttk.Combobox(frame, textvariable=licencia_var, values=["A1", "A2", "B1", "B2"], state="readonly")
        licencia_combo.grid(row=1, column=1, padx=5, pady=5)
        ultimo = [None]
        resultado = tk.Label(self.area_principal, text="", font=("Arial", 12), fg="white", bg=self.color_pestaña)
        resultado.pack(pady=15)

        def registrar():
            if not Chofer:
                messagebox.showinfo("Aviso", "Módulo de choferes no disponible")
                return
            chofer = Chofer(dni_entry.get(), nom_entry.get(), licencia_var.get())
            self.cola_choferes_disponibles.encolar(chofer)
            self.historial.append(f"✅ Chofer registrado: {chofer.nombre} | DNI: {chofer.dni}")
            messagebox.showinfo("✅", f"Chofer {chofer.nombre} registrado")

        def asignar():
            if not asignar_chofer:
                messagebox.showinfo("Aviso", "Módulo de choferes no disponible")
                return
            ultimo[0] = asignar_chofer(self.cola_choferes_disponibles)
            if ultimo[0]:
                resultado.config(text=f"✅ Asignado: {ultimo[0].nombre} | Estado: {ultimo[0].estado}")
                self.historial.append(f"✅ Chofer asignado: {ultimo[0].nombre}")
            else:
                resultado.config(text="❌ No hay choferes disponibles")
                self.historial.append("⚠️ Intento asignar chofer: sin disponibilidad")

        def descansar():
            if not enviar_a_descanso:
                return
            if ultimo[0]:
                enviar_a_descanso(ultimo[0], self.cola_choferes_descanso)
                self.historial.append(f"🛌 Chofer en descanso: {ultimo[0].nombre}")
                resultado.config(text=f"🛌 {ultimo[0].nombre} enviado a descanso")
                ultimo[0] = None

        def liberar():
            if not liberar_de_descanso:
                messagebox.showinfo("Aviso", "Módulo de choferes no disponible")
                return
            c = liberar_de_descanso(self.cola_choferes_descanso, self.cola_choferes_disponibles)
            if c:
                resultado.config(text=f"🔄 {c.nombre} vuelve disponible")
                self.historial.append(f"🔄 Chofer liberado: {c.nombre}")
            else:
                resultado.config(text="❌ Nadie en descanso")
                self.historial.append("⚠️ Intento liberar chofer: nadie en descanso")

        tk.Button(frame, text="Registrar", command=registrar, bg="#2ecc71", fg="white", padx=10).grid(row=2, column=0, pady=10)
        tk.Button(frame, text="Asignar", command=asignar, bg="#3498db", fg="white", padx=10).grid(row=2, column=1, pady=10)
        tk.Button(frame, text="Enviar a Descanso", command=descansar, bg="#9b59b6", fg="white", padx=10).grid(row=2, column=2, pady=10)
        tk.Button(frame, text="Liberar", command=liberar, bg="#e67e22", fg="white", padx=10).grid(row=2, column=3, pady=10)

    def cargar_pantalla_asientos(self):
        self.limpiar_area_principal()
        tk.Label(self.area_principal, text="💺 GESTIÓN DE ASIENTOS",
                 font=("Arial", 20, "bold"), fg="white", bg=self.color_pestaña).pack(pady=10)
        if not self.asientos and Asiento:
            self.asientos = [Asiento(i+1, 35) for i in range(40)]
        frame_controles = tk.Frame(self.area_principal, bg=self.color_pestaña)
        frame_controles.pack(pady=5)
        tk.Label(frame_controles, text="Número de asiento:", fg="white", bg=self.color_pestaña).grid(row=0, column=0, padx=5, pady=5)
        num_entry = tk.Entry(frame_controles, width=5)
        num_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(frame_controles, text="Reservar", bg="#3498db", fg="white", padx=10,
                  command=lambda: self.reservar_asiento(num_entry)).grid(row=0, column=2, padx=3)
        tk.Button(frame_controles, text="Marcar Ocupado", bg="#e74c3c", fg="white", padx=10,
                  command=lambda: self.ocupar_asiento(num_entry)).grid(row=0, column=3, padx=3)
        tk.Button(frame_controles, text="Liberar", bg="#2ecc71", fg="white", padx=10,
                  command=lambda: self.liberar_asiento(num_entry)).grid(row=0, column=4, padx=3)
        panel = tk.Frame(self.area_principal, bg=self.color_pestaña)
        panel.pack(pady=10, fill="both", expand=True)
        frame_asientos = tk.Frame(panel, bg=self.color_pestaña)
        frame_asientos.pack(side="top", padx=10, pady=15)
        tk.Label(frame_asientos, text="Estado de asientos:", fg="white", bg=self.color_pestaña,
                 font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=5, pady=5)
        self.botones_asientos = {}
        fila = 1
        columna = 0
        for asiento in self.asientos:
            color = "#2ecc71" if asiento.estado == "libre" else "#e74c3c"
            texto = f"{asiento.numero:02d}"
            btn = tk.Button(frame_asientos, text=texto, width=4, height=2,
                            bg=color, fg="white", font=("Arial", 9, "bold"),
                            command=lambda n=asiento.numero: self.seleccionar_asiento(n, num_entry))
            btn.grid(row=fila, column=columna, padx=2, pady=1)
            self.botones_asientos[asiento.numero] = btn
            columna += 1
            if columna >= 5:
                columna = 0
                fila += 1
        frame_info = tk.Frame(panel, bg=self.color_pestaña, width=300)
        frame_info.pack(side="right", padx=10, fill="y")
        tk.Label(frame_info, text="Mensajes:", fg="white", bg=self.color_pestaña,
                 font=("Arial", 11, "bold")).pack(anchor="w", pady=5)
        self.caja_mensajes = tk.Text(frame_info, width=35, height=18, bg="#0a1929", fg="white", font=("Arial", 9))
        self.caja_mensajes.pack()
        self.actualizar_resumen()

    def seleccionar_asiento(self, numero, entry_widget):
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, str(numero))
        self.caja_mensajes.insert(tk.END, f"👉 Seleccionado asiento {numero}\n")
        self.caja_mensajes.see(tk.END)

    def reservar_asiento(self, entry_widget):
        numero = entry_widget.get().strip()
        if not numero.isdigit():
            self.caja_mensajes.insert(tk.END, "⚠️ Escribe un número válido\n")
            return
        n = int(numero)
        if 1 <= n <= len(self.asientos):
            if self.asientos[n-1].reservar():
                self.historial.append(f"💺 Asiento {n} reservado")
                self.caja_mensajes.insert(tk.END, f"✅ Asiento {n} → reservado\n")
            else:
                self.caja_mensajes.insert(tk.END, f"⚠️ Asiento {n} ya está ocupado\n")
            self.actualizar_boton(n)
            self.actualizar_resumen()
        else:
            self.caja_mensajes.insert(tk.END, f"❌ Asiento {n} no existe\n")
        self.caja_mensajes.see(tk.END)

    def ocupar_asiento(self, entry_widget):
        numero = entry_widget.get().strip()
        if not numero.isdigit():
            self.caja_mensajes.insert(tk.END, "⚠️ Escribe un número válido\n")
            return
        n = int(numero)
        if 1 <= n <= len(self.asientos):
            self.asientos[n-1].estado = "ocupado"
            self.historial.append(f"🔴 Asiento {n} → ocupado")
            self.caja_mensajes.insert(tk.END, f"🔴 Asiento {n} marcado como ocupado\n")
            self.actualizar_boton(n)
            self.actualizar_resumen()
        else:
            self.caja_mensajes.insert(tk.END, f"❌ Asiento {n} no existe\n")
        self.caja_mensajes.see(tk.END)

    def liberar_asiento(self, entry_widget):
        numero = entry_widget.get().strip()
        if not numero.isdigit():
            self.caja_mensajes.insert(tk.END, "⚠️ Escribe un número válido\n")
            return
        n = int(numero)
        if 1 <= n <= len(self.asientos):
            self.asientos[n-1].estado = "libre"
            self.historial.append(f"🟢 Asiento {n} → liberado")
            self.caja_mensajes.insert(tk.END, f"🟢 Asiento {n} liberado\n")
            self.actualizar_boton(n)
            self.actualizar_resumen()
        else:
            self.caja_mensajes.insert(tk.END, f"❌ Asiento {n} no existe\n")
        self.caja_mensajes.see(tk.END)

    def actualizar_boton(self, numero):
        btn = self.botones_asientos.get(numero)
        if btn:
            estado = self.asientos[numero-1].estado
            color = "#2ecc71" if estado == "libre" else "#e74c3c"
            btn.config(bg=color)

    def actualizar_resumen(self):
        if self.caja_mensajes:
            total = len(self.asientos)
            libres = sum(1 for a in self.asientos if a.estado == "libre")
            ocupados = total - libres
            self.caja_mensajes.insert(tk.END, f"\n--- Resumen: BUS001 ---\n")
            self.caja_mensajes.insert(tk.END, f"Total asientos: {total}\n")
            self.caja_mensajes.insert(tk.END, f"Disponibles:   {libres}\n")
            self.caja_mensajes.insert(tk.END, f"Ocupados:     {ocupados}\n")
            self.caja_mensajes.see(tk.END)

    # ==============================================
    # PANTALLA DE PASAJEROS
    # ==============================================
    def cargar_pantalla_pasajeros(self):
        self.limpiar_area_principal()
        
        tk.Label(self.area_principal, text="👤 REGISTRO DE PASAJEROS",
                 font=("Segoe UI", 22, "bold"), fg="white", bg=self.color_pestaña).pack(pady=15)
        
        tk.Label(self.area_principal, text="📌 Haz clic en un pasajero de la lista para seleccionarlo",
                 font=("Segoe UI", 10), fg="#FCD34D", bg=self.color_pestaña).pack()
        
        marco = tk.Frame(self.area_principal, bg=self.color_pestaña)
        marco.pack(pady=10)
        
        # DNI
        tk.Label(marco, text="DNI:", font=("Segoe UI", 11, "bold"),
                 fg="white", bg=self.color_pestaña).grid(row=0, column=0, padx=5, pady=8, sticky="e")
        
        entrada_dni = tk.Entry(marco, width=12, font=("Segoe UI", 12))
        entrada_dni.grid(row=0, column=1, padx=5, pady=8)
        self.entrada_dni = entrada_dni
        
        estado_label = tk.Label(marco, text="", fg="#FCD34D", bg=self.color_pestaña, font=("Segoe UI", 9))
        estado_label.grid(row=0, column=3, padx=8, pady=8)
        
        dnis_disponibles = ", ".join(list(BASE_DATOS_PRUEBA.keys())[:3]) + ", ..."
        tk.Label(marco, text=f"DNIs: {dnis_disponibles}", 
                 font=("Segoe UI", 8), fg="#94A3B8", bg=self.color_pestaña).grid(row=0, column=4, padx=5, pady=8)
        
        def limpiar_seleccion():
            self.pasajero_seleccionado = None
            entrada_nombre.config(bg="white")
        
        entrada_dni.bind('<KeyRelease>', lambda e: limpiar_seleccion())
        
        def buscar_datos():
            dni = entrada_dni.get().strip()
            
            if len(dni) != 8:
                messagebox.showwarning("Aviso", "El DNI debe tener 8 dígitos")
                entrada_dni.focus()
                return
            
            if not dni.isdigit():
                messagebox.showwarning("Aviso", "El DNI solo debe contener números")
                entrada_dni.focus()
                return
            
            # Buscar en pasajeros registrados
            for p in self.pasajeros:
                if p.dni == dni:
                    entrada_nombre.delete(0, tk.END)
                    entrada_nombre.insert(0, p.nombre)
                    entrada_telefono.delete(0, tk.END)
                    entrada_telefono.insert(0, p.telefono)
                    var_destino.set(p.destino)
                    entrada_asiento.delete(0, tk.END)
                    entrada_asiento.insert(0, p.asiento)
                    entrada_nombre.config(bg="#FDE68A")
                    self.pasajero_seleccionado = p
                    messagebox.showinfo("✅ Encontrado", f"Pasajero ya registrado:\n{p.nombre}\n\nYa puedes imprimir su boleto o factura.")
                    return
            
            # Buscar en base de datos
            estado_label.config(text="⏳ Buscando...")
            estado_label.update()
            
            datos = consultar_dni_reniec(dni)
            estado_label.config(text="")
            
            if datos.get("error"):
                disponibles = datos.get("disponibles", [])
                msg = f"{datos['error']}\n\nDNIs disponibles:\n" + "\n".join(disponibles[:5])
                if len(disponibles) > 5:
                    msg += f"\n... y {len(disponibles)-5} más"
                if messagebox.askyesno("DNI no encontrado", 
                    f"{msg}\n\n¿Deseas ingresar los datos manualmente?"):
                    entrada_nombre.focus()
                return
            
            nombre_completo = datos.get("nombre_completo", "")
            if nombre_completo:
                entrada_nombre.delete(0, tk.END)
                entrada_nombre.insert(0, nombre_completo)
                entrada_nombre.config(bg="#F0FDF4")
                messagebox.showinfo("✅ Éxito", f"Datos encontrados:\n{nombre_completo}")
        
        tk.Button(marco, text="🔍 Buscar", bg="#2563EB", fg="white",
                  font=("Segoe UI", 10, "bold"), padx=10, command=buscar_datos).grid(row=0, column=2, padx=8, pady=8)
        
        def mostrar_dnis():
            dnis = "\n".join([f"• {dni}: {datos['nombre_completo']}" for dni, datos in BASE_DATOS_PRUEBA.items()])
            messagebox.showinfo("DNIs disponibles", 
                f"DNIs en la base de datos:\n\n{dnis}\n\n"
                f"Total: {len(BASE_DATOS_PRUEBA)} DNIs")
        
        tk.Button(marco, text="📋 Ver todos", bg="#8B5CF6", fg="white",
                  font=("Segoe UI", 9), padx=8, command=mostrar_dnis).grid(row=0, column=5, padx=5, pady=8)
        
        # Nombre
        tk.Label(marco, text="Nombre Completo:", font=("Segoe UI", 11, "bold"),
                 fg="white", bg=self.color_pestaña).grid(row=1, column=0, padx=5, pady=8, sticky="e")
        
        entrada_nombre = tk.Entry(marco, width=35, font=("Segoe UI", 12))
        entrada_nombre.grid(row=1, column=1, columnspan=3, padx=5, pady=8)
        self.entrada_nombre = entrada_nombre
        
        # Teléfono
        tk.Label(marco, text="Teléfono:", font=("Segoe UI", 11, "bold"),
                 fg="white", bg=self.color_pestaña).grid(row=2, column=0, padx=5, pady=8, sticky="e")
        
        entrada_telefono = tk.Entry(marco, width=15, font=("Segoe UI", 12))
        entrada_telefono.grid(row=2, column=1, padx=5, pady=8)
        self.entrada_telefono = entrada_telefono
        
        # Destino
        tk.Label(marco, text="Destino:", font=("Segoe UI", 11, "bold"),
                 fg="white", bg=self.color_pestaña).grid(row=2, column=2, padx=5, pady=8, sticky="e")
        
        var_destino = tk.StringVar()
        var_destino.set("Lima")
        menu_destino = tk.OptionMenu(marco, var_destino, *self.ciudades)
        menu_destino.config(width=15, font=("Segoe UI", 10))
        menu_destino.grid(row=2, column=3, padx=5, pady=8)
        self.var_destino = var_destino
        
        # Asiento
        tk.Label(marco, text="N° Asiento:", font=("Segoe UI", 11, "bold"),
                 fg="white", bg=self.color_pestaña).grid(row=3, column=0, padx=5, pady=8, sticky="e")
        
        entrada_asiento = tk.Entry(marco, width=12, font=("Segoe UI", 12))
        entrada_asiento.grid(row=3, column=1, padx=5, pady=8)
        self.entrada_asiento = entrada_asiento
        
        marco_botones = tk.Frame(self.area_principal, bg=self.color_pestaña)
        marco_botones.pack(pady=15)
        
        def registrar():
            dni = entrada_dni.get().strip()
            nombre = entrada_nombre.get().strip()
            telefono = entrada_telefono.get().strip()
            destino = var_destino.get()
            asiento = entrada_asiento.get().strip()
            
            if not dni or not nombre:
                messagebox.showwarning("Aviso", "DNI y Nombre son obligatorios")
                return
            
            if len(dni) != 8:
                messagebox.showwarning("Aviso", "El DNI debe tener 8 dígitos")
                return
            
            # Verificar duplicado
            for p in self.pasajeros:
                if p.dni == dni:
                    messagebox.showwarning("Aviso", "Ese DNI ya está registrado")
                    self.pasajero_seleccionado = p
                    entrada_nombre.config(bg="#FDE68A")
                    return
            
            pasajero = Pasajero(dni, nombre, telefono, destino, asiento)
            self.pasajeros.append(pasajero)
            self.pasajero_seleccionado = pasajero
            self.actualizar_lista_pasajeros()
            self.historial.append(f"✅ Pasajero registrado: {dni} - {nombre}")
            
            entrada_nombre.config(bg="#FDE68A")
            
            messagebox.showinfo("✅ Éxito", 
                f"Pasajero registrado correctamente\n\n"
                f"Nombre: {nombre}\n"
                f"DNI: {dni}\n\n"
                f"Ahora puedes imprimir su boleto o factura.")
        
        tk.Button(marco_botones, text="✅ Registrar", bg="#10B981", fg="white",
                  font=("Segoe UI", 11, "bold"), padx=20, pady=8, command=registrar).grid(row=0, column=0, padx=10)
        
        def seleccionar_pasajero_click(dni):
            """Carga los datos del pasajero seleccionado al hacer clic"""
            for p in self.pasajeros:
                if p.dni == dni:
                    entrada_dni.delete(0, tk.END)
                    entrada_dni.insert(0, p.dni)
                    entrada_nombre.delete(0, tk.END)
                    entrada_nombre.insert(0, p.nombre)
                    entrada_telefono.delete(0, tk.END)
                    entrada_telefono.insert(0, p.telefono)
                    var_destino.set(p.destino)
                    entrada_asiento.delete(0, tk.END)
                    entrada_asiento.insert(0, p.asiento)
                    entrada_nombre.config(bg="#FDE68A")
                    self.pasajero_seleccionado = p
                    messagebox.showinfo("✅ Seleccionado", 
                        f"Pasajero cargado:\n{p.nombre}\n\nYa puedes imprimir su boleto o factura.")
                    break
        
        # ===== BOTÓN BOLETO =====
        def imprimir_boleta_pasajero():
            pasajero_actual = self.pasajero_seleccionado
            
            if not pasajero_actual:
                dni = entrada_dni.get().strip()
                if len(dni) != 8:
                    messagebox.showwarning("Aviso", "Primero busca o registra un pasajero, o selecciona uno de la lista")
                    return
                
                for p in self.pasajeros:
                    if p.dni == dni:
                        pasajero_actual = p
                        self.pasajero_seleccionado = p
                        break
            
            if not pasajero_actual:
                messagebox.showwarning("Aviso", "No hay pasajero seleccionado.\n\nBusca un DNI, registra un pasajero, o haz clic en uno de la lista.")
                return
            
            destino = var_destino.get()
            mostrar_boleta(pasajero_actual, "Lima", destino)
        
        tk.Button(marco_botones, text="🎫 Boleto", command=imprimir_boleta_pasajero,
                  bg="#8B5CF6", fg="white", font=("Segoe UI", 11, "bold"), 
                  padx=20, pady=8).grid(row=0, column=3, padx=10)
        
        # ===== BOTÓN FACTURA =====
        def generar_factura_pasajero():
            pasajero_actual = self.pasajero_seleccionado
            
            if not pasajero_actual:
                dni = entrada_dni.get().strip()
                if len(dni) != 8:
                    messagebox.showwarning("Aviso", "Primero busca o registra un pasajero, o selecciona uno de la lista")
                    return
                
                for p in self.pasajeros:
                    if p.dni == dni:
                        pasajero_actual = p
                        self.pasajero_seleccionado = p
                        break
            
            if not pasajero_actual:
                messagebox.showwarning("Aviso", "No hay pasajero seleccionado.\n\nBusca un DNI, registra un pasajero, o haz clic en uno de la lista.")
                return
            
            destino = var_destino.get()
            asiento = entrada_asiento.get().strip() or pasajero_actual.asiento
            
            servicio_var = tk.StringVar(value="Económico")
            servicio_window = tk.Toplevel(self.root)
            servicio_window.title("Tipo de Servicio")
            servicio_window.geometry("300x220")
            servicio_window.transient(self.root)
            servicio_window.grab_set()
            servicio_window.configure(bg="#1E293B")
            
            tk.Label(servicio_window, text="Selecciona el tipo de servicio:", 
                     font=("Segoe UI", 11), fg="#F8FAFC", bg="#1E293B").pack(pady=20)
            
            tk.Radiobutton(servicio_window, text="Económico", variable=servicio_var, 
                           value="Económico", bg="#1E293B", fg="#F8FAFC",
                           selectcolor="#0F172A").pack(pady=5)
            tk.Radiobutton(servicio_window, text="Premium (+30%)", variable=servicio_var, 
                           value="Premium", bg="#1E293B", fg="#F8FAFC",
                           selectcolor="#0F172A").pack(pady=5)
            
            def confirmar_servicio():
                servicio_window.destroy()
                mostrar_factura(pasajero_actual, "Lima", destino, asiento, 
                               servicio=servicio_var.get())
            
            tk.Button(servicio_window, text="🧾 Generar Factura", command=confirmar_servicio,
                      bg="#8B5CF6", fg="white", font=("Segoe UI", 10, "bold"), 
                      padx=20, pady=8).pack(pady=20)
        
        tk.Button(marco_botones, text="🧾 Factura", command=generar_factura_pasajero,
                  bg="#8B5CF6", fg="white", font=("Segoe UI", 11, "bold"), 
                  padx=20, pady=8).grid(row=0, column=4, padx=10)
        
        # ===== BOTÓN ELIMINAR =====
        def eliminar():
            dni = entrada_dni.get().strip()
            if len(dni) != 8:
                messagebox.showwarning("Aviso", "Escribe un DNI de 8 dígitos")
                return
            for i, p in enumerate(self.pasajeros):
                if p.dni == dni:
                    if messagebox.askyesno("Confirmar", f"¿Eliminar a {p.nombre}?"):
                        del self.pasajeros[i]
                        self.pasajero_seleccionado = None
                        self.actualizar_lista_pasajeros()
                        self.historial.append(f"🗑️ Pasajero eliminado: {dni} - {p.nombre}")
                        entrada_dni.delete(0, tk.END)
                        entrada_nombre.delete(0, tk.END)
                        entrada_nombre.config(bg="white")
                        entrada_telefono.delete(0, tk.END)
                        entrada_asiento.delete(0, tk.END)
                        messagebox.showinfo("✅ Eliminado", "Pasajero eliminado")
                    return
            messagebox.showinfo("ℹ️ Aviso", "DNI no encontrado")
        
        tk.Button(marco_botones, text="🗑️ Eliminar", bg="#EF4444", fg="white",
                  font=("Segoe UI", 11, "bold"), padx=20, pady=8, command=eliminar).grid(row=0, column=2, padx=10)
        
        # ===== LISTA DE PASAJEROS =====
        tk.Label(self.area_principal, text="📋 Lista de Pasajeros Registrados (Haz clic para seleccionar)",
                 font=("Segoe UI", 13, "bold"), fg="white", bg=self.color_pestaña).pack(pady=(20, 5))
        
        frame_lista_scroll = tk.Frame(self.area_principal, bg=self.color_pestaña)
        frame_lista_scroll.pack(pady=5, fill="x", padx=40)
        
        canvas_lista = tk.Canvas(frame_lista_scroll, bg="white", height=150, highlightthickness=0)
        scrollbar_lista = tk.Scrollbar(frame_lista_scroll, orient="vertical", command=canvas_lista.yview)
        
        marco_lista = tk.Frame(canvas_lista, bg="white")
        marco_lista.bind(
            "<Configure>",
            lambda e: canvas_lista.configure(scrollregion=canvas_lista.bbox("all"))
        )
        
        canvas_lista.create_window((0, 0), window=marco_lista, anchor="nw")
        canvas_lista.configure(yscrollcommand=scrollbar_lista.set)
        
        canvas_lista.pack(side="left", fill="both", expand=True)
        scrollbar_lista.pack(side="right", fill="y")
        
        # Encabezados
        tk.Label(marco_lista, text="DNI", font=("Segoe UI", 10, "bold"), bg="#E5E7EB", width=12, relief="ridge").grid(row=0, column=0, padx=1, pady=2, sticky="ew")
        tk.Label(marco_lista, text="NOMBRE COMPLETO", font=("Segoe UI", 10, "bold"), bg="#E5E7EB", width=40, relief="ridge").grid(row=0, column=1, padx=1, pady=2, sticky="ew")
        tk.Label(marco_lista, text="DESTINO", font=("Segoe UI", 10, "bold"), bg="#E5E7EB", width=15, relief="ridge").grid(row=0, column=2, padx=1, pady=2, sticky="ew")
        tk.Label(marco_lista, text="ASIENTO", font=("Segoe UI", 10, "bold"), bg="#E5E7EB", width=10, relief="ridge").grid(row=0, column=3, padx=1, pady=2, sticky="ew")
        
        self.marco_lista_pasajeros = marco_lista
        self.actualizar_lista_pasajeros()

    def actualizar_lista_pasajeros(self):
        """Actualiza la lista de pasajeros con clic para seleccionar"""
        if not hasattr(self, 'marco_lista_pasajeros') or not self.marco_lista_pasajeros:
            return
        
        for widget in self.marco_lista_pasajeros.winfo_children():
            fila = widget.grid_info().get('row', 0)
            if fila > 0:
                widget.destroy()
        
        fila = 1
        for p in self.pasajeros:
            btn_dni = tk.Button(self.marco_lista_pasajeros, text=p.dni, 
                               font=("Segoe UI", 9), bg="white", width=12,
                               relief="flat", cursor="hand2",
                               command=lambda dni=p.dni: self.seleccionar_pasajero_click(dni))
            btn_dni.grid(row=fila, column=0, padx=1, pady=1, sticky="ew")
            
            btn_nombre = tk.Button(self.marco_lista_pasajeros, text=p.nombre[:28], 
                                  font=("Segoe UI", 9), bg="white", width=40,
                                  relief="flat", cursor="hand2", anchor="w",
                                  command=lambda dni=p.dni: self.seleccionar_pasajero_click(dni))
            btn_nombre.grid(row=fila, column=1, padx=1, pady=1, sticky="ew")
            
            tk.Label(self.marco_lista_pasajeros, text=p.destino, 
                    font=("Segoe UI", 9), bg="white", width=15).grid(row=fila, column=2, padx=1, pady=1)
            
            tk.Label(self.marco_lista_pasajeros, text=str(p.asiento) if p.asiento else "-", 
                    font=("Segoe UI", 9), bg="white", width=10).grid(row=fila, column=3, padx=1, pady=1)
            fila += 1

    def seleccionar_pasajero_click(self, dni):
        """Carga los datos del pasajero seleccionado al hacer clic"""
        for p in self.pasajeros:
            if p.dni == dni:
                if hasattr(self, 'entrada_dni') and self.entrada_dni:
                    self.entrada_dni.delete(0, tk.END)
                    self.entrada_dni.insert(0, p.dni)
                if hasattr(self, 'entrada_nombre') and self.entrada_nombre:
                    self.entrada_nombre.delete(0, tk.END)
                    self.entrada_nombre.insert(0, p.nombre)
                    self.entrada_nombre.config(bg="#FDE68A")
                if hasattr(self, 'entrada_telefono') and self.entrada_telefono:
                    self.entrada_telefono.delete(0, tk.END)
                    self.entrada_telefono.insert(0, p.telefono)
                if hasattr(self, 'var_destino') and self.var_destino:
                    self.var_destino.set(p.destino)
                if hasattr(self, 'entrada_asiento') and self.entrada_asiento:
                    self.entrada_asiento.delete(0, tk.END)
                    self.entrada_asiento.insert(0, p.asiento)
                
                self.pasajero_seleccionado = p
                messagebox.showinfo("✅ Seleccionado", 
                    f"Pasajero cargado:\n{p.nombre}\n\nYa puedes imprimir su boleto o factura.")
                break

    # ==============================================
    # REPORTES Y HISTORIAL
    # ==============================================
    
    def cargar_pantalla_reportes(self):
        self.limpiar_area_principal()
        tk.Label(self.area_principal, text="📊 REPORTES",
                 font=("Arial", 20, "bold"), fg="white", bg=self.color_pestaña).pack(pady=20)

        frame_stats = tk.Frame(self.area_principal, bg=self.color_pestaña)
        frame_stats.pack(pady=10)

        total = len(self.pasajeros)
        tk.Label(frame_stats, text=f"👥 Total Pasajeros: {total}", 
                font=("Arial", 14, "bold"), fg="#60A5FA", bg=self.color_pestaña).grid(row=0, column=0, padx=30)

        if self.asientos:
            libres = sum(1 for a in self.asientos if a.estado == "libre")
            ocupados = len(self.asientos) - libres
            tk.Label(frame_stats, text=f"💺 Asientos Ocupados: {ocupados}/{len(self.asientos)}", 
                    font=("Arial", 14, "bold"), fg="#FCD34D", bg=self.color_pestaña).grid(row=0, column=1, padx=30)

        caja_lista = tk.Text(self.area_principal, width=90, height=20, font=("Arial", 10))
        caja_lista.pack(pady=10)

        def actualizar_lista():
            caja_lista.delete("1.0", tk.END)
            if not self.pasajeros:
                caja_lista.insert(tk.END, "⚠️ No hay pasajeros registrados aún.\n")
                caja_lista.insert(tk.END, "📝 Registra un pasajero y aparecerá aquí.\n")
            else:
                caja_lista.insert(tk.END, f"{'DNI':<12} | {'NOMBRE':<30} | {'ASIENTO':<10} | {'DESTINO':<15} | {'TELÉFONO':<12} | {'FECHA'}\n")
                caja_lista.insert(tk.END, "-" * 100 + "\n")
                for p in self.pasajeros:
                    caja_lista.insert(tk.END, 
                        f"{p.dni:<12} | {p.nombre[:28]:<30} | {str(p.asiento) if p.asiento else '-':<10} | {p.destino:<15} | {p.telefono:<12} | {p.fecha_registro}\n")
        
        actualizar_lista()
        
        marco_botones = tk.Frame(self.area_principal, bg=self.color_pestaña)
        marco_botones.pack(pady=5)
        
        tk.Button(marco_botones, text="🔄 Actualizar", command=actualizar_lista,
                  bg="#2563EB", fg="white", font=("Arial", 10, "bold"), padx=15, pady=5).grid(row=0, column=0, padx=5)
        
        def exportar_reporte():
            if not self.pasajeros:
                messagebox.showinfo("Aviso", "No hay datos para exportar")
                return
            
            try:
                filename = f"reporte_pasajeros_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write("="*80 + "\n")
                    f.write("REPORTE DE PASAJEROS - CIVA TRANSPORTES\n")
                    f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
                    f.write("="*80 + "\n\n")
                    f.write(f"{'DNI':<12} | {'NOMBRE':<35} | {'DESTINO':<15} | {'ASIENTO':<8} | {'TELÉFONO'}\n")
                    f.write("-"*80 + "\n")
                    for p in self.pasajeros:
                        f.write(f"{p.dni:<12} | {p.nombre[:33]:<35} | {p.destino:<15} | {str(p.asiento) if p.asiento else '-':<8} | {p.telefono}\n")
                    f.write("\n" + "="*80 + "\n")
                    f.write(f"TOTAL PASAJEROS: {len(self.pasajeros)}\n")
                messagebox.showinfo("✅ Éxito", f"Reporte exportado como:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")
        
        tk.Button(marco_botones, text="📥 Exportar Reporte", command=exportar_reporte,
                  bg="#10B981", fg="white", font=("Arial", 10, "bold"), padx=15, pady=5).grid(row=0, column=1, padx=5)

    def cargar_pantalla_historial(self):
        self.limpiar_area_principal()
        tk.Label(self.area_principal, text="📜 HISTORIAL DE OPERACIONES",
                 font=("Arial", 20, "bold"), fg="white", bg=self.color_pestaña).pack(pady=20)

        caja_historial = tk.Text(self.area_principal, width=90, height=20, font=("Arial", 10))
        caja_historial.pack(pady=10)

        def actualizar_historial():
            caja_historial.delete("1.0", tk.END)
            if not self.historial:
                caja_historial.insert(tk.END, "ℹ️ Aún no hay registros en el historial.\n")
            else:
                for i, registro in enumerate(reversed(self.historial), 1):
                    caja_historial.insert(tk.END, f"{i:>3}. {registro}\n")

        actualizar_historial()

        def limpiar_historial():
            if messagebox.askyesno("Confirmar", "¿Borrar todo el historial?"):
                self.historial.clear()
                actualizar_historial()
                messagebox.showinfo("✅", "Historial eliminado")

        marco_botones = tk.Frame(self.area_principal, bg=self.color_pestaña)
        marco_botones.pack(pady=5)
        tk.Button(marco_botones, text="🔄 Actualizar", command=actualizar_historial,
                  bg="#2563EB", fg="white", font=("Arial", 10, "bold"), padx=15, pady=5).grid(row=0, column=0, padx=5)
        tk.Button(marco_botones, text="🗑️ Limpiar Historial", command=limpiar_historial,
                  bg="#EF4444", fg="white", font=("Arial", 10, "bold"), padx=15, pady=5).grid(row=0, column=1, padx=5)

    def cargar_datos_prueba(self):
        if Asiento:
            self.asientos = [Asiento(i+1, 35) for i in range(40)]

# ==============================================
# EJECUCIÓN
# ==============================================

def main():
    def iniciar_sistema():
        app = SistemaLogisticoCiva()
        app.root.mainloop()

    mostrar_pantalla_login(iniciar_sistema)

if __name__ == "__main__":
    main()