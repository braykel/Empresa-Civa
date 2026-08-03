class Ruta:
    def __init__(self, codigo, origen, destino, distancia_km, tiempo_horas):
        self.codigo = codigo
        self.origen = origen
        self.destino = destino
        self.distancia = distancia_km
        self.tiempo = tiempo_horas

    def __str__(self):
        return f"{self.codigo}: {self.origen} → {self.destino} | {self.distancia}km | {self.tiempo}h"