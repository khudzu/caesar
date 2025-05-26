import streamlit as st
import sqlite3
import pandas as pd

# Fungsi enkripsi sederhana
def enkripsi(text, key):
    hasil = ''
    for i in range(len(text)):
        if text[i] == ' ':
            c = ord(' ')
        else:
            c = ((ord(text[i]) + ord(key[i % len(key)]) - 97) % 26) + 97
        hasil += chr(c)
    return hasil

# Inisialisasi database
def init_db():
    conn = sqlite3.connect('data_penduduk.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS penduduk (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            alamat TEXT,
            ttl TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Menyimpan ke database
def simpan_ke_db(nama, alamat, ttl):
    conn = sqlite3.connect('data_penduduk.db')
    c = conn.cursor()
    c.execute('INSERT INTO penduduk (nama, alamat, ttl) VALUES (?, ?, ?)', (nama, alamat, ttl))
    conn.commit()
    conn.close()

# Menampilkan data dari database
def ambil_data():
    conn = sqlite3.connect('data_penduduk.db')
    df = pd.read_sql_query('SELECT * FROM penduduk', conn)
    conn.close()
    return df

# Inisialisasi database saat pertama kali
init_db()

# UI Streamlit
st.title("🔐 Enkripsi & Penyimpanan Data Penduduk")

with st.form("form_data"):
    nama = st.text_input("Nama Lengkap")
    alamat = st.text_area("Alamat")
    ttl = st.text_input("Tempat & Tanggal Lahir (contoh: Sidoarjo, 1 Jan 1990)")
    kunci = st.text_input("Kunci Enkripsi", type="password")
    submit = st.form_submit_button("Enkripsi & Simpan")

if submit:
    if not kunci:
        st.error("Kunci enkripsi tidak boleh kosong.")
    else:
        # Proses enkripsi
        nama_enkrip = enkripsi(nama.lower(), kunci.lower())
        alamat_enkrip = enkripsi(alamat.lower(), kunci.lower())
        ttl_enkrip = enkripsi(ttl.lower(), kunci.lower())

        # Simpan ke database
        simpan_ke_db(nama_enkrip, alamat_enkrip, ttl_enkrip)
        st.success("Data berhasil dienkripsi dan disimpan!")

# Tampilkan data terenkripsi
st.subheader("📊 Data Penduduk Terenkripsi")
df = ambil_data()
st.dataframe(df)
