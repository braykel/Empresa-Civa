import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from estructuras.cola import Cola
from modelos.chofer import Chofer
from modelos.bus import Bus
from modelos.ruta import Ruta
from modelos.asiento import Asiento
from algoritmos.asignacion_choferes import asignar_chofer, enviar_a_descanso, liberar_de_descanso
from algoritmos.asignacion_buses import registrar_bus, asignar_bus
from algoritmos.dijkstra import calcular_ruta_mas_corta


class SistemaLogisticoCiva:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Logístico Civa - Transporte Interprovincial")
        self.root.geometry("1000x700")

        self.color_fondo = "#1a1a2e"
        self.color_pestaña = "#16213e"
        self.color_texto = "#ffffff"
        self.root.configure(bg=self.color_fondo)

        self.cola_choferes_disponibles = Cola()
        self.cola_choferes_descanso = Cola()
        self.cola_buses = Cola()
        self.asientos = []
        self.historial = []

        # Lista de ciudades disponibles
        self.ciudades = ["Lima", "Ica", "Nazca", "Arequipa", "Trujillo", "Chiclayo"]

        self.grafo_rutas = {
            "Lima": [("Ica", 306), ("Trujillo", 555)],
            "Ica": [("Lima", 306), ("Nazca", 210)],
            "Nazca": [("Ica", 210), ("Arequipa", 450)],
            "Trujillo": [("Lima", 555), ("Chiclayo", 208)],
            "Chiclayo": [("Trujillo", 208)],
            "Arequipa": [("Nazca", 450)]
        }

        tk.Label(root, text="Sistema Logístico Civa\nTransporte Interprovincial",
                 font=("Arial", 14, "bold"),
                 bg=self.color_fondo, fg=self.color_texto).pack(pady=10)

        self.crear_pestañas()
        self.area_principal = tk.Frame(root, bg=self.color_pestaña, width=900, height=550)
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
            ("Reportes", self.cargar_pantalla_reportes),
            ("Historial", self.cargar_pantalla_historial)
        ]
        for i, (nombre, funcion) in enumerate(pestañas):
            btn = tk.Button(frame_tabs, text=nombre, font=("Arial", 11),
                            bg=self.color_pestaña, fg=self.color_texto,
                            padx=20, pady=5, relief="flat",
                            command=lambda f=funcion: f())
            btn.grid(row=0, column=i, padx=2)

    def limpiar_area_principal(self):
        for widget in self.area_principal.winfo_children():
            widget.destroy()

    def cargar_pantalla_inicio(self):
        self.limpiar_area_principal()
        ruta_imagen = os.path.join(os.path.dirname(__file__), "..", "assets", "fondo.jpg")
        if os.path.exists(ruta_imagen):
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
            lista.insert(tk.END, "=== Buses Registrados ===\n")
            temp = Cola()
            while not self.cola_buses.esta_vacia():
                bus = self.cola_buses.desencolar()
                lista.insert(tk.END, f"{bus.codigo} | {bus.placa} | {bus.tipo_servicio} | {bus.estado}\n")
                temp.encolar(bus)
            while not temp.esta_vacia():
                self.cola_buses.encolar(temp.desencolar())
        def registrar():
            bus = Bus(cod_entry.get(), placa_entry.get(), int(cap_entry.get()), servicio_var.get())
            registrar_bus(self.cola_buses, bus)
            self.historial.append(f"✅ Bus registrado: {bus.codigo} | Placa: {bus.placa}")
            messagebox.showinfo("✅", f"Bus {bus.codigo} registrado")
            actualizar_lista()
        def asignar():
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
            chofer = Chofer(dni_entry.get(), nom_entry.get(), licencia_var.get())
            self.cola_choferes_disponibles.encolar(chofer)
            self.historial.append(f"✅ Chofer registrado: {chofer.nombre} | DNI: {chofer.dni}")
            messagebox.showinfo("✅", f"Chofer {chofer.nombre} registrado")
        def asignar():
            ultimo[0] = asignar_chofer(self.cola_choferes_disponibles)
            if ultimo[0]:
                resultado.config(text=f"✅ Asignado: {ultimo[0].nombre} | Estado: {ultimo[0].estado}")
                self.historial.append(f"✅ Chofer asignado: {ultimo[0].nombre}")
            else:
                resultado.config(text="❌ No hay choferes disponibles")
                self.historial.append("⚠️ Intento asignar chofer: sin disponibilidad")
        def descansar():
            if ultimo[0]:
                enviar_a_descanso(ultimo[0], self.cola_choferes_descanso)
                self.historial.append(f"🛌 Chofer en descanso: {ultimo[0].nombre}")
                resultado.config(text=f"🛌 {ultimo[0].nombre} enviado a descanso")
                ultimo[0] = None
        def liberar():
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
        if not self.asientos:
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

    def cargar_pantalla_reportes(self):
        self.limpiar_area_principal()
        tk.Label(self.area_principal, text="📊 REPORTES DEL SISTEMA",
                 font=("Arial", 20, "bold"), fg="white", bg=self.color_pestaña).pack(pady=20)
        texto = f"""
        🚌 Buses disponibles: {len(self.cola_buses)}
        👨‍✈️ Choferes disponibles: {len(self.cola_choferes_disponibles)}
        🛌 Choferes en descanso: {len(self.cola_choferes_descanso)}
        💺 Asientos totales: {len(self.asientos)}
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
            caja.insert(tk.END, "- Algoritmo de Dijkstra listo\n")
            caja.insert(tk.END, "- Colas de asignación activas\n")
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
        chofer1 = Chofer("72345678", "Carlos Perez", "A1")
        chofer2 = Chofer("71234567", "Ana Ruiz", "A2")
        self.cola_choferes_disponibles.encolar(chofer1)
        self.cola_choferes_disponibles.encolar(chofer2)
        bus1 = Bus("BUS001", "ABC-123", 40, "economico")
        bus2 = Bus("BUS002", "DEF-456", 50, "premium")
        registrar_bus(self.cola_buses, bus1)
        registrar_bus(self.cola_buses, bus2)
        self.historial.append("✅ Datos de prueba cargados: 2 choferes, 2 buses")


if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaLogisticoCiva(root)
    root.mainloop()