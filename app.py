import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- DATABASE SETUP ----------------

# Ensure clothes table exists (with tags and category)
def ensure_clothes_table():
    conn = sqlite3.connect("packingplanner.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS clothes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            tags TEXT,
            image TEXT,
            category TEXT
        )
    """)
    conn.commit()
    conn.close()

# Ensure packing_items table exists (supports manual entries and clothing_id)
def ensure_packing_items_table():
    conn = sqlite3.connect("packingplanner.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS packing_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clothing_id INTEGER,
            name TEXT,
            FOREIGN KEY(clothing_id) REFERENCES clothes(id)
        )
    """)
    conn.commit()
    conn.close()

ensure_clothes_table()
ensure_packing_items_table()

# ---------------- ROUTES ----------------

@app.route('/')
def index():
    conn = sqlite3.connect("packingplanner.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # All closet items
    c.execute("SELECT * FROM clothes")
    closet = c.fetchall()

    # All packing items with optional clothing name
    c.execute("""
        SELECT pi.id, pi.clothing_id, pi.name, c.name AS clothing_name
        FROM packing_items pi
        LEFT JOIN clothes c ON pi.clothing_id = c.id
    """)
    packing_list = c.fetchall()

    # IDs of packed closet items
    packed_ids = [row['clothing_id'] for row in packing_list if row['clothing_id']]

    conn.close()
    return render_template('index.html', closet=closet, packing_list=packing_list, packed_ids=packed_ids)

# ---------------- Upload clothes ----------------

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

# ---------------- Add closet item to packing list ----------------

@app.route('/add_to_packing', methods=['POST'])
def add_to_packing():
    clothing_id = request.form['clothing_id']

    conn = sqlite3.connect('packingplanner.db')
    c = conn.cursor()

    # Only add if not already packed
    c.execute("SELECT id FROM packing_items WHERE clothing_id = ?", (clothing_id,))
    if not c.fetchone():
        c.execute("INSERT INTO packing_items (clothing_id) VALUES (?)", (clothing_id,))

    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# ---------------- Add manual packing item ----------------

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

# ---------------- Remove item from packing list ----------------

@app.route('/remove_packing_item', methods=['POST'])
def remove_packing_item():
    item_id = request.form['item_id']
    conn = sqlite3.connect("packingplanner.db")
    c = conn.cursor()
    c.execute("DELETE FROM packing_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route("/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    conn = sqlite3.connect("packingplanner.db")
    c = conn.cursor()
    c.execute("DELETE FROM clothes WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

# ---------------- Run app ----------------

if __name__ == '__main__':
    app.run(debug=True)