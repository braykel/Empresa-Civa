from estructuras.cola import Cola
from modelos.bus import Bus

def registrar_bus(cola_buses: Cola, bus: Bus):
    cola_buses.encolar(bus)
    print(f"🚌 Registrado: {bus.codigo} - {bus.placa}")

def asignar_bus(cola_buses: Cola, tipo_servicio_requerido):
    """Asigna un bus que coincida con el tipo de servicio necesario"""
    cola_temporal = Cola()
    bus_asignado = None

    while not cola_buses.esta_vacia():
        bus = cola_buses.desencolar()
        if bus.tipo_servicio == tipo_servicio_requerido and bus.estado == "disponible" and bus_asignado is None:
            bus.estado = "en_ruta"
            bus_asignado = bus
            print(f"✅ Bus asignado: {bus.codigo} para servicio {tipo_servicio_requerido}")
        else:
            cola_temporal.encolar(bus)

    # Volvemos a guardar los buses restantes
    while not cola_temporal.esta_vacia():
        cola_buses.encolar(cola_temporal.desencolar())

    if not bus_asignado:
        print(f"❌ No hay buses disponibles para servicio {tipo_servicio_requerido}")
    return bus_asignado