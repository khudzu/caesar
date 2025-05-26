import streamlit as st
import sqlite3
import pandas as pd

# Dummy kredensial login
USER_CREDENTIALS = {
    "admin": "admin123"
}

# Fungsi enkripsi & dekripsi (pakai rumus Anda)
def enkripsi(text, key):
    hasil = ''
    for i in range(len(text)):
        if text[i] == ' ':
            c = ord(' ')
        else:
            c = ((ord(text[i]) + ord(key[i % len(key)]) - 97) % 26) + 97
        hasil += chr(c)
    return hasil

def dekripsi(cipher, key):
    hasil = ''
    for i in range(len(cipher)):
        if cipher[i] == ' ':
            c = ord(' ')
        else:
            c = ((ord(cipher[i]) - ord(key[i % len(key)]) - 97) % 26) + 97
        hasil += chr(c)
    return hasil

# Inisialisasi database SQLite
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

def simpan_ke_db(nama, alamat, ttl):
    conn = sqlite3.connect('data_penduduk.db')
    c = conn.cursor()
    c.execute('INSERT INTO penduduk (nama, alamat, ttl) VALUES (?, ?, ?)', (nama, alamat, ttl))
    conn.commit()
    conn.close()

def ambil_data():
    conn = sqlite3.connect('data_penduduk.db')
    df = pd.read_sql_query('SELECT * FROM penduduk', conn)
    conn.close()
    return df

def update_data(id, nama, alamat, ttl):
    conn = sqlite3.connect('data_penduduk.db')
    c = conn.cursor()
    c.execute('UPDATE penduduk SET nama=?, alamat=?, ttl=? WHERE id=?', (nama, alamat, ttl, id))
    conn.commit()
    conn.close()

def hapus_data(id):
    conn = sqlite3.connect('data_penduduk.db')
    c = conn.cursor()
    c.execute('DELETE FROM penduduk WHERE id=?', (id,))
    conn.commit()
    conn.close()

def login(username, password):
    return USER_CREDENTIALS.get(username) == password

# Inisialisasi DB
init_db()

# Session state login
if "login_status" not in st.session_state:
    st.session_state.login_status = False

if not st.session_state.login_status:
    st.title("🔐 Login Pengguna")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")

        if login_btn:
            if login(username, password):
                st.session_state.login_status = True
                st.success("Login berhasil!")
                st.rerun()
            else:
                st.error("Username atau password salah!")

else:
    st.sidebar.title("🔧 Navigasi")
    menu = st.sidebar.radio("Pilih Menu", ["Input Data", "Lihat Data Terenkripsi", "Dekripsi Data", "Edit Data", "Hapus Data", "Logout"])

    if menu == "Input Data":
        st.title("📝 Input & Enkripsi Data Penduduk")
        with st.form("form_input"):
            nama = st.text_input("Nama")
            alamat = st.text_area("Alamat")
            ttl = st.text_input("Tempat Lahir")
            kunci = st.text_input("Kunci Enkripsi", type="password")
            submit = st.form_submit_button("Simpan")

            if submit:
                if not kunci:
                    st.warning("Kunci tidak boleh kosong!")
                else:
                    nama_enc = enkripsi(nama.lower(), kunci.lower())
                    alamat_enc = enkripsi(alamat.lower(), kunci.lower())
                    ttl_enc = enkripsi(ttl.lower(), kunci.lower())

                    simpan_ke_db(nama_enc, alamat_enc, ttl_enc)
                    st.success("Data berhasil dienkripsi dan disimpan!")

    elif menu == "Lihat Data Terenkripsi":
        st.title("📦 Data Terenkripsi")
        data = ambil_data()
        st.dataframe(data)

    elif menu == "Dekripsi Data":
        st.title("🔓 Dekripsi Data Penduduk")
        kunci_dekripsi = st.text_input("Masukkan Kunci Dekripsi", type="password")

        if kunci_dekripsi:
            df_enc = ambil_data()
            decrypted_data = {
                "ID": [],
                "Nama": [],
                "Alamat": [],
                "Tempat Lahir": []
            }

            for _, row in df_enc.iterrows():
                try:
                    decrypted_data["ID"].append(row["id"])
                    decrypted_data["Nama"].append(dekripsi(row["nama"], kunci_dekripsi.lower()))
                    decrypted_data["Alamat"].append(dekripsi(row["alamat"], kunci_dekripsi.lower()))
                    decrypted_data["Tempat Lahir"].append(dekripsi(row["ttl"], kunci_dekripsi.lower()))
                except:
                    decrypted_data["Nama"].append("DEKRIPSI GAGAL")
                    decrypted_data["Alamat"].append("DEKRIPSI GAGAL")
                    decrypted_data["Tempat Lahir"].append("DEKRIPSI GAGAL")

            df_decrypted = pd.DataFrame(decrypted_data)
            st.dataframe(df_decrypted)

    elif menu == "Edit Data":
        st.title("✏️ Edit Data Penduduk")
        data = ambil_data()
        selected_id = st.selectbox("Pilih ID untuk diedit", data["id"])

        row = data[data["id"] == selected_id].iloc[0]
        kunci = st.text_input("Kunci Dekripsi", type="password")
        if kunci:
            nama = dekripsi(row["nama"], kunci.lower())
            alamat = dekripsi(row["alamat"], kunci.lower())
            ttl = dekripsi(row["ttl"], kunci.lower())

            with st.form("edit_form"):
                nama_new = st.text_input("Nama", value=nama)
                alamat_new = st.text_area("Alamat", value=alamat)
                ttl_new = st.text_input("Tempat Lahir", value=ttl)
                kunci_baru = st.text_input("Kunci Enkripsi Baru", type="password")
                simpan_btn = st.form_submit_button("Simpan Perubahan")

                if simpan_btn:
                    if not kunci_baru:
                        st.warning("Kunci enkripsi baru tidak boleh kosong!")
                    else:
                        nama_enc = enkripsi(nama_new.lower(), kunci_baru.lower())
                        alamat_enc = enkripsi(alamat_new.lower(), kunci_baru.lower())
                        ttl_enc = enkripsi(ttl_new.lower(), kunci_baru.lower())
                        update_data(selected_id, nama_enc, alamat_enc, ttl_enc)
                        st.success("Data berhasil diperbarui!")

    elif menu == "Hapus Data":
        st.title("🗑️ Hapus Data Penduduk")
        data = ambil_data()
        selected_id = st.selectbox("Pilih ID untuk dihapus", data["id"])
        if st.button("Hapus"):
            hapus_data(selected_id)
            st.success(f"Data dengan ID {selected_id} berhasil dihapus!")
            st.rerun()

    elif menu == "Logout":
        st.session_state.login_status = False
        st.rerun()
