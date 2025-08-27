import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ensure tags column exists
def ensure_tags_column():
    conn = sqlite3.connect("packingplanner.db")
    c = conn.cursor()
    c.execute("PRAGMA table_info(clothes)")
    columns = [col[1] for col in c.fetchall()]
    if "tags" not in columns:
        c.execute("ALTER TABLE clothes ADD COLUMN tags TEXT")
        conn.commit()
    conn.close()

ensure_tags_column()

def ensure_packing_items_table():
    conn = sqlite3.connect("packingplanner.db")
    c = conn.cursor()
    # Create packing_items table if it doesn't exist
    c.execute("""
        CREATE TABLE IF NOT EXISTS packing_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
    """)
    conn.commit()
    conn.close()

ensure_packing_items_table()


@app.route('/')
def index():
    conn = sqlite3.connect("packingplanner.db")
    conn.row_factory = sqlite3.Row

    c = conn.cursor()
    c.execute("SELECT * FROM clothes")
    closet = c.fetchall()

    # Optional: packing list items table
    c.execute("SELECT * FROM packing_items")
    packing_list = c.fetchall()

    conn.close()
    return render_template('index.html', closet=closet, packing_list=packing_list)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        name = request.form['name']
        tags = request.form.get('tags', "")
        category = request.form['category']
        image = request.files['image']

        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            conn = sqlite3.connect("packingplanner.db")
            c = conn.cursor()

            c.execute(
                "INSERT INTO clothes (name, tags, image, category) VALUES (?, ?, ?, ?)",
                (name, tags, filename, category)
            )
            conn.commit()
            conn.close()

        return redirect(url_for('index'))

    return render_template('upload.html')


@app.route('/add_packing_item', methods=['POST'])
def add_packing_item():
    item_name = request.form['item_name']
    if item_name:
        conn = sqlite3.connect("packingplanner.db")
        c = conn.cursor()
        c.execute("INSERT INTO packing_items (name) VALUES (?)", (item_name,))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))


@app.route('/add_to_packing', methods = ['POST'])
def add_to_packing():
    clothing_id = request.form['clothing_id']

    conn = sqlite3.connect('packingplanner.db')
    c = conn.cursor()

    # Check if already added
    c.execute("SELECT id FROM packing_items WHERE clothing_id = ?", (clothing_id,))
    if not c.fetchone():
        c.execute("INSERT INTO packing_items (clothing_id) VALUES (?)", (clothing_id,))

    conn.commit()
    conn.close()

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)