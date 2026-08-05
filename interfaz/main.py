import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import hashlib
import json

# ==============================================
# SISTEMA DE USUARIOS Y CONFIGURACIÓN
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
        with open(ARCHIVO_RECORDAR, "r") as f:
            datos = json.load(f)
            return datos.get("correo", "")
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
# IMPORTACIONES DE TUS MÓDULOS
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
except Exception as e:
    Cola = None
    Chofer = Bus = Ruta = Asiento = None
    asignar_chofer = enviar_a_descanso = liberar_de_descanso = None
    registrar_bus = asignar_bus = calcular_ruta_mas_corta = None


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

    def __str__(self):
        return f"DNI: {self.dni} | {self.nombre} | Asiento: {self.asiento}"


# ==============================================
# SISTEMA PRINCIPAL COMPLETO
# ==============================================

class SistemaLogisticoCiva:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema Logístico Civa - Transporte Interprovincial")
        self.root.geometry("1000x700")

        self.color_fondo = "#1a1a2e"
        self.color_pestaña = "#16213e"
        self.color_texto = "#ffffff"
        self.root.configure(bg=self.color_fondo)

        if Cola:
            self.cola_choferes_disponibles = Cola()
            self.cola_choferes_descanso = Cola()
            self.cola_buses = Cola()
        self.asientos = []
        self.historial = []
        self.pasajeros = []

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

        tk.Label(self.root, text="Sistema Logístico Civa\nTransporte Interprovincial",
                 font=("Arial", 14, "bold"),
                 bg=self.color_fondo, fg=self.color_texto).pack(pady=10)

        self.crear_pestañas()
        self.area_principal = tk.Frame(self.root, bg=self.color_pestaña, width=900, height=550)
        self.area_principal.pack(pady=10)
        self.area_principal.pack_propagate(False)

        self.cargar_pantalla_inicio()
        self.cargar_datos_prueba()

    def crear_pestañas(self):
        frame_tabs = tk.Frame(self.root, bg=self.color_fondo)
        frame_tabs.pack()
        pestañas = [
            ("Inicio", self.cargar_pantalla_inicio),
            ("Rutas", self.cargar_pantalla_rutas),
            ("Buses", self.cargar_pantalla_buses),
            ("Choferes", self.cargar_pantalla_choferes),
            ("Asientos", self.cargar_pantalla_asientos),
            ("👤 Pasajeros", self.cargar_pantalla_pasajeros),
            ("Reportes", self.cargar_pantalla_reportes),
            ("Historial", self.cargar_pantalla_historial)
        ]
        for i, (nombre, funcion) in enumerate(pestañas):
            btn = tk.Button(frame_tabs, text=nombre, font=("Arial", 11),
                            bg=self.color_pestaña, fg=self.color_texto,
                            padx=15, pady=5, relief="flat",
                            command=lambda f=funcion: f())
            btn.grid(row=0, column=i, padx=2)

    def limpiar_area_principal(self):
        for widget in self.area_principal.winfo_children():
            widget.destroy()

    def cargar_pantalla_inicio(self):
        self.limpiar_area_principal()
        carpeta_actual = os.path.dirname(__file__)
        ruta_imagen = os.path.join(carpeta_actual, "assets", "fondo.jpg")
        if os.path.exists(ruta_imagen):
            from PIL import Image, ImageTk
            img = Image.open(ruta_imagen)
            img = img.resize((900, 550), Image.Resampling.LANCZOS)
            self.fondo = ImageTk.PhotoImage(img)
            tk.Label(self.area_principal, image=self.fondo).pack()
        else:
            tk.Label(self.area_principal, text="📸 Coloca tu imagen en assets/fondo.jpg",
                     font=("Arial", 18), bg=self.color_pestaña, fg="white").pack(pady=50)
        tk.Label(self.area_principal, text="SISTEMA LOGÍSTICO CIVA",
                 font=("Arial", 36, "bold"), fg="white", bg="#000000").place(relx=0.5, rely=0.4, anchor="center")
        tk.Label(self.area_principal, text="Gestión Integral de Transporte Interprovincial",
                 font=("Arial", 16), fg="white", bg="#000000").place(relx=0.5, rely=0.52, anchor="center")

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
        frame_asientos.pack(side="left", padx=10)
        tk.Label(frame_asientos, text="Estado de asientos:", fg="white", bg=self.color_pestaña,
                 font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=4, pady=5)
        self.botones_asientos = {}
        fila = 1
        columna = 0
        for asiento in self.asientos:
            color = "#2ecc71" if asiento.estado == "libre" else "#e74c3c"
            texto = f"{asiento.numero:02d}"
            btn = tk.Button(frame_asientos, text=texto, width=5, height=2,
                            bg=color, fg="white", font=("Arial", 9, "bold"),
                            command=lambda n=asiento.numero: self.seleccionar_asiento(n, num_entry))
            btn.grid(row=fila, column=columna, padx=2, pady=2)
            self.botones_asientos[asiento.numero] = btn
            columna += 1
            if columna >= 4:
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
                 font=("Arial", 20, "bold"), fg="white", bg=self.color_pestaña).pack(pady=15)

        frame_form = tk.Frame(self.area_principal, bg=self.color_pestaña)
        frame_form.pack(pady=10)

        tk.Label(frame_form, text="DNI:", fg="white", bg=self.color_pestaña, font=("Arial", 11)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        entrada_dni = tk.Entry(frame_form, font=("Arial", 11), width=15)
        entrada_dni.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_form, text="Nombre Completo:", fg="white", bg=self.color_pestaña, font=("Arial", 11)).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        entrada_nombre = tk.Entry(frame_form, font=("Arial", 11), width=30)
        entrada_nombre.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(frame_form, text="Teléfono:", fg="white", bg=self.color_pestaña, font=("Arial", 11)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        entrada_telefono = tk.Entry(frame_form, font=("Arial", 11), width=15)
        entrada_telefono.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame_form, text="Destino:", fg="white", bg=self.color_pestaña, font=("Arial", 11)).grid(row=1, column=2, padx=5, pady=5, sticky="e")
        destino_var = tk.StringVar()
        destino_var.set("Arequipa")
        combo_destino = ttk.Combobox(frame_form, textvariable=destino_var, values=self.ciudades, state="readonly", font=("Arial", 11), width=25)
        combo_destino.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(frame_form, text="N° Asiento:", fg="white", bg=self.color_pestaña, font=("Arial", 11)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        entrada_asiento = tk.Entry(frame_form, font=("Arial", 11), width=15)
        entrada_asiento.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.area_principal, text="📋 Lista de Pasajeros Registrados",
                 font=("Arial", 12, "bold"), fg="white", bg=self.color_pestaña).pack(pady=(15,5))

        caja_lista = tk.Text(self.area_principal, width=95, height=12, font=("Arial", 10))
        caja_lista.pack(pady=5)

        def actualizar_lista():
            caja_lista.delete("1.0", tk.END)
            if not self.pasajeros:
                caja_lista.insert(tk.END, "⚠️ No hay pasajeros registrados aún.\n")
                caja_lista.insert(tk.END, "👉 Registra un pasajero arriba y aparecerá aquí.\n")
            else:
                caja_lista.insert(tk.END, f"{'DNI':<12} {'NOMBRE':<30} {'ASIENTO':<10} {'DESTINO':<15} {'TELÉFONO'}\n")
                caja_lista.insert(tk.END, "-"*80 + "\n")
                for p in self.pasajeros:
                    caja_lista.insert(tk.END, f"{p.dni:<12} {p.nombre:<30} {p.asiento:<10} {p.destino:<15} {p.telefono}\n")

        def registrar_pasajero():
            dni = entrada_dni.get().strip()
            nombre = entrada_nombre.get().strip()
            telefono = entrada_telefono.get().strip()
            destino = destino_var.get()

            if not dni or not nombre:
                messagebox.showwarning("Aviso", "El DNI y Nombre son obligatorios")
                return
            if not dni.isdigit() or len(dni) != 8:
                messagebox.showwarning("Aviso", "El DNI debe tener 8 dígitos")
                return
            if not entrada_asiento.get().strip().isdigit():
                messagebox.showwarning("Aviso", "Escribe un número de asiento válido")
                return

            asiento = int(entrada_asiento.get().strip())

            for p in self.pasajeros:
                if p.dni == dni:
                    messagebox.showwarning("Aviso", f"Ya existe un pasajero con DNI: {dni}")
                    return

            pasajero = Pasajero(dni, nombre, telefono, destino, asiento)
            self.pasajeros.append(pasajero)
            self.historial.append(f"👤 Pasajero registrado: {nombre} | DNI: {dni} | Asiento {asiento} → {destino}")

            entrada_dni.delete(0, tk.END)
            entrada_nombre.delete(0, tk.END)
            entrada_telefono.delete(0, tk.END)
            entrada_asiento.delete(0, tk.END)

            messagebox.showinfo("✅ Éxito", f"Pasajero registrado:\n{nombre}\nDNI: {dni}")
            actualizar_lista()

        def buscar_por_dni():
            dni = entrada_dni.get().strip()
            if not dni:
                messagebox.showinfo("🔍 Buscar Pasajero", "Escribe un DNI para buscar")
                return
            encontrado = None
            for p in self.pasajeros:
                if p.dni == dni:
                    encontrado = p
                    break
            if encontrado:
                entrada_nombre.delete(0, tk.END)
                entrada_nombre.insert(0, encontrado.nombre)
                entrada_telefono.delete(0, tk.END)
                entrada_telefono.insert(0, encontrado.telefono)
                entrada_asiento.delete(0, tk.END)
                entrada_asiento.insert(0, str(encontrado.asiento))
                messagebox.showinfo("✅ Encontrado", 
                    f"Nombre: {encontrado.nombre}\nDestino: {encontrado.destino}\nAsiento: {encontrado.asiento}")
            else:
                messagebox.showinfo("🔍 Resultado", f"No se encontró pasajero con DNI: {dni}")

        def eliminar_pasajero():
            dni = entrada_dni.get().strip()
            if not dni:
                messagebox.showwarning("Aviso", "Escribe el DNI del pasajero a eliminar")
                return
            for i, p in enumerate(self.pasajeros):
                if p.dni == dni:
                    nombre = p.nombre
                    del self.pasajeros[i]
                    self.historial.append(f"🗑️ Pasajero eliminado: {nombre} | DNI: {dni}")
                    messagebox.showinfo("✅ Eliminado", f"Pasajero {nombre} eliminado correctamente")
                    entrada_dni.delete(0, tk.END)
                    entrada_nombre.delete(0, tk.END)
                    entrada_telefono.delete(0, tk.END)
                    entrada_asiento.delete(0, tk.END)
                    actualizar_lista()
                    return
            messagebox.showinfo("Aviso", "Pasajero no encontrado")

        frame_botones = tk.Frame(self.area_principal, bg=self.color_pestaña)
        frame_botones.pack(pady=10)

        tk.Button(frame_botones, text="✅ Registrar Pasajero", command=registrar_pasajero,
                  bg="#2ecc71", fg="white", font=("Arial", 11, "bold"), padx=20, pady=8).grid(row=0, column=0, padx=10)
        tk.Button(frame_botones, text="🔍 Buscar por DNI", command=buscar_por_dni,
                  bg="#3498db", fg="white", font=("Arial", 11), padx=20, pady=8).grid(row=0, column=1, padx=10)
        tk.Button(frame_botones, text="🗑️ Eliminar", command=eliminar_pasajero,
                  bg="#e74c3c", fg="white", font=("Arial", 11), padx=20, pady=8).grid(row=0, column=2, padx=10)

        actualizar_lista()

    def cargar_pantalla_reportes(self):
        self.limpiar_area_principal()
        tk.Label(self.area_principal, text="📊 REPORTES DEL SISTEMA",
                 font=("Arial", 20, "bold"), fg="white", bg=self.color_pestaña).pack(pady=20)
        
        buses_cant = self.cola_buses.tamaño() if (Cola and hasattr(self.cola_buses, 'tamaño')) else 'N/A'
        chof_disp = self.cola_choferes_disponibles.tamaño() if (Cola and hasattr(self.cola_choferes_disponibles, 'tamaño')) else 'N/A'
        chof_desc = self.cola_choferes_descanso.tamaño() if (Cola and hasattr(self.cola_choferes_descanso, 'tamaño')) else 'N/A'

        texto = f"""
        🚌 Buses registrados:     {buses_cant}
        👨‍✈️ Choferes disponibles:  {chof_disp}
        🛌 Choferes en descanso:   {chof_desc}
        💺 Asientos totales:       {len(self.asientos)}
        👤 Pasajeros registrados:  {len(self.pasajeros)}
        📋 Operaciones registradas: {len(self.historial)}
        """
        tk.Label(self.area_principal, text=texto, font=("Arial", 14),
                 fg="white", bg=self.color_pestaña, justify="left").pack(pady=20)

    def cargar_pantalla_historial(self):
        self.limpiar_area_principal()
        tk.Label(self.area_principal, text="📜 HISTORIAL DE OPERACIONES",
                 font=("Arial", 20, "bold"), fg="white", bg=self.color_pestaña).pack(pady=10)
        tk.Button(self.area_principal, text="🗑️ Borrar Historial Completo",
                  command=self.borrar_historial,
                  bg="#e74c3c", fg="white", font=("Arial", 11, "bold"),
                  padx=20, pady=6).pack(pady=5)
        caja = tk.Text(self.area_principal, width=90, height=16, font=("Arial", 10), bg="#0a1929", fg="white")
        caja.pack(pady=10)
        self.caja_historial = caja
        if not self.historial:
            caja.insert(tk.END, "- Sistema iniciado correctamente\n")
            caja.insert(tk.END, "- Estructuras de datos cargadas\n")
            caja.insert(tk.END, "- Algoritmo de Rutas listo\n")
            caja.insert(tk.END, "- Módulo de Pasajeros activo\n")
            caja.insert(tk.END, "\n👉 Realiza acciones y se registrarán aquí automáticamente...\n")
        else:
            caja.insert(tk.END, f"--- {len(self.historial)} operaciones registradas ---\n\n")
            for linea in self.historial:
                caja.insert(tk.END, linea + "\n")
        caja.config(state="disabled")

    def borrar_historial(self):
        self.historial.clear()
        messagebox.showinfo("✅", "Historial eliminado correctamente")
        self.cargar_pantalla_historial()

    def cargar_datos_prueba(self):
        if not Cola or not Chofer or not Bus or not registrar_bus:
            return
        chofer1 = Chofer("72345678", "Carlos Perez", "A1")
        chofer2 = Chofer("71234567", "Ana Ruiz", "A2")
        self.cola_choferes_disponibles.encolar(chofer1)
        self.cola_choferes_disponibles.encolar(chofer2)
        bus1 = Bus("BUS001", "ABC-123", 40, "economico")
        bus2 = Bus("BUS002", "DEF-456", 50, "premium")
        registrar_bus(self.cola_buses, bus1)
        registrar_bus(self.cola_buses, bus2)
        self.historial.append("✅ Datos de prueba cargados: 2 choferes, 2 buses")

    def ejecutar(self):
        self.root.mainloop()


# ==============================================
# INICIO DEL PROGRAMA
# ==============================================

if __name__ == "__main__":
    def iniciar_sistema():
        app = SistemaLogisticoCiva()
        app.ejecutar()

    mostrar_pantalla_login(iniciar_sistema)