class Cola:
    def __init__(self):
        self._elementos = []

    def esta_vacia(self):
        return len(self._elementos) == 0

    def encolar(self, item):
        self._elementos.append(item)

    def desencolar(self):
        if not self.esta_vacia():
            return self._elementos.pop(0)
        return None

    def ver_primero(self):
        if not self.esta_vacia():
            return self._elementos[0]
        return None

    def __len__(self):
        return len(self._elementos)