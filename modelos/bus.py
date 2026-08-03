class Bus:
    def __init__(self, codigo, placa, capacidad, tipo_servicio):
        self.codigo = codigo
        self.placa = placa
        self.capacidad = capacidad
        self.tipo_servicio = tipo_servicio  # economico / premium / vip
        self.estado = "disponible"  # disponible / en_ruta / mantenimiento

    def __str__(self):
        return f"Bus {self.codigo} | Placa: {self.placa} | Tipo: {self.tipo_servicio} | Estado: {self.estado}"