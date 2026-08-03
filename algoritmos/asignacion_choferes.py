from estructuras.cola import Cola
from modelos.chofer import Chofer

def asignar_chofer(cola_choferes: Cola):
    """Asigna el primer chofer disponible de la cola"""
    if cola_choferes.esta_vacia():
        print("❌ No hay choferes disponibles")
        return None
    
    chofer = cola_choferes.desencolar()
    chofer.estado = "en_viaje"
    print(f"✅ Asignado: {chofer.nombre}")
    return chofer

def enviar_a_descanso(chofer: Chofer, cola_descanso: Cola):
    """Envía un chofer al descanso después de su turno"""
    chofer.estado = "descansando"
    cola_descanso.encolar(chofer)
    print(f"🛌 {chofer.nombre} enviado a descanso")

def liberar_de_descanso(cola_descanso: Cola, cola_disponibles: Cola):
    """Libera al primer chofer de la cola de descanso"""
    if cola_descanso.esta_vacia():
        print("❌ No hay choferes en descanso")
        return None
    
    chofer = cola_descanso.desencolar()
    chofer.estado = "disponible"
    chofer.horas_conducidas = 0
    cola_disponibles.encolar(chofer)
    print(f"🔄 {chofer.nombre} vuelve a estar disponible")
    return chofer