from inventario.bd import get_connection
from inventario.libro import Libro
import json
import csv
import os

class Inventario:
    def __init__(self):
        self.libros = {}  # diccionario {id: Libro}
        self.cargar_desde_bd()

    def cargar_desde_bd(self):
        self.libros = {}
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM libros')
        filas = cursor.fetchall()
        conn.close()
        for fila in filas:
            libro = Libro(fila['id'], fila['titulo'], fila['autor'], fila['cantidad'])
            self.libros[fila['id']] = libro

    def agregar_libro(self, titulo, autor, cantidad):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO libros (titulo, autor, cantidad) VALUES (?, ?, ?)',
            (titulo, autor, cantidad)
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
        conn.close()
        libro = Libro(nuevo_id, titulo, autor, cantidad)
        self.libros[nuevo_id] = libro

    def eliminar_libro(self, id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM libros WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        if id in self.libros:
            del self.libros[id]

    def buscar_por_titulo(self, titulo):
        return [l for l in self.libros.values() if titulo.lower() in l.get_titulo().lower()]

    def mostrar_todos(self):
        return list(self.libros.values())

    # ─── EXPORTACIONES ───────────────────────────────────────────────────────

    def exportar_txt(self):
        os.makedirs('inventario/data', exist_ok=True)
        with open('inventario/data/datos.txt', 'w', encoding='utf-8') as f:
            for libro in self.libros.values():
                f.write(f'{libro.get_id()}|{libro.get_titulo()}|{libro.get_autor()}|{libro.get_cantidad()}\n')

    def exportar_json(self):
        os.makedirs('inventario/data', exist_ok=True)
        data = [
            {
                'id': l.get_id(),
                'titulo': l.get_titulo(),
                'autor': l.get_autor(),
                'cantidad': l.get_cantidad()
            }
            for l in self.libros.values()
        ]
        with open('inventario/data/datos.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def exportar_csv(self):
        os.makedirs('inventario/data', exist_ok=True)
        with open('inventario/data/datos.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'titulo', 'autor', 'cantidad'])
            for libro in self.libros.values():
                writer.writerow([
                    libro.get_id(),
                    libro.get_titulo(),
                    libro.get_autor(),
                    libro.get_cantidad()
                ])

    def importar_txt(self):
        path = 'inventario/data/datos.txt'
        if not os.path.exists(path):
            return
        with open(path, 'r', encoding='utf-8') as f:
            for linea in f:
                partes = linea.strip().split('|')
                if len(partes) == 4:
                    self.agregar_libro(partes[1], partes[2], int(partes[3]))
