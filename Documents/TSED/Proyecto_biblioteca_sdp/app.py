from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from modelos.usuario import Usuario
from conexion.conexion import get_connection
from inventario.bd import crear_tabla
from inventario.inventario import Inventario
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import hashlib
import os

app = Flask(__name__)
app.secret_key = 'biblioteca_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

crear_tabla()
inv = Inventario()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@login_manager.user_loader
def load_user(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM usuarios WHERE id_usuario = %s', (user_id,))
    u = cursor.fetchone()
    conn.close()
    if u:
        return Usuario(u['id_usuario'], u['nombre'], u['email'], u['password'])
    return None

# ─── AUTH ────────────────────────────────────────────────────────────────────

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = hash_password(request.form['password'])
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)',
            (nombre, email, password)
        )
        conn.commit()
        conn.close()
        flash('Registro exitoso. Inicia sesión.')
        return redirect(url_for('login'))
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hash_password(request.form['password'])
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            'SELECT * FROM usuarios WHERE email = %s AND password = %s',
            (email, password)
        )
        u = cursor.fetchone()
        conn.close()
        if u:
            usuario = Usuario(u['id_usuario'], u['nombre'], u['email'], u['password'])
            login_user(usuario)
            return redirect(url_for('libros'))
        flash('Credenciales incorrectas.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ─── PÁGINAS ─────────────────────────────────────────────────────────────────

@app.route('/')
@login_required
def inicio():
    return render_template('index.html')

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/libro/<titulo>')
@login_required
def libro(titulo):
    return f'Libro: {titulo} – consulta exitosa'

# ─── CRUD LIBROS ─────────────────────────────────────────────────────────────

@app.route('/libros')
@login_required
def libros():
    todos = inv.mostrar_todos()
    return render_template('libros.html', libros=todos)

@app.route('/agregar', methods=['POST'])
@login_required
def agregar():
    titulo = request.form['titulo']
    autor = request.form['autor']
    cantidad = int(request.form['cantidad'])
    inv.agregar_libro(titulo, autor, cantidad)
    return redirect(url_for('libros'))

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        cantidad = int(request.form['cantidad'])
        cursor.execute(
            'UPDATE libros SET titulo=%s, autor=%s, cantidad=%s WHERE id=%s',
            (titulo, autor, cantidad, id)
        )
        conn.commit()
        conn.close()
        inv.cargar_desde_bd()
        return redirect(url_for('libros'))
    cursor.execute('SELECT * FROM libros WHERE id = %s', (id,))
    libro = cursor.fetchone()
    conn.close()
    return render_template('editar.html', libro=libro)

@app.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    inv.eliminar_libro(id)
    return redirect(url_for('libros'))

# ─── EXPORTAR ────────────────────────────────────────────────────────────────

@app.route('/exportar/<formato>')
@login_required
def exportar(formato):
    if formato == 'txt':
        inv.exportar_txt()
    elif formato == 'json':
        inv.exportar_json()
    elif formato == 'csv':
        inv.exportar_csv()
    return redirect(url_for('libros'))

# ─── REPORTE PDF ─────────────────────────────────────────────────────────────

@app.route('/reporte-pdf')
@login_required
def reporte_pdf():
    path = 'static/reporte_libros.pdf'
    c = canvas.Canvas(path, pagesize=letter)
    c.setFont('Helvetica-Bold', 16)
    c.drawString(180, 750, 'Reporte de Biblioteca Virtual')
    c.setFont('Helvetica-Bold', 11)
    c.drawString(50, 720, 'ID')
    c.drawString(90, 720, 'Título')
    c.drawString(350, 720, 'Autor')
    c.drawString(510, 720, 'Cantidad')
    c.setFont('Helvetica', 11)
    y = 700
    for libro in inv.mostrar_todos():
        c.drawString(50, y, str(libro.get_id()))
        c.drawString(90, y, libro.get_titulo()[:35])
        c.drawString(350, y, libro.get_autor()[:22])
        c.drawString(510, y, str(libro.get_cantidad()))
        y -= 20
        if y < 50:
            c.showPage()
            y = 750
    c.save()
    return send_file(path, as_attachment=True)

# ─── TEST CONEXIÓN ────────────────────────────────────────────────────────────

@app.route('/test-mysql')
def test_mysql():
    try:
        conn = get_connection()
        conn.close()
        return 'Conexión MySQL exitosa!'
    except Exception as e:
        return f'Error: {e}'

if __name__ == '__main__':
    app.run(debug=True)
