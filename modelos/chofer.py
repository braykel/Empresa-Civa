class Chofer:
    def __init__(self, dni, nombre, licencia):
        self.dni = dni
        self.nombre = nombre
        self.licencia = licencia
        self.estado = "disponible"  # disponible / en_viaje / descansando
        self.horas_conducidas = 0

    def __str__(self):
        return f"{self.nombre} | DNI: {self.dni} | Estado: {self.estado}"