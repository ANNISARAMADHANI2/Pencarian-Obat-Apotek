# Import library pandas untuk manipulasi data, terutama DataFrame
import pandas as pd
# Import library gradio untuk membuat antarmuka pengguna web interaktif
import gradio as gr
# Import library matplotlib.pyplot untuk membuat visualisasi grafis, seperti diagram pohon
import matplotlib.pyplot as plt
# Import library numpy untuk operasi numerik, di sini mungkin digunakan untuk kalkulasi posisi pada Matplotlib
import numpy as np

# Mencoba membaca file CSV bernama "Data SDA.csv" ke dalam DataFrame pandas
try:
    df = pd.read_csv("Data SDA.csv")
# Menangani error jika file tidak ditemukan
except FileNotFoundError:
    print("Error: File 'Data SDA.csv' tidak ditemukan. Pastikan file tersebut ada di direktori yang sama.")
    # Jika file tidak ditemukan, buat DataFrame kosong dengan kolom yang diharapkan
    # Ini untuk mencegah error di bagian lain skrip yang bergantung pada DataFrame df
    df = pd.DataFrame(columns=['Nama Obat', 'Nama Pemesan', 'Kategori Penyakit', 'Tanggal Pesan'])

# Mendefinisikan kelas Node untuk struktur data Binary Search Tree (BST)
class Node:
    # Konstruktor kelas Node
    def __init__(self, nama_obat):
        # nama_obat akan menjadi kunci untuk BST, disimpan dalam huruf kecil (lowercase)
        self.nama_obat = nama_obat
        # List untuk menyimpan semua data (baris dari CSV) yang memiliki nama_obat yang sama
        self.data = []
        # Referensi ke anak kiri (node dengan nama_obat lebih kecil)
        self.left = None
        # Referensi ke anak kanan (node dengan nama_obat lebih besar)
        self.right = None
        # Atribut untuk menyimpan koordinat x node saat visualisasi dengan Matplotlib
        self.x = 0
        # Atribut untuk menyimpan koordinat y node saat visualisasi dengan Matplotlib
        self.y = 0

# Fungsi rekursif untuk memasukkan data (sebuah baris dari DataFrame) ke dalam BST
def insert(root, row):
    # Memeriksa apakah kolom 'Nama Obat' ada dalam baris dan nilainya tidak kosong/NaN (Not a Number)
    if 'Nama Obat' not in row or pd.isna(row['Nama Obat']):
        return root # Jika nama obat kosong, abaikan baris ini dan kembalikan root saat ini

    # Mengambil nama obat, menghilangkan spasi di awal/akhir, dan mengubahnya menjadi huruf kecil sebagai kunci
    nama_obat_key = str(row['Nama Obat']).strip().lower()
    # Memeriksa apakah setelah diproses, nama_obat_key menjadi string kosong
    if not nama_obat_key:
        return root # Jika string kosong, abaikan dan kembalikan root saat ini

    # Jika root (akar pohon) masih kosong (pohon belum ada isinya)
    if root is None:
        # Buat node baru dengan nama_obat_key
        node = Node(nama_obat_key)
        # Tambahkan seluruh baris data (dikonversi menjadi dictionary jika tipe Series) ke list data node
        # Jika 'row' adalah Series pandas, ubah ke dict. Jika sudah dict (misalnya dari pemanggilan rekursif lain), gunakan langsung.
        node.data.append(row.to_dict() if isinstance(row, pd.Series) else row)
        return node # Kembalikan node baru sebagai root

    # Jika nama_obat_key lebih kecil dari nama_obat di root saat ini
    if nama_obat_key < root.nama_obat:
        # Masukkan secara rekursif ke subtree kiri
        root.left = insert(root.left, row)
    # Jika nama_obat_key lebih besar dari nama_obat di root saat ini
    elif nama_obat_key > root.nama_obat:
        # Masukkan secara rekursif ke subtree kanan
        root.right = insert(root.right, row)
    # Jika nama_obat_key sama dengan nama_obat di root saat ini (obat sudah ada)
    else:
        # Tambahkan data baris ini ke list data pada node yang sudah ada
        root.data.append(row.to_dict() if isinstance(row, pd.Series) else row)
    return root # Kembalikan root (yang mungkin telah dimodifikasi atau tetap sama)

# Fungsi untuk mencari data (node) di BST berdasarkan nama obat
def search(root, nama_obat_cari):
    # Validasi input: jika nama_obat_cari kosong atau bukan string, kembalikan None
    if not nama_obat_cari or not isinstance(nama_obat_cari, str):
        return None
    # Memproses nama_obat_cari: menghilangkan spasi di awal/akhir dan mengubah ke huruf kecil
    nama_obat_key = nama_obat_cari.strip().lower()
    # Jika setelah diproses menjadi string kosong, kembalikan None
    if not nama_obat_key:
        return None

    # Mulai pencarian dari root
    current = root
    # Looping selama current node tidak None (belum mencapai ujung pohon)
    while current is not None:
        # Jika nama_obat_key lebih kecil dari nama_obat di node current
        if nama_obat_key < current.nama_obat:
            current = current.left # Pindah ke anak kiri
        # Jika nama_obat_key lebih besar dari nama_obat di node current
        elif nama_obat_key > current.nama_obat:
            current = current.right # Pindah ke anak kanan
        # Jika nama_obat_key sama dengan nama_obat di node current
        else:
            return current # Node ditemukan, kembalikan node tersebut
    return None # Jika loop selesai tanpa menemukan node, berarti node tidak ada, kembalikan None

# Inisialisasi root BST sebagai None (kosong)
root = None
# Memeriksa apakah DataFrame df tidak kosong
if not df.empty:
    # Melakukan iterasi (looping) pada setiap baris dalam DataFrame df
    # `_` digunakan karena kita tidak memerlukan indeks barisnya secara langsung
    for _, row in df.iterrows():
        # Memasukkan setiap baris (data obat) ke dalam BST menggunakan fungsi insert
        root = insert(root, row)
else:
    # Jika DataFrame kosong, cetak pesan bahwa BST tidak dibangun
    print("DataFrame kosong, BST tidak dibangun.")

# Menyiapkan daftar nama obat unik untuk digunakan dalam dropdown Gradio
# Periksa apakah DataFrame tidak kosong dan memiliki kolom 'Nama Obat'
if not df.empty and 'Nama Obat' in df.columns:
    # Ambil kolom 'Nama Obat', hilangkan nilai NaN (dropna), ubah ke tipe string,
    # hilangkan spasi (strip), ubah ke format Title Case (huruf pertama setiap kata kapital),
    # ambil nilai unik, lalu urutkan.
    daftar_obat_unique = sorted(df['Nama Obat'].dropna().astype(str).str.strip().str.title().unique())
    # Tambahkan opsi "-" di awal daftar sebagai pilihan default atau "kosong"
    daftar_obat = ["-"] + daftar_obat_unique
else:
    # Jika DataFrame kosong atau kolom 'Nama Obat' tidak ada, buat daftar default hanya dengan "-"
    daftar_obat = ["-"]

# --- Fungsi untuk Visualisasi BST dengan Matplotlib (Simpan ke File) ---

# Fungsi helper rekursif untuk menggambar node dan edge (garis antar node) dengan Matplotlib
def _draw_tree_matplotlib_recursive(node, ax):
    # `ax` adalah objek Axes dari Matplotlib tempat menggambar
    if node is None: # Basis kasus rekursi: jika node kosong, tidak ada yang digambar
        return

    # Menyiapkan label untuk node: Nama Obat (dengan huruf kapital di awal setiap kata)
    # dan jumlah data (jumlah pesanan) untuk obat tersebut.
    # `node.nama_obat` sudah dalam lowercase, jadi kita ubah ke title case untuk tampilan.
    label = f"{node.nama_obat.title()}\n(Data: {len(node.data)})"
    # Menampilkan teks (label) pada posisi (node.x, node.y) di Axes `ax`
    # ha='center', va='center' agar teks ditengah-tengah kotak
    # bbox adalah kotak di sekitar teks dengan properti visual tertentu
    ax.text(node.x, node.y, label, ha='center', va='center',
            bbox=dict(facecolor='skyblue', alpha=0.7, edgecolor='black', boxstyle='round,pad=0.5'))

    # Jika ada anak kiri
    if node.left:
        # Gambar garis dari node saat ini ke anak kiri
        # `lw` adalah line width (ketebalan garis), `color` adalah warna garis
        ax.plot([node.x, node.left.x], [node.y, node.left.y], '-', lw=1.5, color='gray')
        # Panggil fungsi ini secara rekursif untuk anak kiri
        _draw_tree_matplotlib_recursive(node.left, ax)
    # Jika ada anak kanan
    if node.right:
        # Gambar garis dari node saat ini ke anak kanan
        ax.plot([node.x, node.right.x], [node.y, node.right.y], '-', lw=1.5, color='gray')
        # Panggil fungsi ini secara rekursif untuk anak kanan
        _draw_tree_matplotlib_recursive(node.right, ax)

# Fungsi untuk menetapkan koordinat x dan y ke setiap node dalam pohon
def assign_xy(node, current_x_ref, depth=0, y_spacing=1.0, x_spacing=1.0, x_coords_at_depth=None):
    if node is None: # Basis kasus rekursi: jika node kosong, hentikan
        return

    if x_coords_at_depth is None: # Inisialisasi jika ini panggilan pertama
        x_coords_at_depth = {}

    # 1. Proses subtree kiri terlebih dahulu (sesuai inorder traversal)
    # Ini akan menetapkan posisi untuk semua node di subtree kiri
    assign_xy(node.left, current_x_ref, depth + 1, y_spacing, x_spacing, x_coords_at_depth)

    # 2. Tetapkan posisi y untuk node saat ini berdasarkan kedalamannya
    # y negatif agar root berada di atas dan pohon tumbuh ke bawah
    node.y = -depth * y_spacing

    # 3. Tetapkan posisi x untuk node saat ini
    # `current_x_ref[0]` adalah posisi x berikutnya yang tersedia setelah node sebelumnya (atau subtree kiri) diproses.
    proposed_x = current_x_ref[0]

    # Periksa apakah ada tumpang tindih dengan node lain pada kedalaman (depth) yang sama.
    # Ambil x terakhir yang digunakan pada kedalaman ini (jika ada, defaultnya -infinity)
    # tambahkan sedikit spasi (x_spacing * 0.5) untuk jarak antar node pada level yang sama.
    min_x_at_this_depth = x_coords_at_depth.get(depth, -float('inf')) + (x_spacing * 0.5)

    # Pilih x yang lebih besar antara proposed_x (dari inorder traversal) dan min_x_at_this_depth (untuk menghindari overlap)
    node.x = max(proposed_x, min_x_at_this_depth)

    # Update referensi x global untuk node berikutnya yang akan diproses (biasanya root dari subtree kanan)
    current_x_ref[0] = node.x + x_spacing
    # Catat koordinat x yang digunakan pada kedalaman ini
    x_coords_at_depth[depth] = node.x

    # 4. Proses subtree kanan (sesuai inorder traversal)
    assign_xy(node.right, current_x_ref, depth + 1, y_spacing, x_spacing, x_coords_at_depth)


# Fungsi untuk mengumpulkan semua node dalam pohon ke dalam sebuah list
# Ini berguna untuk menentukan batas-batas plot visualisasi (min/max x dan y)
def collect_all_nodes(node, nodes_list=None):
    if nodes_list is None: # Inisialisasi list jika ini panggilan pertama
        nodes_list = []
    if node: # Jika node tidak None
        nodes_list.append(node) # Tambahkan node saat ini ke list
        collect_all_nodes(node.left, nodes_list) # Kumpulkan node dari subtree kiri
        collect_all_nodes(node.right, nodes_list) # Kumpulkan node dari subtree kanan
    return nodes_list # Kembalikan list yang berisi semua node

# Fungsi utama untuk membuat visualisasi BST menggunakan Matplotlib dan menyimpannya ke file
def visualize_bst_matplotlib(tree_root, filename="bst_matplotlib.png", title="Visualisasi BST"):
    if tree_root is None: # Jika pohon kosong
        print(f"Pohon ({title}) kosong, tidak ada yang divisualisasikan dengan Matplotlib.")
        # Buat figure dan axes kosong
        fig, ax = plt.subplots(figsize=(8, 5))
        # Tampilkan teks bahwa pohon kosong
        ax.text(0.5, 0.5, f"{title}\n(Kosong)", ha='center', va='center', fontsize=14, color='gray')
        ax.axis('off') # Sembunyikan sumbu x dan y
        plt.title(title, fontsize=16) # Beri judul pada plot
        try:
            plt.savefig(filename) # Simpan gambar ke file
            print(f"Gambar '{filename}' untuk pohon kosong telah disimpan.")
        except Exception as e:
            print(f"Gagal menyimpan gambar pohon kosong: {e}")
        plt.close(fig) # Tutup figure untuk menghemat memori
        return # Keluar dari fungsi

    # Buat figure dan axes untuk menggambar pohon. Ukuran bisa disesuaikan.
    fig, ax = plt.subplots(figsize=(20, 12))

    # Inisialisasi variabel untuk fungsi `assign_xy`
    # `current_x_tracker` adalah list dengan satu elemen agar bisa diubah nilainya di dalam rekursi (pass by reference)
    current_x_tracker = [0.0]
    # `x_coords_per_depth` untuk melacak x yang sudah digunakan per kedalaman, menghindari tumpang tindih
    x_coords_per_depth = {}

    # Panggil fungsi `assign_xy` untuk menghitung dan menetapkan koordinat x,y untuk setiap node
    # Ini akan memodifikasi atribut node.x dan node.y secara langsung
    assign_xy(tree_root, current_x_tracker, depth=0, y_spacing=1.0, x_spacing=1.5, x_coords_at_depth=x_coords_per_depth)

    # Panggil fungsi rekursif untuk menggambar pohon (node dan edge)
    _draw_tree_matplotlib_recursive(tree_root, ax)

    # Mengumpulkan semua node untuk menentukan batas plot agar semua node terlihat
    all_nodes = collect_all_nodes(tree_root)
    if all_nodes: # Jika ada node dalam pohon
        # Ambil semua koordinat x dan y dari semua node
        all_x = [n.x for n in all_nodes]
        all_y = [n.y for n in all_nodes]
        if all_x and all_y: # Pastikan list koordinat tidak kosong
            # Atur batas sumbu x dan y dengan sedikit padding (-1 dan +1)
            ax.set_xlim(min(all_x) - 1, max(all_x) + 1)
            ax.set_ylim(min(all_y) - 1, max(all_y) + 1)

    ax.axis('off') # Sembunyikan sumbu x dan y pada visualisasi akhir
    plt.title(title, fontsize=16) # Beri judul pada plot
    try:
        plt.savefig(filename) # Simpan visualisasi ke file
        print(f"Visualisasi Matplotlib '{title}' disimpan sebagai '{filename}'")
    except Exception as e: # Tangani error jika gagal menyimpan
        print(f"Gagal menyimpan visualisasi Matplotlib '{title}': {e}")
    plt.close(fig) # Tutup figure untuk menghemat memori


# Fungsi yang akan dipanggil oleh Gradio ketika tombol "Cari Data" diklik
def cari_obat_gradio(nama_obat_input):
    # Jika input nama obat kosong, atau hanya "-", atau string kosong setelah di-strip
    if not nama_obat_input or str(nama_obat_input).strip() == "-" or not str(nama_obat_input).strip():
        # Kembalikan DataFrame kosong dengan header yang sudah diubah untuk memberi petunjuk
        return pd.DataFrame(columns=['Nama Pemesan', 'Kategori Penyakit', 'Tanggal Pesan']).rename(
            columns={
                'Nama Pemesan': "Nama Pemesan (Silakan pilih atau ketik nama obat untuk dicari)",
                'Kategori Penyakit': "Kategori Penyakit",
                'Tanggal Pesan': "Tanggal Pesan"
            }
        )

    # Lakukan pencarian di BST menggunakan fungsi search, pastikan input adalah string
    node_hasil = search(root, str(nama_obat_input))
    if node_hasil: # Jika node (obat) ditemukan
        # Buat DataFrame dari list of dictionaries yang ada di `node_hasil.data`
        hasil_df = pd.DataFrame(node_hasil.data)
        # Tentukan kolom yang ingin ditampilkan dan urutannya
        kolom_tampil = ['Nama Pemesan', 'Kategori Penyakit', 'Tanggal Pesan']
        # Pastikan semua kolom yang ingin ditampilkan ada di hasil_df.
        # Jika tidak ada, tambahkan kolom tersebut dengan nilai string kosong.
        for kol in kolom_tampil:
            if kol not in hasil_df.columns:
                hasil_df[kol] = ""
        # Kembalikan DataFrame dengan kolom yang sudah dipilih dan diurutkan
        return hasil_df[kolom_tampil]
    else: # Jika node (obat) tidak ditemukan
        # Buat DataFrame kosong terlebih dahulu
        temp_df = pd.DataFrame(columns=['Nama Pemesan', 'Kategori Penyakit', 'Tanggal Pesan'])
        # Tambahkan satu baris yang berisi pesan bahwa obat tidak ditemukan
        # `str(nama_obat_input).title()` untuk menampilkan nama obat yang dicari dengan format yang rapi
        temp_df.loc[0] = [f"Obat '{str(nama_obat_input).title()}' tidak ditemukan.", "", ""]
        return temp_df


# Fungsi untuk mengisi textbox input nama obat berdasarkan pilihan dari dropdown
def isi_textbox_dari_dropdown(pilihan_dropdown):
    if pilihan_dropdown == "-": # Jika pilihan dropdown adalah "-",
        return "" # Kosongkan textbox
    return pilihan_dropdown # Jika tidak, isi textbox dengan pilihan dropdown


# Membuat antarmuka pengguna (UI) dengan Gradio
# `gr.Blocks` memungkinkan pembuatan UI yang lebih kustom dengan layout yang fleksibel
# `theme=gr.themes.Soft()` menggunakan tema visual "Soft" dari Gradio
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    # Menampilkan teks Markdown sebagai judul utama aplikasi
    gr.Markdown("# ⚕️ Pencarian Data Pemesan Obat Apotek ⚕️")
    # Menampilkan teks Markdown sebagai deskripsi singkat aplikasi
    gr.Markdown("Aplikasi ini memungkinkan Anda mencari data pemesan obat dari data yang tersedia.")

    # Membuat Tab "Pencarian Obat"
    with gr.TabItem("Pencarian Obat"):
        # Judul di dalam tab
        gr.Markdown("## 🔍 Cari Detail Pemesan Berdasarkan Nama Obat")
        # Membuat baris (Row) untuk menata komponen secara horizontal
        with gr.Row():
            # Komponen Textbox untuk input nama obat secara manual
            input_obat_gradio = gr.Textbox(label="Ketik Nama Obat", placeholder="Contoh: Paracetamol")
            # Komponen Dropdown untuk memilih nama obat dari daftar yang sudah ada
            # `choices` diisi dengan `daftar_obat` yang sudah disiapkan sebelumnya
            # `value="-"` menetapkan nilai default dropdown
            dropdown_obat_gradio = gr.Dropdown(choices=daftar_obat, label="Atau Pilih dari Daftar", value="-")

        # Komponen Button untuk memicu aksi pencarian
        # `variant="primary"` membuat tombol tampil lebih menonjol
        cari_btn_gradio = gr.Button("Cari Data", variant="primary")

        # Judul untuk bagian hasil pencarian
        gr.Markdown("### Hasil Pencarian:")
        # Komponen DataFrame untuk menampilkan hasil pencarian dalam bentuk tabel
        hasil_pencarian_df_gradio = gr.DataFrame(
            headers=['Nama Pemesan', 'Kategori Penyakit', 'Tanggal Pesan'], # Menentukan header tabel
            label="Detail Pesanan Obat" # Label untuk komponen DataFrame
        )

        # Menghubungkan event: ketika nilai dropdown_obat_gradio berubah (event `change`)
        # Panggil fungsi `isi_textbox_dari_dropdown`
        # Inputnya adalah `dropdown_obat_gradio`, outputnya adalah `input_obat_gradio`
        dropdown_obat_gradio.change(fn=isi_textbox_dari_dropdown, inputs=dropdown_obat_gradio, outputs=input_obat_gradio)
        # Menghubungkan event: ketika tombol cari_btn_gradio diklik (event `click`)
        # Panggil fungsi `cari_obat_gradio`
        # Inputnya adalah `input_obat_gradio`, outputnya adalah `hasil_pencarian_df_gradio`
        cari_btn_gradio.click(fn=cari_obat_gradio, inputs=input_obat_gradio, outputs=hasil_pencarian_df_gradio)

    # Garis pemisah horizontal (Markdown)
    gr.Markdown("---")
    # Informasi tambahan mengenai visualisasi BST yang dibuat saat aplikasi dimulai
    gr.Markdown("Visualisasi keseluruhan struktur data obat (BST) telah dibuat dan disimpan sebagai `bst_keseluruhan_matplotlib.png` saat aplikasi dimulai (jika data tersedia).")


# Blok ini akan dieksekusi hanya jika skrip dijalankan secara langsung (bukan diimpor sebagai modul)
if __name__ == "__main__":
    print("\n--- Membuat Visualisasi BST Keseluruhan (Matplotlib) ---")
    # Memanggil fungsi untuk membuat dan menyimpan visualisasi dari keseluruhan BST
    # yang telah dibangun dari file CSV. Gambar disimpan sebagai "bst_keseluruhan.png".
    # Perhatikan ada typo di nama file "bst_keseluruan", mungkin seharusnya "bst_keseluruhan.png"
    visualize_bst_matplotlib(root, filename="obat.png", title="BST Obat Keseluruhan") # Saya perbaiki typo di filename

    print("\n--- Menjalankan Aplikasi Web Gradio untuk Pencarian Data ---")
    print("Buka browser Anda dan navigasi ke URL yang ditampilkan di bawah ini.")
    # Meluncurkan aplikasi web Gradio. Ini akan membuat server lokal dan memberikan URL untuk diakses.
    demo.launch()
    
    #kalau tagarnya di hapus jdnya 224 baris