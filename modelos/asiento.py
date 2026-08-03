class Asiento:
    def __init__(self, numero, precio):
        self.numero = numero
        self.precio = precio
        self.estado = "libre"  # libre / reservado / ocupado

    def reservar(self):
        if self.estado == "libre":
            self.estado = "reservado"
            return True
        return False

    def liberar(self):
        self.estado = "libre"

    def __str__(self):
        return f"Asiento {self.numero}: {self.estado} | S/ {self.precio}"