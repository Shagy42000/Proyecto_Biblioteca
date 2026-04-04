class Libro:
    def __init__(self, id, titulo, autor, cantidad):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.cantidad = cantidad

    def get_id(self):
        return self.id

    def get_titulo(self):
        return self.titulo

    def get_autor(self):
        return self.autor

    def get_cantidad(self):
        return self.cantidad

    def set_cantidad(self, cantidad):
        self.cantidad = cantidad

    def __str__(self):
        return f'{self.id} | {self.titulo} | {self.autor} | Cantidad: {self.cantidad}'
