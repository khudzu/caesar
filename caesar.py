import streamlit as st

# Judul aplikasi
st.title("Enkripsi Bifurkasi Sederhana")

# Input dari pengguna
p = st.text_input("Masukkan teks (p):", value="proses bifurkasi")
k = st.text_input("Masukkan kunci (k):", value="kau")

# Tombol proses
if st.button("Enkripsi"):
    cip = ''
    for i in range(len(p)):
        if p[i] == ' ':
            c = ord(' ')
        else:
            c = ((ord(p[i]) + ord(k[i % len(k)]) - 97) % 26) + 97
        cip += chr(c)

    # Output hasil enkripsi
    st.success(f"Hasil Enkripsi: {cip}")
