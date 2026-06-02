from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# DATABASE
def init_db():

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
CREATE TABLE IF NOT EXISTS pesanan(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nomor_po TEXT,
    vendor TEXT,

    invoice INTEGER DEFAULT 0,
    pembayaran INTEGER DEFAULT 0,
    packing INTEGER DEFAULT 0,
    pengiriman INTEGER DEFAULT 0,
    diterima INTEGER DEFAULT 0
)
""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS barang(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pesanan_id INTEGER,
        nama_barang TEXT,
        qty INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route("/")
def dashboard():

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM pesanan")
    data = c.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        data=data
    )

@app.route("/detail/<int:id>")
def detail(id):

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute(
        "SELECT * FROM pesanan WHERE id=?",
        (id,)
    )

    po = c.fetchone()

    if not po:
        conn.close()
        return "PO tidak ditemukan"

    c.execute(
        "SELECT * FROM barang WHERE pesanan_id=?",
        (id,)
    )

    barang = c.fetchall()

    conn.close()

    status = [
        po[3],
        po[4],
        po[5],
        po[6],
        po[7]
    ]

    progress = (sum(status) / 5) * 100

    return render_template(
        "detail_po.html",
        po=po,
        barang=barang,
        progress=progress
    )
@app.route("/tambah", methods=["POST"])
def tambah():

    vendor = request.form["vendor"]

    barang = request.form.getlist("barang[]")
    qty = request.form.getlist("qty[]")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM pesanan")
    jumlah = c.fetchone()[0] + 1

    nomor_po = f"PO-{jumlah:03d}"

    c.execute(
        """
        INSERT INTO pesanan
        (nomor_po,vendor)
        VALUES (?,?)
        """,
        (nomor_po, vendor)
    )

    pesanan_id = c.lastrowid

    for b,q in zip(barang, qty):

        if b.strip():

            c.execute(
                """
                INSERT INTO barang
                (pesanan_id,nama_barang,qty)
                VALUES (?,?,?)
                """,
                (pesanan_id,b,q)
            )

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/update_status/<int:id>", methods=["POST"])
def update_status(id):

    invoice = 1 if "invoice" in request.form else 0
    pembayaran = 1 if "pembayaran" in request.form else 0
    packing = 1 if "packing" in request.form else 0
    pengiriman = 1 if "pengiriman" in request.form else 0
    diterima = 1 if "diterima" in request.form else 0

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
        UPDATE pesanan
        SET
        invoice=?,
        pembayaran=?,
        packing=?,
        pengiriman=?,
        diterima=?
        WHERE id=?
    """,
    (
        invoice,
        pembayaran,
        packing,
        pengiriman,
        diterima,
        id
    ))

    conn.commit()
    conn.close()

    return redirect(f"/detail/{id}")

@app.route("/hapus/<int:id>")
def hapus(id):

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Hapus semua barang dalam PO
    c.execute(
        "DELETE FROM barang WHERE pesanan_id=?",
        (id,)
    )

    # Hapus PO
    c.execute(
        "DELETE FROM pesanan WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":

        vendor = request.form["vendor"]

        c.execute(
            """
            UPDATE pesanan
            SET vendor=?
            WHERE id=?
            """,
            (vendor, id)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    c.execute(
        "SELECT * FROM pesanan WHERE id=?",
        (id,)
    )

    po = c.fetchone()

    conn.close()

    return render_template(
        "edit_po.html",
        po=po
    )

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)