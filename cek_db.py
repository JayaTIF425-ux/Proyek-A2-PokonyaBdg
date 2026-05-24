import sqlite3

db = sqlite3.connect('data/hargapangan.db')
db.execute("""
    DELETE FROM harga_pangan
    WHERE id NOT IN (
        SELECT MIN(id) FROM harga_pangan
        GROUP BY komoditas, tanggal, jenis_pasar
    )
""")
db.commit()
print("Duplikat dihapus:", db.total_changes, "baris")
db.close()