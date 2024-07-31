import streamlit as st
import pandas as pd
import requests
from pymongo import MongoClient

# Koneksi ke MongoDB Atlas
client = MongoClient("mongodb+srv://IPutuAdityaWarman:aditganteng123@mycluster.mezsl0t.mongodb.net/?retryWrites=true&w=majority&appName=MyCluster")
db = client['sic5_project']
collection = db['data_child']

# Data berat dan tinggi badan rata-rata
data_berat_tinggi = {
    "Usia (Bulan)": [6, 12, 18, 24, 30, 36, 48, 60],
    "Berat Badan Rata-Rata Laki-Laki (kg)": [7.9, 9.6, 10.9, 12.2, 13.3, 14.3, 16.3, 18.3],
    "Berat Badan Rata-Rata Perempuan (kg)": [7.3, 8.9, 10.2, 11.5, 12.6, 13.9, 15.5, 17.4],
    "Tinggi Badan Rata-Rata Laki-Laki (cm)": [61.0, 69.7, 76.0, 81.8, 87.1, 92.0, 101.7, 111.2],
    "Tinggi Badan Rata-Rata Perempuan (cm)": [60.5, 68.7, 74.9, 80.3, 85.3, 90.4, 99.1, 108.2]
}

df_berat_tinggi = pd.DataFrame(data_berat_tinggi)

st.title('Check Stunting Anak dari 6 Bulan hingga 5 tahun')

# Input ID dan Nama Bayi
id_bayi = st.text_input("ID Bayi:")
nama_bayi = st.text_input("Nama Bayi:")

jenis_kelamin = st.radio("Jenis Kelamin Anak:", ["Laki-Laki", "Perempuan"])
usia_anak = st.number_input("Usia Anak (Bulan):", min_value=6, max_value=60, step=6)

# Get data from Flask
response = requests.get('http://127.0.0.1:5000/data')
if response.status_code == 200:
    data_store = response.json()
    if data_store:
        berat_badan_anak = data_store[-1]['weight']
        tinggi_badan_anak = data_store[-1]['height']
    else:
        berat_badan_anak = 0.0
        tinggi_badan_anak = 0.0
else:
    st.error("Gagal mengambil data dari server Flask")
    berat_badan_anak = 0.0
    tinggi_badan_anak = 0.0
    
st.write(f"Usia Anak: {usia_anak} Bulan")
st.write(f"Berat Badan Anak: {berat_badan_anak:.2f} kg")
st.write(f"Tinggi Badan Anak: {tinggi_badan_anak:.2f} cm")

if jenis_kelamin == "Laki-Laki":
    berat_badan_rata_rata = df_berat_tinggi[df_berat_tinggi["Usia (Bulan)"] == usia_anak]["Berat Badan Rata-Rata Laki-Laki (kg)"].values[0]
    tinggi_badan_rata_rata = df_berat_tinggi[df_berat_tinggi["Usia (Bulan)"] == usia_anak]["Tinggi Badan Rata-Rata Laki-Laki (cm)"].values[0]
else:
    berat_badan_rata_rata = df_berat_tinggi[df_berat_tinggi["Usia (Bulan)"] == usia_anak]["Berat Badan Rata-Rata Perempuan (kg)"].values[0]
    tinggi_badan_rata_rata = df_berat_tinggi[df_berat_tinggi["Usia (Bulan)"] == usia_anak]["Tinggi Badan Rata-Rata Perempuan (cm)"].values[0]
    
keterangan = ""
if berat_badan_anak < berat_badan_rata_rata - 2 and tinggi_badan_anak < tinggi_badan_rata_rata - 2:
    status = "Stunting"
    keterangan = "Berat badan dan tinggi badan anak di bawah rata-rata."
elif berat_badan_anak < berat_badan_rata_rata - 2:
    status = "Stunting"
    keterangan = "Berat badan anak di bawah rata-rata."
elif tinggi_badan_anak < tinggi_badan_rata_rata - 2:
    status = "Stunting"
    keterangan = "Tinggi badan anak di bawah rata-rata."
else:
    status = "Tidak Stunting"
    
st.write(f"Status anak: {status}")
if keterangan:
    st.write(f"Keterangan: {keterangan}")
    
st.subheader("Berat Badan Rata-Rata Anak Berdasarkan Usia:")
st.dataframe(df_berat_tinggi[["Usia (Bulan)", "Berat Badan Rata-Rata Laki-Laki (kg)", "Berat Badan Rata-Rata Perempuan (kg)"]])

st.subheader("Tinggi Badan Rata-Rata Anak Berdasarkan Usia:")
st.dataframe(df_berat_tinggi[["Usia (Bulan)", "Tinggi Badan Rata-Rata Laki-Laki (cm)", "Tinggi Badan Rata-Rata Perempuan (cm)"]])

if st.button("Post to MongoDB"):
    data_child = {
        "id_bayi": id_bayi,
        "nama_bayi": nama_bayi,
        "usia": usia_anak,
        "berat_badan": tinggi_badan_anak,
        "jenis_kelamin": jenis_kelamin,
        "status": status,
        "keterangan": keterangan
    }
    collection.insert_one(data_child)
    st.success("Data berhasil dikirim ke MongoDB!")