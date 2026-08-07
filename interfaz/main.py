import tkinter as tk
from tkinter import ttk, messagebox
import os
import hashlib
import json
from datetime import datetime
import subprocess
import tempfile
import requests

# ==============================================
# CARGAR VARIABLES DE ENTORNO
# ==============================================

CODART_TOKEN = "SQObJdDDnP9S1k1Hu8iAPCPbpjOghsUmiY9dUsdcJ58zdAFMX3SYQyJayCN7"

# ==============================================
# CONSULTA CODART API
# ==============================================

def consultar_dni_codart(dni):
    """Consulta datos personales por DNI usando CODART API"""
    if len(dni) != 8 or not dni.isdigit():
        return {"error": "El DNI debe tener 8 dígitos", "success": False}
    
    if not CODART_TOKEN:
        return {"error": "Token de CODART no configurado", "success": False}
    
    try:
        url = f"https://api-codart.cgrt.org/api/v1/consultas/reniec/dni/{dni}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {CODART_TOKEN}"
        }
        respuesta = requests.get(url, headers=headers, timeout=10)
        
        if respuesta.status_code == 200:
            data = respuesta.json()
            if data.get("success"):
                result = data.get("result", {})
                return {
                    "success": True,
                    "nombre_completo": result.get("full_name", ""),
                    "nombres": result.get("first_name", ""),
                    "apellido_paterno": result.get("first_last_name", ""),
                    "apellido_materno": result.get("second_last_name", ""),
                    "fuente": "CODART API"
                }
            else:
                return {"error": "DNI no encontrado en RENIEC", "success": False}
        else:
            return {"error": f"Error {respuesta.status_code}", "success": False}
            
    except Exception as e:
        return {"error": f"Error: {str(e)}", "success": False}

# ==============================================
# BASE DE DATOS DE PRUEBA
# ==============================================

BASE_DATOS_PRUEBA = {
    "12345678": {"nombre_completo": "JUAN CARLOS PEREZ GOMEZ"},
    "87654321": {"nombre_completo": "MARIA ELENA LOPEZ FLORES"},
    "45678912": {"nombre_completo": "PEDRO ANTONIO RAMIREZ SANCHEZ"},
    "78912345": {"nombre_completo": "ANA MARIA TORRES VEGA"},
    "32165498": {"nombre_completo": "CARLOS ALBERTO MENDOZA RUIZ"},
    "65498732": {"nombre_completo": "LAURA PATRICIA CASTRO DIAZ"},
}

def consultar_dni_reniec(dni):
    """Consulta datos personales por DNI (CODART o local)"""
    resultado = consultar_dni_codart(dni)
    if resultado.get("success"):
        return resultado
    
    if dni in BASE_DATOS_PRUEBA:
        datos = BASE_DATOS_PRUEBA[dni].copy()
        datos["success"] = True
        datos["fuente"] = "Base de datos local"
        return datos
    else:
        return {"error": "DNI no encontrado", "success": False}

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
    "Lima": 0, "Huaral": 45, "Ica": 65, "Nazca": 85,
    "Arequipa": 120, "Trujillo": 95, "Chiclayo": 110
}

# ==============================================
# DIÁLOGO DE IMPRESIÓN PROFESIONAL
# ==============================================

def mostrar_dialogo_impresion(parent=None):
    """
    Muestra un diálogo profesional para seleccionar opciones de impresión
    """
    ventana = tk.Toplevel(parent)
    ventana.title("🖨️ Imprimir Documento")
    ventana.geometry("420x380")
    ventana.resizable(False, False)
    ventana.configure(bg="#1E293B")
    ventana.transient(parent)
    ventana.grab_set()
    
    # Centrar
    x = (ventana.winfo_screenwidth() // 2) - 210
    y = (ventana.winfo_screenheight() // 2) - 190
    ventana.geometry(f"420x380+{x}+{y}")
    
    # Título con icono
    tk.Label(ventana, text="🖨️ Opciones de Impresión",
             font=("Segoe UI", 16, "bold"), fg="#F8FAFC", bg="#1E293B").pack(pady=15)
    
    tk.Frame(ventana, bg="#334155", height=1, width=380).pack(pady=5)
    
    # Marco principal
    marco = tk.Frame(ventana, bg="#1E293B")
    marco.pack(pady=15, padx=25, fill="both", expand=True)
    
    # ===== TAMAÑO DE PAPEL =====
    tk.Label(marco, text="📄 Tamaño de papel:", font=("Segoe UI", 11, "bold"),
             fg="#FCD34D", bg="#1E293B").pack(anchor="w", pady=(0, 5))
    
    var_papel = tk.StringVar()
    var_papel.set("Ticket (80mm)")
    
    opciones_papel = [
        "Ticket (80mm)",
        "Ticket (58mm)",
        "A4",
        "Carta",
        "Oficio"
    ]
    
    menu_papel = tk.OptionMenu(marco, var_papel, *opciones_papel)
    menu_papel.config(width=30, font=("Segoe UI", 10), bg="#0F172A", fg="#F8FAFC",
                      relief="flat", highlightthickness=1, highlightcolor="#2563EB")
    menu_papel.pack(pady=(0, 12), anchor="w")
    
    # ===== IMPRESORA =====
    tk.Label(marco, text="🖨️ Impresora:", font=("Segoe UI", 11, "bold"),
             fg="#FCD34D", bg="#1E293B").pack(anchor="w", pady=(0, 5))
    
    # Obtener impresoras disponibles
    impresoras = ["Impresora predeterminada"]
    try:
        if os.name == 'nt':
            import win32print
            impresoras = [p[2] for p in win32print.EnumPrinters(
                win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
    except:
        pass
    
    var_impresora = tk.StringVar()
    var_impresora.set(impresoras[0])
    
    menu_impresora = tk.OptionMenu(marco, var_impresora, *impresoras)
    menu_impresora.config(width=30, font=("Segoe UI", 10), bg="#0F172A", fg="#F8FAFC",
                          relief="flat", highlightthickness=1, highlightcolor="#2563EB")
    menu_impresora.pack(pady=(0, 12), anchor="w")
    
    # ===== COPIAS =====
    frame_copias = tk.Frame(marco, bg="#1E293B")
    frame_copias.pack(anchor="w", pady=(0, 12))
    
    tk.Label(frame_copias, text="📋 Copias:", font=("Segoe UI", 11, "bold"),
             fg="#FCD34D", bg="#1E293B").pack(side="left", padx=(0, 15))
    
    var_copias = tk.IntVar()
    var_copias.set(1)
    
    spin_copias = tk.Spinbox(frame_copias, from_=1, to=10, textvariable=var_copias,
                              width=8, font=("Segoe UI", 11), bg="#0F172A", fg="#F8FAFC",
                              relief="flat", highlightthickness=1, highlightcolor="#2563EB")
    spin_copias.pack(side="left")
    
    # ===== BOTONES =====
    frame_botones = tk.Frame(ventana, bg="#1E293B")
    frame_botones.pack(pady=15, fill="x", padx=25)
    
    # Variable para devolver el resultado
    resultado = [None]
    
    def imprimir():
        resultado[0] = {
            "papel": var_papel.get(),
            "impresora": var_impresora.get(),
            "copias": var_copias.get()
        }
        ventana.destroy()
    
    def cancelar():
        resultado[0] = None
        ventana.destroy()
    
    tk.Button(frame_botones, text="🖨️ Imprimir", 
              command=imprimir,
              bg="#10B981", fg="white", font=("Segoe UI", 11, "bold"), 
              padx=25, pady=10, relief="flat").pack(side="left", padx=(0, 10))
    
    tk.Button(frame_botones, text="❌ Cancelar", 
              command=cancelar,
              bg="#EF4444", fg="white", font=("Segoe UI", 11, "bold"), 
              padx=25, pady=10, relief="flat").pack(side="left")
    
    ventana.wait_window()
    return resultado[0]

# ==============================================
# FUNCIONES DE IMPRESIÓN MEJORADAS
# ==============================================

def imprimir_con_dialogo(contenido_texto, parent=None):
    """
    Imprime mostrando el diálogo de selección de opciones
    """
    try:
        # Mostrar diálogo
        opciones = mostrar_dialogo_impresion(parent)
        
        if opciones is None:
            return False, "⚠️ Impresión cancelada por el usuario"
        
        # Obtener opciones
        papel = opciones.get("papel", "Ticket (80mm)")
        copias = opciones.get("copias", 1)
        
        # Configurar ancho según papel
        if "80mm" in papel:
            ancho = 32
        elif "58mm" in papel:
            ancho = 24
        else:
            ancho = 80
        
        # Reformatear texto
        lineas = []
        for linea in contenido_texto.split('\n'):
            if len(linea) <= ancho:
                lineas.append(linea)
            else:
                for i in range(0, len(linea), ancho):
                    lineas.append(linea[i:i+ancho])
        
        contenido_formateado = '\n'.join(lineas)
        
        # Agregar separador entre copias
        if copias > 1:
            contenido_formateado = (contenido_formateado + "\n" + "-" * ancho + "\n") * copias
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(contenido_formateado)
            archivo_temp = f.name
        
        # Imprimir según el sistema operativo
        if os.name == 'nt':
            # Windows
            try:
                # Intentar con la impresora seleccionada
                if opciones.get("impresora") != "Impresora predeterminada":
                    # Usar el comando de impresión con la impresora específica
                    subprocess.run(['notepad', '/p', archivo_temp], check=True)
                else:
                    subprocess.run(['notepad', '/p', archivo_temp], check=True)
            except:
                subprocess.run(['notepad', '/p', archivo_temp], check=True)
        else:
            # Linux/Mac
            subprocess.run(['lp', '-o', 'media=80mm', archivo_temp], check=True)
        
        os.unlink(archivo_temp)
        return True, f"✅ Documento enviado a la impresora\n📄 {papel} | 📋 {copias} copia(s)"
        
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def imprimir_ticket_directo(contenido_texto, parent=None):
    """
    Imprime mostrando el diálogo de selección de opciones
    """
    return imprimir_con_dialogo(contenido_texto, parent)

# ==============================================
# FUNCIONES DE IMPRESIÓN EN TICKET (80mm)
# ==============================================

def centrar(texto, ancho=32):
    """Centra texto para ticket de 80mm"""
    espacios = ancho - len(texto)
    if espacios <= 0:
        return texto
    izquierda = espacios // 2
    derecha = espacios - izquierda
    return " " * izquierda + texto + " " * derecha

def imprimir_boleta_ticket(pasajero, origen="Lima", destino="", fecha_viaje=None):
    """Genera boleto optimizado para ticket 80mm"""
    if not fecha_viaje:
        fecha_viaje = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    num_boleta = f"B-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    filename = f"boleto_{pasajero.dni}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    LINEA = "=" * 32
    LINEA_PUNTEADA = "-" * 32
    
    contenido = f"""
{centrar("🚌 CIVA TRANSPORTES 🚌")}
{centrar("TRANSPORTE INTERPROVINCIAL")}
{LINEA}

{centrar("🎫 BOLETO DE VIAJE")}
{centrar(f"N°: {num_boleta}")}
{LINEA_PUNTEADA}

👤 PASAJERO
   {pasajero.nombre}
   DNI: {pasajero.dni}
   Tel: {pasajero.telefono if pasajero.telefono else 'No registrado'}

{LINEA_PUNTEADA}
🚌 VIAJE
   Origen:  {origen}
   Destino: {destino}
   Asiento: {pasajero.asiento if pasajero.asiento else 'No asignado'}
   Fecha:   {fecha_viaje}

{LINEA_PUNTEADA}
💰 TOTAL: S/ 0.00
{LINEA}

{centrar("✨ ¡GRACIAS POR VIAJAR! ✨")}
{centrar("Presenta este boleto al abordar")}
{centrar("⏰ Llegar 30 min antes")}
{LINEA}
    """
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(contenido)
    return filename, contenido

def mostrar_boleta_ticket(pasajero, origen="Lima", destino="", fecha_viaje=None):
    """Muestra vista previa del boleto con diálogo de impresión"""
    if not fecha_viaje:
        fecha_viaje = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    filename, contenido = imprimir_boleta_ticket(pasajero, origen, destino, fecha_viaje)
    
    ventana = tk.Toplevel()
    ventana.title(f"🎫 Boleto - {pasajero.nombre}")
    ventana.geometry("400x600")
    ventana.resizable(False, False)
    ventana.configure(bg="#1E293B")
    
    tk.Label(ventana, text="🎫 BOLETO DE VIAJE", 
             font=("Segoe UI", 12, "bold"), fg="#F8FAFC", bg="#1E293B").pack(pady=8)
    
    ticket_frame = tk.Frame(ventana, bg="white", relief="solid", bd=1)
    ticket_frame.pack(padx=15, pady=5, fill="both", expand=True)
    
    ticket_text = tk.Text(ticket_frame, font=("Courier New", 9), bg="white", 
                          fg="#000000", wrap="none", height=30)
    ticket_text.pack(fill="both", expand=True, padx=5, pady=5)
    ticket_text.insert("1.0", contenido)
    ticket_text.config(state="disabled")
    
    frame_botones = tk.Frame(ventana, bg="#1E293B")
    frame_botones.pack(pady=10, fill="x")
    
    def guardar():
        messagebox.showinfo("✅ Éxito", f"Ticket guardado como:\n{filename}")
    
    def imprimir():
        exito, mensaje = imprimir_con_dialogo(contenido, ventana)
        if exito:
            messagebox.showinfo("🖨️ Éxito", mensaje)
        else:
            messagebox.showerror("❌ Error", mensaje)
    
    def cerrar():
        ventana.destroy()
    
    tk.Button(frame_botones, text="💾 Guardar", 
              command=guardar,
              bg="#2563EB", fg="white", font=("Segoe UI", 8, "bold"), 
              padx=10, pady=4).pack(side="left", padx=5, expand=True, fill="x")
    
    tk.Button(frame_botones, text="🖨️ Imprimir", 
              command=imprimir,
              bg="#10B981", fg="white", font=("Segoe UI", 8, "bold"), 
              padx=10, pady=4).pack(side="left", padx=5, expand=True, fill="x")
    
    tk.Button(frame_botones, text="❌ Cerrar", 
              command=cerrar,
              bg="#EF4444", fg="white", font=("Segoe UI", 8, "bold"), 
              padx=10, pady=4).pack(side="left", padx=5, expand=True, fill="x")

# ==============================================
# FUNCIONES DE FACTURACIÓN
# ==============================================

def calcular_precio_viaje(destino, tipo_servicio="Económico"):
    precio_base = PRECIOS_DESTINO.get(destino, 50.00)
    if tipo_servicio == "Premium":
        precio_base = precio_base * 1.3
    return precio_base

def generar_factura(pasajero, origen="Lima", destino="", asiento="", 
                    fecha_viaje=None, tipo_servicio="Económico", metodo_pago="Efectivo"):
    if not fecha_viaje:
        fecha_viaje = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    num_factura = f"F001-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    precio_unitario = calcular_precio_viaje(destino, tipo_servicio)
    subtotal = precio_unitario
    igv = subtotal * EMPRESA["igv"]
    total = subtotal + igv
    
    return {
        "numero": num_factura,
        "fecha_emision": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "fecha_viaje": fecha_viaje,
        "cliente": {"nombre": pasajero.nombre, "dni": pasajero.dni},
        "viaje": {"origen": origen, "destino": destino, "asiento": asiento, "tipo_servicio": tipo_servicio},
        "subtotal": subtotal, "igv": igv, "total": total,
        "metodo_pago": metodo_pago
    }

def mostrar_factura_ticket(pasajero, origen="Lima", destino="", asiento="", 
                           fecha_viaje=None, servicio="Económico", metodo_pago="Efectivo"):
    if not fecha_viaje:
        fecha_viaje = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    factura = generar_factura(pasajero, origen, destino, asiento, fecha_viaje, servicio, metodo_pago)
    
    LINEA = "=" * 32
    LINEA_PUNTEADA = "-" * 32
    
    contenido = f"""
{centrar("🧾 FACTURA ELECTRÓNICA")}
{centrar(EMPRESA['nombre'])}
{centrar(f"RUC: {EMPRESA['ruc']}")}
{LINEA}

{centrar(f"N°: {factura['numero']}")}
{centrar(f"Fecha: {factura['fecha_emision']}")}
{LINEA_PUNTEADA}

📋 CLIENTE
   {factura['cliente']['nombre']}
   DNI: {factura['cliente']['dni']}

{LINEA_PUNTEADA}
🚌 VIAJE
   {factura['viaje']['origen']} → {factura['viaje']['destino']}
   Asiento: {factura['viaje']['asiento'] or 'No asignado'}
   Servicio: {factura['viaje']['tipo_servicio']}

{LINEA_PUNTEADA}
💰 PAGO
   Subtotal: S/{factura['subtotal']:.2f}
   IGV (18%): S/{factura['igv']:.2f}
   {centrar(f"TOTAL: S/{factura['total']:.2f}")}

{LINEA_PUNTEADA}
   Método: {factura['metodo_pago']}

{LINEA}
{centrar("✨ ¡GRACIAS POR VIAJAR! ✨")}
{LINEA}
    """
    
    ventana = tk.Toplevel()
    ventana.title(f"🧾 Factura - {pasajero.nombre}")
    ventana.geometry("400x600")
    ventana.resizable(False, False)
    ventana.configure(bg="#1E293B")
    
    tk.Label(ventana, text="🧾 FACTURA", 
             font=("Segoe UI", 12, "bold"), fg="#F8FAFC", bg="#1E293B").pack(pady=8)
    
    ticket_frame = tk.Frame(ventana, bg="white", relief="solid", bd=1)
    ticket_frame.pack(padx=15, pady=5, fill="both", expand=True)
    
    ticket_text = tk.Text(ticket_frame, font=("Courier New", 9), bg="white", 
                          fg="#000000", wrap="none", height=30)
    ticket_text.pack(fill="both", expand=True, padx=5, pady=5)
    ticket_text.insert("1.0", contenido)
    ticket_text.config(state="disabled")
    
    frame_botones = tk.Frame(ventana, bg="#1E293B")
    frame_botones.pack(pady=10, fill="x")
    
    def imprimir():
        exito, mensaje = imprimir_con_dialogo(contenido, ventana)
        if exito:
            messagebox.showinfo("🖨️ Éxito", mensaje)
        else:
            messagebox.showerror("❌ Error", mensaje)
    
    def cerrar():
        ventana.destroy()
    
    tk.Button(frame_botones, text="🖨️ Imprimir", 
              command=imprimir,
              bg="#10B981", fg="white", font=("Segoe UI", 8, "bold"), 
              padx=10, pady=4).pack(side="left", padx=5, expand=True, fill="x")
    
    tk.Button(frame_botones, text="❌ Cerrar", 
              command=cerrar,
              bg="#EF4444", fg="white", font=("Segoe UI", 8, "bold"), 
              padx=10, pady=4).pack(side="left", padx=5, expand=True, fill="x")

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

def cifrar_clave(clave):
    return hashlib.md5(clave.encode()).hexdigest()

# ==============================================
# CLASE PASAJERO
# ==============================================

class Pasajero:
    def __init__(self, dni, nombre, telefono="", destino="", asiento=0):
        self.dni = dni
        self.nombre = nombre
        self.telefono = telefono
        self.destino = destino
        self.asiento = asiento

# ==============================================
# SISTEMA PRINCIPAL
# ==============================================

class SistemaLogisticoCiva:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema Logístico Civa")
        self.root.geometry("1050x800")
        self.root.configure(bg="#0F172A")
        
        self.pasajeros = []
        self.historial = []
        self.entrada_dni = None
        self.entrada_nombre = None
        self.entrada_telefono = None
        self.entrada_asiento = None
        self.var_destino = None
        
        self.ciudades = ["Lima", "Huaral", "Ica", "Nazca", "Arequipa", "Trujillo", "Chiclayo"]
        
        self.crear_interfaz()
        self.cargar_inicio()
    
    def crear_interfaz(self):
        # Título
        marco_titulo = tk.Frame(self.root, bg="#2563EB", height=80)
        marco_titulo.pack(fill="x")
        marco_titulo.pack_propagate(False)
        
        tk.Label(marco_titulo, text="🏢 SISTEMA LOGÍSTICO CIVA",
                 font=("Segoe UI", 22, "bold"),
                 bg="#2563EB", fg="white").pack(pady=(15, 2))
        tk.Label(marco_titulo, text="Transporte Interprovincial",
                 font=("Segoe UI", 10, "italic"),
                 bg="#2563EB", fg="#BFDBFE").pack()
        
        # Pestañas
        frame_tabs = tk.Frame(self.root, bg="#0F172A")
        frame_tabs.pack(pady=(0, 5))
        
        pestañas = [
            ("🏠 Inicio", self.cargar_inicio),
            ("👤 Pasajeros", self.cargar_pasajeros),
            ("🎫 Boletos", self.cargar_boletos),
            ("🧾 Facturas", self.cargar_facturas),
            ("📊 Reportes", self.cargar_reportes)
        ]
        
        for i, (nombre, funcion) in enumerate(pestañas):
            btn = tk.Button(frame_tabs, text=nombre, font=("Segoe UI", 10, "bold"),
                            bg="#1E293B", fg="#F8FAFC",
                            padx=18, pady=8, relief="flat", cursor="hand2",
                            activebackground="#2563EB",
                            command=funcion)
            btn.grid(row=0, column=i, padx=3)
        
        self.area_principal = tk.Frame(self.root, bg="#1E293B", width=980, height=540)
        self.area_principal.pack(pady=15)
        self.area_principal.pack_propagate(False)
    
    def limpiar_area(self):
        for widget in self.area_principal.winfo_children():
            widget.destroy()
    
    def cargar_inicio(self):
        self.limpiar_area()
        self.area_principal.config(bg="#0F172A")
        
        frame = tk.Frame(self.area_principal, bg="#0F172A")
        frame.pack(expand=True, fill="both")
        
        tk.Label(frame, text="SISTEMA LOGÍSTICO CIVA",
                 font=("Segoe UI", 36, "bold"), 
                 fg="#F8FAFC", bg="#0F172A").pack(pady=(80, 10))
        
        tk.Label(frame, text="Gestión Integral de Transporte Interprovincial",
                 font=("Segoe UI", 16), fg="#94A3B8", bg="#0F172A").pack(pady=(0, 30))
        
        tk.Frame(frame, bg="#2563EB", height=3, width=400).pack(pady=20)
        
        tk.Label(frame, 
                 text="🏢 Sistema para la gestión de:\n\n"
                      "• 👤 Registro de pasajeros\n"
                      "• 🎫 Generación de boletos\n"
                      "• 🧾 Facturación electrónica\n"
                      "• 📊 Reportes y estadísticas",
                 font=("Segoe UI", 12),
                 fg="#CBD5E1", bg="#0F172A",
                 justify="center").pack(pady=10)
        
        tk.Label(frame, 
                 text="v2.0 | Civa Transportes",
                 font=("Segoe UI", 9), fg="#64748B", bg="#0F172A").pack(side="bottom", pady=20)
    
    def cargar_pasajeros(self):
        self.limpiar_area()
        
        tk.Label(self.area_principal, text="👤 REGISTRO DE PASAJEROS",
                 font=("Segoe UI", 22, "bold"), fg="white", bg="#1E293B").pack(pady=15)
        
        marco = tk.Frame(self.area_principal, bg="#1E293B")
        marco.pack(pady=10)
        
        # DNI
        tk.Label(marco, text="DNI:", font=("Segoe UI", 11, "bold"),
                 fg="white", bg="#1E293B").grid(row=0, column=0, padx=5, pady=8, sticky="e")
        
        entrada_dni = tk.Entry(marco, width=12, font=("Segoe UI", 12))
        entrada_dni.grid(row=0, column=1, padx=5, pady=8)
        self.entrada_dni = entrada_dni
        
        def buscar_dni():
            dni = entrada_dni.get().strip()
            if len(dni) != 8:
                messagebox.showwarning("Aviso", "El DNI debe tener 8 dígitos")
                return
            
            resultado = consultar_dni_reniec(dni)
            if resultado.get("success"):
                entrada_nombre.delete(0, tk.END)
                entrada_nombre.insert(0, resultado.get("nombre_completo", ""))
                entrada_nombre.config(bg="#F0FDF4")
                messagebox.showinfo("✅ Éxito", f"Datos encontrados:\n{resultado.get('nombre_completo')}")
            else:
                messagebox.showerror("Error", resultado.get("error", "Error desconocido"))
        
        tk.Button(marco, text="🔍 Buscar", bg="#2563EB", fg="white",
                  font=("Segoe UI", 10, "bold"), padx=10, command=buscar_dni).grid(row=0, column=2, padx=8, pady=8)
        
        # Nombre
        tk.Label(marco, text="Nombre:", font=("Segoe UI", 11, "bold"),
                 fg="white", bg="#1E293B").grid(row=1, column=0, padx=5, pady=8, sticky="e")
        
        entrada_nombre = tk.Entry(marco, width=35, font=("Segoe UI", 12))
        entrada_nombre.grid(row=1, column=1, columnspan=2, padx=5, pady=8)
        self.entrada_nombre = entrada_nombre
        
        # Teléfono
        tk.Label(marco, text="Teléfono:", font=("Segoe UI", 11, "bold"),
                 fg="white", bg="#1E293B").grid(row=2, column=0, padx=5, pady=8, sticky="e")
        
        entrada_telefono = tk.Entry(marco, width=15, font=("Segoe UI", 12))
        entrada_telefono.grid(row=2, column=1, padx=5, pady=8)
        self.entrada_telefono = entrada_telefono
        
        # Destino
        tk.Label(marco, text="Destino:", font=("Segoe UI", 11, "bold"),
                 fg="white", bg="#1E293B").grid(row=2, column=2, padx=5, pady=8, sticky="e")
        
        var_destino = tk.StringVar()
        var_destino.set("Lima")
        menu_destino = tk.OptionMenu(marco, var_destino, *self.ciudades)
        menu_destino.config(width=15, font=("Segoe UI", 10))
        menu_destino.grid(row=2, column=3, padx=5, pady=8)
        self.var_destino = var_destino
        
        # Asiento
        tk.Label(marco, text="Asiento:", font=("Segoe UI", 11, "bold"),
                 fg="white", bg="#1E293B").grid(row=3, column=0, padx=5, pady=8, sticky="e")
        
        entrada_asiento = tk.Entry(marco, width=12, font=("Segoe UI", 12))
        entrada_asiento.grid(row=3, column=1, padx=5, pady=8)
        self.entrada_asiento = entrada_asiento
        
        # Botones
        marco_botones = tk.Frame(self.area_principal, bg="#1E293B")
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
            
            for p in self.pasajeros:
                if p.dni == dni:
                    messagebox.showwarning("Aviso", "Ese DNI ya está registrado")
                    return
            
            pasajero = Pasajero(dni, nombre, telefono, destino, asiento)
            self.pasajeros.append(pasajero)
            self.historial.append(f"✅ Pasajero registrado: {nombre}")
            
            entrada_dni.delete(0, tk.END)
            entrada_nombre.delete(0, tk.END)
            entrada_nombre.config(bg="white")
            entrada_telefono.delete(0, tk.END)
            entrada_asiento.delete(0, tk.END)
            
            messagebox.showinfo("✅ Éxito", f"Pasajero {nombre} registrado correctamente")
            self.actualizar_lista()
        
        tk.Button(marco_botones, text="✅ Registrar", bg="#10B981", fg="white",
                  font=("Segoe UI", 11, "bold"), padx=20, pady=8, command=registrar).grid(row=0, column=0, padx=10)
        
        # Lista
        tk.Label(self.area_principal, text="📋 Lista de Pasajeros",
                 font=("Segoe UI", 13, "bold"), fg="white", bg="#1E293B").pack(pady=(20, 5))
        
        self.lista = tk.Listbox(self.area_principal, width=80, height=10, font=("Segoe UI", 10))
        self.lista.pack(pady=5)
        self.actualizar_lista()
    
    def actualizar_lista(self):
        self.lista.delete(0, tk.END)
        for p in self.pasajeros:
            self.lista.insert(tk.END, f"{p.dni} - {p.nombre} - {p.destino}")
    
    def cargar_boletos(self):
        self.limpiar_area()
        
        tk.Label(self.area_principal, text="🎫 GENERAR BOLETO",
                 font=("Segoe UI", 22, "bold"), fg="white", bg="#1E293B").pack(pady=15)
        
        if not self.pasajeros:
            tk.Label(self.area_principal, text="⚠️ Primero registra un pasajero",
                     font=("Segoe UI", 14), fg="#FCD34D", bg="#1E293B").pack(pady=30)
            return
        
        tk.Label(self.area_principal, text="Selecciona un pasajero:", 
                 font=("Segoe UI", 12), fg="white", bg="#1E293B").pack()
        
        opciones = [f"{p.dni} - {p.nombre}" for p in self.pasajeros]
        var_seleccion = tk.StringVar()
        var_seleccion.set(opciones[0])
        
        menu = tk.OptionMenu(self.area_principal, var_seleccion, *opciones)
        menu.config(width=30, font=("Segoe UI", 10))
        menu.pack(pady=10)
        
        def generar():
            seleccion = var_seleccion.get()
            dni = seleccion.split(" - ")[0]
            pasajero = None
            for p in self.pasajeros:
                if p.dni == dni:
                    pasajero = p
                    break
            
            if pasajero:
                destino = pasajero.destino or "No especificado"
                mostrar_boleta_ticket(pasajero, "Lima", destino)
        
        tk.Button(self.area_principal, text="🎫 Generar Boleto", 
                  command=generar,
                  bg="#8B5CF6", fg="white", font=("Segoe UI", 12, "bold"),
                  padx=30, pady=10).pack(pady=20)
    
    def cargar_facturas(self):
        self.limpiar_area()
        
        tk.Label(self.area_principal, text="🧾 GENERAR FACTURA",
                 font=("Segoe UI", 22, "bold"), fg="white", bg="#1E293B").pack(pady=15)
        
        if not self.pasajeros:
            tk.Label(self.area_principal, text="⚠️ Primero registra un pasajero",
                     font=("Segoe UI", 14), fg="#FCD34D", bg="#1E293B").pack(pady=30)
            return
        
        tk.Label(self.area_principal, text="Selecciona un pasajero:", 
                 font=("Segoe UI", 12), fg="white", bg="#1E293B").pack()
        
        opciones = [f"{p.dni} - {p.nombre}" for p in self.pasajeros]
        var_seleccion = tk.StringVar()
        var_seleccion.set(opciones[0])
        
        menu = tk.OptionMenu(self.area_principal, var_seleccion, *opciones)
        menu.config(width=30, font=("Segoe UI", 10))
        menu.pack(pady=10)
        
        frame_opciones = tk.Frame(self.area_principal, bg="#1E293B")
        frame_opciones.pack(pady=10)
        
        tk.Label(frame_opciones, text="Servicio:", font=("Segoe UI", 11),
                 fg="white", bg="#1E293B").grid(row=0, column=0, padx=10)
        var_servicio = tk.StringVar()
        var_servicio.set("Económico")
        tk.OptionMenu(frame_opciones, var_servicio, "Económico", "Premium").grid(row=0, column=1)
        
        tk.Label(frame_opciones, text="Método de Pago:", font=("Segoe UI", 11),
                 fg="white", bg="#1E293B").grid(row=0, column=2, padx=10)
        var_pago = tk.StringVar()
        var_pago.set("Efectivo")
        tk.OptionMenu(frame_opciones, var_pago, "Efectivo", "Tarjeta", "Yape", "Plin").grid(row=0, column=3)
        
        def generar():
            seleccion = var_seleccion.get()
            dni = seleccion.split(" - ")[0]
            pasajero = None
            for p in self.pasajeros:
                if p.dni == dni:
                    pasajero = p
                    break
            
            if pasajero:
                destino = pasajero.destino or "No especificado"
                asiento = str(pasajero.asiento) if pasajero.asiento else ""
                mostrar_factura_ticket(pasajero, "Lima", destino, asiento, 
                                       servicio=var_servicio.get(), metodo_pago=var_pago.get())
        
        tk.Button(self.area_principal, text="🧾 Generar Factura", 
                  command=generar,
                  bg="#8B5CF6", fg="white", font=("Segoe UI", 12, "bold"),
                  padx=30, pady=10).pack(pady=20)
    
    def cargar_reportes(self):
        self.limpiar_area()
        
        tk.Label(self.area_principal, text="📊 REPORTES",
                 font=("Segoe UI", 22, "bold"), fg="white", bg="#1E293B").pack(pady=15)
        
        col1 = tk.Frame(self.area_principal, bg="#1E293B")
        col1.pack(side="left", expand=True, fill="both", padx=10)
        col2 = tk.Frame(self.area_principal, bg="#1E293B")
        col2.pack(side="left", expand=True, fill="both", padx=10)
        col3 = tk.Frame(self.area_principal, bg="#1E293B")
        col3.pack(side="left", expand=True, fill="both", padx=10)
        
        tk.Label(col1, text=f"👥 {len(self.pasajeros)}", 
                 font=("Segoe UI", 24, "bold"), fg="#60A5FA", bg="#1E293B").pack()
        tk.Label(col1, text="Pasajeros", font=("Segoe UI", 12), fg="#94A3B8", bg="#1E293B").pack()
        
        tk.Label(col2, text=f"🎫 {len([h for h in self.historial if 'boleto' in h.lower()])}", 
                 font=("Segoe UI", 24, "bold"), fg="#FCD34D", bg="#1E293B").pack()
        tk.Label(col2, text="Boletos", font=("Segoe UI", 12), fg="#94A3B8", bg="#1E293B").pack()
        
        tk.Label(col3, text=f"🧾 {len([h for h in self.historial if 'factura' in h.lower()])}", 
                 font=("Segoe UI", 24, "bold"), fg="#10B981", bg="#1E293B").pack()
        tk.Label(col3, text="Facturas", font=("Segoe UI", 12), fg="#94A3B8", bg="#1E293B").pack()

# ==============================================
# FUNCIONES DE LOGIN
# ==============================================

def mostrar_login(al_ingresar):
    ventana = tk.Tk()
    ventana.title("Inicio de Sesión - Civa")
    ventana.geometry("400x420")
    ventana.resizable(False, False)
    ventana.configure(bg="#0F172A")
    
    x = (ventana.winfo_screenwidth() // 2) - 200
    y = (ventana.winfo_screenheight() // 2) - 210
    ventana.geometry(f"400x420+{x}+{y}")
    
    tk.Label(ventana, text="🚌 Sistema Logístico Civa", 
             font=("Segoe UI", 16, "bold"), fg="#F8FAFC", bg="#0F172A").pack(pady=(40, 10))
    tk.Label(ventana, text="Inicia sesión para continuar", 
             font=("Segoe UI", 10), fg="#94A3B8", bg="#0F172A").pack(pady=(0, 30))
    
    marco = tk.Frame(ventana, bg="#0F172A")
    marco.pack(pady=10)
    
    tk.Label(marco, text="Correo electrónico:", font=("Segoe UI", 11),
             fg="#F8FAFC", bg="#0F172A").grid(row=0, column=0, sticky="w", pady=5)
    entrada_correo = tk.Entry(marco, width=35, font=("Segoe UI", 11))
    entrada_correo.grid(row=1, column=0, pady=5)
    entrada_correo.insert(0, "admin@civa.com")
    
    tk.Label(marco, text="Contraseña:", font=("Segoe UI", 11),
             fg="#F8FAFC", bg="#0F172A").grid(row=2, column=0, sticky="w", pady=(15, 5))
    entrada_contraseña = tk.Entry(marco, width=35, show="•", font=("Segoe UI", 11))
    entrada_contraseña.grid(row=3, column=0, pady=5)
    entrada_contraseña.insert(0, "123456")
    
    def verificar():
        correo = entrada_correo.get().strip()
        clave = entrada_contraseña.get().strip()
        
        if correo in USUARIOS and USUARIOS[correo]["clave_hash"] == cifrar_clave(clave):
            ventana.destroy()
            al_ingresar()
        else:
            messagebox.showerror("Error", "Correo o contraseña incorrectos")
    
    tk.Button(ventana, text="🚪 Iniciar Sesión", 
              command=verificar,
              bg="#2563EB", fg="white", font=("Segoe UI", 11, "bold"),
              padx=40, pady=10, relief="flat").pack(pady=30)
    
    tk.Label(ventana, text="Demo: admin@civa.com / 123456",
             font=("Segoe UI", 9), fg="#64748B", bg="#0F172A").pack()
    
    ventana.mainloop()

# ==============================================
# MAIN
# ==============================================

def main():
    def iniciar():
        app = SistemaLogisticoCiva()
        app.root.mainloop()
    
    mostrar_login(iniciar)

if __name__ == "__main__":
    main()