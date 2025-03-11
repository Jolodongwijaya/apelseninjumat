import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from PIL import Image
import os
import base64
import random

# inisialisasi koneksi ke database
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "jadwal_apel"
}

# Fungsi koneksi ke database
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Fungsi untuk memnaggil petugas berdasarkan peran
def get_petugas(role):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nama FROM petugas WHERE peran = %s ORDER BY id ASC", (role,))
        return [row[0] for row in cursor.fetchall()]

# Fungsi rotasi petugas
def get_rotated_petugas(role):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        petugas = get_petugas(role)  
        if not petugas:
            return "Tidak ada petugas"
        
        cursor.execute("SELECT DISTINCT nama FROM jadwal WHERE peran = %s", (role,))
        sudah_bertugas = [row[0] for row in cursor.fetchall()]

        # Tambahkan logika untuk memeriksa apakah petugas sudah bertugas dalam peran lain
        if role == "8 Nilai MA":
            cursor.execute("SELECT DISTINCT nama FROM jadwal WHERE peran = 'Ajudan'")
            sudah_bertugas += [row[0] for row in cursor.fetchall()]
        elif role == "Ajudan":
            cursor.execute("SELECT DISTINCT nama FROM jadwal WHERE peran = '8 Nilai MA'")
            sudah_bertugas += [row[0] for row in cursor.fetchall()]

        # Cari petugas yang belum bertugas dalam rotasi
        kandidat = [p for p in petugas if p not in sudah_bertugas]

        # Jika semua sudah bertugas, reset rotasi
        if not kandidat:
            cursor.execute("DELETE FROM jadwal WHERE peran = %s", (role,))
            conn.commit()
            kandidat = petugas

        selected = kandidat[0]
        
        cursor.execute("INSERT INTO jadwal (nama, peran) VALUES (%s, %s)", (selected, role))
        conn.commit()

        return selected

# Fungsi untuk rotasi petugas 8 Nilai MA
def get_rotated_petugas_8_nilai():
    return get_rotated_petugas("8 Nilai MA")

# Fungsi untuk rotasi petugas Ajudan
def get_rotated_petugas_ajudan():
    return get_rotated_petugas("Ajudan")

# Fungsi untuk memanggil data pembina
def get_pembina(hari):
    if hari == "Senin":
        return random.choice(["Ketua PA", "Wakil PA"])
    elif hari == "Jumat":
        return get_rotated_petugas("Hakim")

# Fungsi untuk menyimpan jadwal ke database
def simpan_jadwal(data, tanggal):
    if data is None:
        raise ValueError(f"Jadwal untuk tanggal {tanggal} tidak dapat disimpan karena data kosong.")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM jadwal WHERE tanggal = %s", (tanggal,))
        for posisi, nama in data.items():
            cursor.execute("INSERT INTO jadwal (posisi, nama, tanggal) VALUES (%s, %s, %s)",
                         (posisi, nama, tanggal))
        conn.commit()

# Fungsi untuk memanggil jadwal berdasarkan tanggal
def get_jadwal_by_tanggal(tanggal):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT posisi, nama FROM jadwal WHERE tanggal = %s", (tanggal,))
        return {posisi: nama for posisi, nama in cursor.fetchall()}

# Fungsi untuk memanggil jadwal berdasarkan rentang tanggal
def get_jadwal_by_date_range(start_date, end_date):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT tanggal, posisi, nama FROM jadwal WHERE tanggal BETWEEN %s AND %s ORDER BY tanggal """, (start_date, end_date))
        results = cursor.fetchall()
        
        jadwal_dict = {}
        for tanggal, posisi, nama in results:
            if tanggal not in jadwal_dict:
                jadwal_dict[tanggal] = {}
            jadwal_dict[tanggal][posisi] = nama
        return [{"tanggal": k, "data": v} for k, v in jadwal_dict.items()]

# Fungsi untuk memanggil jadwal berdasarkan nama
def get_jadwal_by_nama(nama):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(""" SELECT tanggal, posisi, nama FROM jadwal WHERE nama = %s ORDER BY tanggal""", (nama,))
        results = cursor.fetchall()
        
        jadwal_dict = {}
        for tanggal, posisi, nama in results:
            if tanggal not in jadwal_dict:
                jadwal_dict[tanggal] = {}
            jadwal_dict[tanggal][posisi] = nama
        return [{"tanggal": k, "data": v} for k, v in jadwal_dict.items()]

# Fungsi untuk generate jadwal harian
def generate_daily_schedule(tanggal):
    hari = "Senin" if datetime.strptime(tanggal, '%Y-%m-%d').weekday() == 0 else "Jumat"
    assigned = []  

    # Fungsi untuk memanggil jadwal berdasarkan tgl
    existing = get_jadwal_by_date_range(tanggal, tanggal)
    if existing:
        return None
    
    jadwal = {
        "MC": get_rotated_petugas("MC"),
        "Pembaca 8 Nilai MA": get_rotated_petugas_8_nilai(),
        "Ajudan": get_rotated_petugas_ajudan(),
        "Pembina": get_pembina(hari),
        "Komandan": "Agung Yusfantoro, S.H."
    }
    assigned.extend(jadwal.values())
    
    return jadwal

# Fungsi untuk export jadwal berupa file PDF
def export_to_pdf(jadwal_list, title):
    file_path = f"jadwal_apel_{title}.pdf"
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height-50, f"Jadwal Apel Bulan {title}")

    y = height - 80
    for jadwal in jadwal_list:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y, f"Tanggal: {jadwal['tanggal']}")
        y -= 20
        
        c.setFont("Helvetica-Bold", 10)
        for posisi, nama in jadwal['data'].items():
            c.drawString(120, y, f"{posisi}: {nama}")
            y -= 15
        y -= 20
        
        if y < 100:
            c.showPage()
            y = height - 50

    c.save()
    return file_path

# Judul Aplikasi 
st.set_page_config(page_title="Aplikasi Jadwal Apel", page_icon="📌", layout='wide')

# Fungsi menambahkan teks berjalan di beranda web 
marquee_text = """
<div class="marquee" id="marqueeText">
    🏛️ Selamat datang di Aplikasi Penjadwalan Apel Pengadilan Agama Kab. Kediri 🏛️
</div>

<style>
    .marquee {
        display: inline-block;
        white-space: nowrap;
        font-size: 20px;
        font-weight: bold;
        animation: marquee 10s linear infinite;
    }

    /* Animasi teks berjalan */
    @keyframes marquee {
        from { transform: translateX(100%); }
        to { transform: translateX(-100%); }
    }
</style>

<script>
    function updateTextColor() {
        const textElement = document.getElementById("marqueeText");
        const isDarkMode = window.matchMedia("(prefers-color-scheme: dark)").matches;
        textElement.style.color = isDarkMode ? "#ffffff" : "#000000";
    }

    document.addEventListener("DOMContentLoaded", updateTextColor);
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", updateTextColor);
</script>
"""

st.markdown(marquee_text, unsafe_allow_html=True)

# UI Streamlit
st.title("📅 Jadwal Apel Pengadilan Agama Kab. Kediri")

def get_all_petugas():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT nama FROM petugas")
        return [row[0] for row in cursor.fetchall()]

# Fungsi untuk memanggil logo yang ingin ditampilkan
logo = Image.open("logoevp.png")

# Fungsi untuk menampilkan dan mengatur ukuran logo
st.sidebar.image(logo, use_container_width=10, caption ="Pengadilan Agama Kab. Kediri")

# Fungsi untuk menampilkan judul di sidebar
search_type = st.sidebar.radio("Jenis Pencarian:", ["Berdasarkan Tanggal", "Berdasarkan Nama"])

if search_type == "Berdasarkan Tanggal":
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Mulai", datetime.today() - timedelta(days=30))
    with col2:
        end_date = st.date_input("Selesai", datetime.today() + timedelta(days=30))
else:
    nama_pencarian = st.sidebar.selectbox(
        "Pilih Nama Petugas:",
        options=get_all_petugas()  
    )

# Fungsi untuk menampilkan data yang ingin di-generate
jadwal_pencarian = get_jadwal_by_date_range(start_date, end_date) if search_type == "Berdasarkan Tanggal" else get_jadwal_by_nama(nama_pencarian)

if jadwal_pencarian:
    st.subheader("🔍 Hasil Pencarian")
    
    # Fungsi menampilkan data jadwal harian
    df_data = []
    columns = ["Tanggal", "Hari", "MC", "Pembaca 8 Nilai MA", "Ajudan", "Pembina", "Komandan"]
    hari_dict = {0: "Senin", 4: "Jumat"}  
    for jadwal in sorted(jadwal_pencarian, key=lambda x: x['tanggal']):
        row = [jadwal['tanggal']]
        tanggal_obj = datetime.strptime(str(jadwal['tanggal']), '%Y-%m-%d')
        row.append(hari_dict[tanggal_obj.weekday()])  
        row.extend(jadwal['data'].get(posisi, '-') for posisi in columns[2:])
        df_data.append(row)
    
    df = pd.DataFrame(df_data, columns=columns)
    st.dataframe(df)
    
    if st.button("📤 Export ke PDF"):
        title = datetime.today().strftime("%B_%Y")
        pdf_file = export_to_pdf(jadwal_pencarian, title)
        with open(pdf_file, "rb") as f:
            st.download_button("💾 Download PDF", f, file_name=pdf_file, mime="application/pdf")
        os.remove(pdf_file)

# Fungsi untuk menampilkan jadwal di bulan yang sedang berjalan
if datetime.today().weekday() == 3:  
    st.info("ℹ️ Memperbarui jadwal bulan ini")
    
    # Fungsi untuk memperbarui jadwal bulanan
    start = datetime.today().replace(day=1)
    end = (start + relativedelta(months=1)) - timedelta(days=1)
    
    dates = []
    current_date = start
    while current_date <= end:
        if current_date.weekday() in [0, 4]:  
            dates.append(current_date)
        current_date += timedelta(days=1)
    
    for date in dates:
        tanggal = date.strftime('%Y-%m-%d')
        jadwal = generate_daily_schedule(tanggal)
        if jadwal:  
            simpan_jadwal(jadwal, tanggal)
    
    st.success("✅ Jadwal bulan ini telah diperbarui!")

# Fungsi untuk menampilkan jadwal harian
columns = ["Tanggal", "Hari", "MC", "Pembaca 8 Nilai MA", "Ajudan", "Pembina", "Komandan"]

st.subheader(f"📅 Jadwal Bulan {datetime.today().strftime('%B %Y')}")
start = datetime.today().replace(day=1)
end = (start + relativedelta(months=1)) - timedelta(days=1)
jadwal_bulan_ini = get_jadwal_by_date_range(start, end)

# Fungsi untuk menampilkan jadwal bulanan
if jadwal_bulan_ini:
    df_data = []
    hari_dict = {0: "Senin", 4: "Jumat"}  
    for jadwal in sorted(jadwal_bulan_ini, key=lambda x: x['tanggal']):
        row = [jadwal['tanggal']]
        tanggal_obj = datetime.strptime(str(jadwal['tanggal']), '%Y-%m-%d')
        row.append(hari_dict[tanggal_obj.weekday()])  
        row.extend(jadwal['data'].get(posisi, '-') for posisi in columns[2:])
        df_data.append(row)
    
    df = pd.DataFrame(df_data, columns=columns)
    st.dataframe(df.style.set_properties(**{'text-align': 'center'}).set_table_styles([dict(selector='th', props=[('text-align', 'center')])]))
    
    # Fungsi export jadwal ke PDF
    if st.button("📥 Export Bulanan ke PDF"):
        title = datetime.today().strftime("%B_%Y")
        pdf_file = export_to_pdf(jadwal_bulan_ini, title)
        with open(pdf_file, "rb") as f:
            st.download_button("💾 Download PDF", f, file_name=pdf_file, mime="application/pdf")
        os.remove(pdf_file)
else:
    st.warning("⚠️ Belum ada jadwal untuk bulan ini")