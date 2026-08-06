import streamlit as st
import pandas as pd
from datetime import datetime
import random

# ==============================================
# CONFIGURACIÓN DE LA PÁGINA
# ==============================================

st.set_page_config(
    page_title="Sistema Logístico Civa",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================
# BASE DE DATOS DE PRUEBA
# ==============================================

# Inicializar session_state para persistencia de datos
if 'pasajeros' not in st.session_state:
    st.session_state.pasajeros = []

if 'historial' not in st.session_state:
    st.session_state.historial = []

# ==============================================
# FUNCIONES DE AYUDA
# ==============================================

def generar_boleta(pasajero):
    """Genera el contenido del boleto"""
    num_boleta = f"B-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    return f"""
╔══════════════════════════════════════════════╗
║                                              ║
║              🚌 CIVA TRANSPORTES              ║
║                                              ║
╠══════════════════════════════════════════════╣
║                                              ║
║  🎫 BOLETO N°: {num_boleta}                    ║
║                                              ║
║  👤 PASAJERO: {pasajero['nombre']}            ║
║  📋 DNI: {pasajero['dni']}                    ║
║  📞 TELÉFONO: {pasajero.get('telefono', 'No registrado')} ║
║                                              ║
║  🚌 ORIGEN: Lima                              ║
║  🏁 DESTINO: {pasajero.get('destino', 'No especificado')} ║
║  💺 ASIENTO: {pasajero.get('asiento', 'No asignado')} ║
║  📅 FECHA: {fecha}                            ║
║                                              ║
╠══════════════════════════════════════════════╣
║                                              ║
║  ✨ ¡GRACIAS POR VIAJAR CON NOSOTROS! ✨    ║
║                                              ║
║  📌 Presenta este boleto al abordar          ║
║  ⏰ Llegar con 30 minutos de anticipación   ║
║                                              ║
╚══════════════════════════════════════════════╝
"""

# ==============================================
# MENÚ LATERAL
# ==============================================

st.sidebar.image("https://img.icons8.com/color/96/000000/bus.png", width=80)
st.sidebar.title("🚌 Sistema Civa")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "📋 MENÚ PRINCIPAL",
    ["🏠 Inicio", "👤 Pasajeros", "🎫 Boletos", "🧾 Facturas", "📊 Reportes"]
)

# ==============================================
# PÁGINA DE INICIO
# ==============================================

if menu == "🏠 Inicio":
    st.title("🚌 SISTEMA LOGÍSTICO CIVA")
    st.markdown("### Gestión Integral de Transporte Interprovincial")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Pasajeros", len(st.session_state.pasajeros))
    with col2:
        st.metric("🚌 Buses", 5)
    with col3:
        st.metric("👨‍✈️ Choferes", 8)
    with col4:
        st.metric("📊 Operaciones", len(st.session_state.historial))
    
    st.markdown("---")
    st.markdown("""
    ### 🎯 Funcionalidades del Sistema
    
    | Módulo | Descripción |
    |--------|-------------|
    | 👤 **Pasajeros** | Registro, búsqueda y gestión de pasajeros |
    | 🎫 **Boletos** | Generación de boletos de viaje |
    | 🧾 **Facturas** | Facturación electrónica con IGV |
    | 📊 **Reportes** | Estadísticas y reportes del sistema |
    """)
    
    if st.session_state.historial:
        with st.expander("📜 Últimas operaciones"):
            for h in st.session_state.historial[-5:]:
                st.write(f"• {h}")

# ==============================================
# PÁGINA DE PASAJEROS
# ==============================================

elif menu == "👤 Pasajeros":
    st.title("👤 REGISTRO DE PASAJEROS")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📝 Registrar", "📋 Lista"])
    
    with tab1:
        with st.form("form_registro_pasajero"):
            col1, col2 = st.columns(2)
            
            with col1:
                dni = st.text_input("DNI", max_chars=8, placeholder="8 dígitos")
                nombre = st.text_input("Nombre Completo", placeholder="Ej: Juan Perez")
            
            with col2:
                telefono = st.text_input("Teléfono", placeholder="Ej: 987654321")
                destino = st.selectbox("Destino", ["Lima", "Huaral", "Ica", "Nazca", "Arequipa", "Trujillo", "Chiclayo"])
            
            asiento = st.number_input("N° Asiento", min_value=1, max_value=40, step=1)
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
            with col_btn1:
                submitted = st.form_submit_button("✅ Registrar Pasajero", type="primary", use_container_width=True)
            
            if submitted:
                if len(dni) != 8:
                    st.error("❌ El DNI debe tener 8 dígitos")
                elif not nombre:
                    st.error("❌ El nombre es obligatorio")
                else:
                    # Verificar duplicado
                    for p in st.session_state.pasajeros:
                        if p["dni"] == dni:
                            st.error("❌ Ese DNI ya está registrado")
                            st.stop()
                    
                    pasajero = {
                        "dni": dni,
                        "nombre": nombre,
                        "telefono": telefono,
                        "destino": destino,
                        "asiento": asiento,
                        "fecha_registro": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }
                    
                    st.session_state.pasajeros.append(pasajero)
                    st.session_state.historial.append(f"✅ Pasajero registrado: {nombre} (DNI: {dni})")
                    st.success(f"✅ Pasajero {nombre} registrado correctamente")
                    st.balloons()
    
    with tab2:
        if st.session_state.pasajeros:
            df = pd.DataFrame(st.session_state.pasajeros)
            st.dataframe(df, use_container_width=True, height=400)
            
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Exportar a CSV",
                    data=csv,
                    file_name=f"pasajeros_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            with col_exp2:
                # Buscar pasajero
                dni_buscar = st.text_input("🔍 Buscar por DNI", max_chars=8)
                if dni_buscar:
                    encontrado = False
                    for p in st.session_state.pasajeros:
                        if p["dni"] == dni_buscar:
                            st.success(f"✅ Pasajero encontrado: {p['nombre']}")
                            encontrado = True
                            break
                    if not encontrado:
                        st.warning("⚠️ Pasajero no encontrado")
        else:
            st.info("ℹ️ No hay pasajeros registrados aún")

# ==============================================
# PÁGINA DE BOLETOS
# ==============================================

elif menu == "🎫 Boletos":
    st.title("🎫 GENERAR BOLETO")
    st.markdown("---")
    
    if not st.session_state.pasajeros:
        st.warning("⚠️ Primero registra un pasajero en la sección 'Pasajeros'")
        st.stop()
    
    # Seleccionar pasajero
    opciones = [f"{p['dni']} - {p['nombre']}" for p in st.session_state.pasajeros]
    seleccion = st.selectbox("Selecciona un pasajero", opciones)
    
    # Obtener el DNI del seleccionado
    dni_seleccionado = seleccion.split(" - ")[0]
    
    # Buscar el pasajero
    pasajero_seleccionado = None
    for p in st.session_state.pasajeros:
        if p["dni"] == dni_seleccionado:
            pasajero_seleccionado = p
            break
    
    if pasajero_seleccionado:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📋 Datos del Pasajero")
            st.write(f"**Nombre:** {pasajero_seleccionado['nombre']}")
            st.write(f"**DNI:** {pasajero_seleccionado['dni']}")
            st.write(f"**Destino:** {pasajero_seleccionado.get('destino', 'No especificado')}")
            st.write(f"**Asiento:** {pasajero_seleccionado.get('asiento', 'No asignado')}")
            
            if st.button("🎫 Generar Boleto", type="primary", use_container_width=True):
                st.session_state.historial.append(f"🎫 Boleto generado para {pasajero_seleccionado['nombre']}")
                
                with col2:
                    st.subheader("🎫 BOLETO DE VIAJE")
                    st.text(generar_boleta(pasajero_seleccionado))
                    
                    # Botón para descargar
                    st.download_button(
                        label="💾 Descargar Boleto",
                        data=generar_boleta(pasajero_seleccionado),
                        file_name=f"boleto_{pasajero_seleccionado['dni']}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                        mime="text/plain"
                    )
        
        with col2:
            st.subheader("🖨️ Opciones de Impresión")
            st.info("💡 Haz clic en 'Generar Boleto' para ver el boleto")
            
            st.markdown("""
            ### 📌 Instrucciones para imprimir:
            1. Haz clic en **"Generar Boleto"**
            2. Copia el contenido del boleto
            3. Pégalo en un editor de texto
            4. Imprime desde el editor
            """)

# ==============================================
# PÁGINA DE FACTURAS
# ==============================================

elif menu == "🧾 Facturas":
    st.title("🧾 GENERAR FACTURA")
    st.markdown("---")
    
    if not st.session_state.pasajeros:
        st.warning("⚠️ Primero registra un pasajero en la sección 'Pasajeros'")
        st.stop()
    
    # Seleccionar pasajero
    opciones = [f"{p['dni']} - {p['nombre']}" for p in st.session_state.pasajeros]
    seleccion = st.selectbox("Selecciona un pasajero", opciones)
    
    dni_seleccionado = seleccion.split(" - ")[0]
    
    pasajero_seleccionado = None
    for p in st.session_state.pasajeros:
        if p["dni"] == dni_seleccionado:
            pasajero_seleccionado = p
            break
    
    if pasajero_seleccionado:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📋 Datos del Pasajero")
            st.write(f"**Nombre:** {pasajero_seleccionado['nombre']}")
            st.write(f"**DNI:** {pasajero_seleccionado['dni']}")
            
            servicio = st.radio("Tipo de Servicio", ["Económico", "Premium"])
            metodo_pago = st.selectbox("Método de Pago", ["Efectivo", "Tarjeta", "Yape", "Plin", "Transferencia"])
            
            # Cálculo de precios
            precios = {
                "Lima": 0, "Huaral": 45, "Ica": 65, "Nazca": 85,
                "Arequipa": 120, "Trujillo": 95, "Chiclayo": 110
            }
            
            destino = pasajero_seleccionado.get('destino', 'Lima')
            precio_base = precios.get(destino, 50)
            if servicio == "Premium":
                precio_base = precio_base * 1.3
            subtotal = precio_base
            igv = subtotal * 0.18
            total = subtotal + igv
            
            if st.button("🧾 Generar Factura", type="primary", use_container_width=True):
                st.session_state.historial.append(f"🧾 Factura generada para {pasajero_seleccionado['nombre']}")
                
                with col2:
                    st.subheader("🧾 FACTURA ELECTRÓNICA")
                    st.markdown(f"""
                    **CIVA TRANSPORTES S.A.C.**  
                    RUC: 20567890123  
                    Av. Colonial 123, Lima - Perú  
                    Tel: (01) 555-1234  
                    
                    **N° FACTURA:** F001-{random.randint(100000, 999999)}  
                    **FECHA:** {datetime.now().strftime('%d/%m/%Y %H:%M')}  
                    
                    ---
                    
                    **📋 CLIENTE**  
                    {pasajero_seleccionado['nombre']}  
                    DNI: {pasajero_seleccionado['dni']}  
                    
                    **🚌 VIAJE**  
                    Lima → {destino}  
                    Servicio: {servicio}  
                    
                    ---
                    
                    **💰 DETALLE DE PAGO**  
                    
                    | Descripción | Cant | P.Unit | Subtotal |
                    |-------------|------|--------|----------|
                    | Pasaje Lima → {destino} | 1 | S/{precio_base:.2f} | S/{subtotal:.2f} |
                    
                    **SUBTOTAL: S/{subtotal:.2f}**  
                    **IGV (18%): S/{igv:.2f}**  
                    **TOTAL: S/{total:.2f}**  
                    
                    **MÉTODO DE PAGO:** {metodo_pago}  
                    
                    ---
                    ✨ ¡GRACIAS POR VIAJAR CON NOSOTROS! ✨
                    """)
                    
                    # Botón para descargar
                    factura_texto = f"""
                    FACTURA ELECTRÓNICA
                    CIVA TRANSPORTES S.A.C.
                    RUC: 20567890123
                    Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}
                    
                    CLIENTE: {pasajero_seleccionado['nombre']}
                    DNI: {pasajero_seleccionado['dni']}
                    
                    VIAJE: Lima → {destino}
                    SERVICIO: {servicio}
                    
                    SUBTOTAL: S/{subtotal:.2f}
                    IGV (18%): S/{igv:.2f}
                    TOTAL: S/{total:.2f}
                    
                    MÉTODO DE PAGO: {metodo_pago}
                    """
                    
                    st.download_button(
                        label="💾 Descargar Factura",
                        data=factura_texto,
                        file_name=f"factura_{pasajero_seleccionado['dni']}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                        mime="text/plain"
                    )

# ==============================================
# PÁGINA DE REPORTES
# ==============================================

elif menu == "📊 Reportes":
    st.title("📊 REPORTES Y ESTADÍSTICAS")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Pasajeros", len(st.session_state.pasajeros))
    with col2:
        st.metric("🎫 Boletos", len([h for h in st.session_state.historial if "boleto" in h.lower()]))
    with col3:
        st.metric("🧾 Facturas", len([h for h in st.session_state.historial if "factura" in h.lower()]))
    with col4:
        st.metric("📊 Operaciones", len(st.session_state.historial))
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📋 Lista de Pasajeros", "📜 Historial"])
    
    with tab1:
        if st.session_state.pasajeros:
            df = pd.DataFrame(st.session_state.pasajeros)
            st.dataframe(df, use_container_width=True, height=400)
            
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Exportar CSV",
                    data=csv,
                    file_name=f"reporte_pasajeros_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("ℹ️ No hay pasajeros registrados")
    
    with tab2:
        if st.session_state.historial:
            for i, h in enumerate(reversed(st.session_state.historial), 1):
                st.write(f"{i}. {h}")
        else:
            st.info("ℹ️ No hay registros en el historial")

# ==============================================
# PIE DE PÁGINA
# ==============================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 10px;">
    <b>Sistema Logístico Civa</b> | Desarrollado con ❤️ | v2.0
</div>
""", unsafe_allow_html=True)