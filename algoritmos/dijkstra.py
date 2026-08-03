import heapq

def calcular_ruta_mas_corta(grafo, origen, destino):
    """
    Grafo ejemplo: {'Lima': [('Trujillo', 555), ('Ica', 306)], ...}
    Devuelve la ruta y la distancia total
    """
    distancias = {nodo: float('inf') for nodo in grafo}
    distancias[origen] = 0
    camino = {origen: None}
    cola_prioridad = [(0, origen)]

    while cola_prioridad:
        distancia_actual, nodo_actual = heapq.heappop(cola_prioridad)
        
        if nodo_actual == destino:
            break
        if distancia_actual > distancias[nodo_actual]:
            continue

        for vecino, peso in grafo[nodo_actual]:
            distancia = distancia_actual + peso
            if distancia < distancias[vecino]:
                distancias[vecino] = distancia
                camino[vecino] = nodo_actual
                heapq.heappush(cola_prioridad, (distancia, vecino))

    # Reconstruir el camino
    ruta_final = []
    nodo = destino
    while nodo is not None:
        ruta_final.insert(0, nodo)
        nodo = camino[nodo]

    return ruta_final, distancias[destino]