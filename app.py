import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
DB_NAME = "books.db"

def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = connect_db()
    
    # Buat tabel jika belum ada
    conn.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        judul VARCHAR(100) NOT NULL,
        penulis VARCHAR(100) NOT NULL,
        tahun INTEGER,
        genre VARCHAR(50)
    )
    ''')
    
    # Cek jika kolom tahun dan genre belum ada, lalu tambahkan
    try:
        # Cek apakah kolom tahun sudah ada
        conn.execute("SELECT tahun FROM books LIMIT 1")
    except sqlite3.OperationalError:
        # Tambahkan kolom tahun jika belum ada
        conn.execute("ALTER TABLE books ADD COLUMN tahun INTEGER")
        print("Kolom 'tahun' ditambahkan ke tabel books")
    
    try:
        # Cek apakah kolom genre sudah ada
        conn.execute("SELECT genre FROM books LIMIT 1")
    except sqlite3.OperationalError:
        # Tambahkan kolom genre jika belum ada
        conn.execute("ALTER TABLE books ADD COLUMN genre VARCHAR(50)")
        print("Kolom 'genre' ditambahkan ke tabel books")
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = connect_db()
    books = conn.execute("SELECT * FROM books ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('index.html', books=books)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        judul = request.form['judul']
        penulis = request.form['penulis']
        tahun = request.form.get('tahun') or None
        genre = request.form.get('genre') or None
        
        conn = connect_db()
        conn.execute("INSERT INTO books (judul, penulis, tahun, genre) VALUES (?, ?, ?, ?)", 
                    (judul, penulis, tahun, genre))
        conn.commit()
        conn.close()
        
        flash('Buku berhasil ditambahkan!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = connect_db()
    book = conn.execute("SELECT * FROM books WHERE id = ?", (id,)).fetchone()
    
    if not book:
        conn.close()
        flash('Buku tidak ditemukan!', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        judul = request.form['judul']
        penulis = request.form['penulis']
        tahun = request.form.get('tahun') or None
        genre = request.form.get('genre') or None
        
        conn.execute("UPDATE books SET judul = ?, penulis = ?, tahun = ?, genre = ? WHERE id = ?", 
                    (judul, penulis, tahun, genre, id))
        conn.commit()
        conn.close()
        
        flash('Buku berhasil diperbarui!', 'success')
        return redirect(url_for('index'))
    
    conn.close()
    return render_template('edit.html', book=book)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    try:
        conn = connect_db()
        conn.execute("DELETE FROM books WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        
        flash('Buku berhasil dihapus!', 'success')
        return jsonify({'success': True})
    except:
        flash('Gagal menghapus buku!', 'error')
        return jsonify({'success': False})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)