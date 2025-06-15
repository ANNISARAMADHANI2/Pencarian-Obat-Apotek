import pandas as pd
import gradio as gr
import matplotlib.pyplot as plt # Untuk visualisasi dengan Matplotlib
import numpy as np # Diperlukan untuk beberapa kalkulasi posisi di Matplotlib

# Baca file CSV
try:
    df = pd.read_csv("Data SDA.csv")
except FileNotFoundError:
    print("Error: File 'Data SDA.csv' tidak ditemukan. Pastikan file tersebut ada di direktori yang sama.")
    # Buat DataFrame kosong jika file tidak ditemukan agar skrip tidak error
    df = pd.DataFrame(columns=['Nama Obat', 'Nama Pemesan', 'Kategori Penyakit', 'Tanggal Pesan'])

# Kelas Node BST
class Node:
    def __init__(self, nama_obat):
        self.nama_obat = nama_obat # Ini akan menjadi kunci (sudah di-lower())
        self.data = []
        self.left = None
        self.right = None
        # Atribut untuk Matplotlib (posisi x, y)
        self.x = 0
        self.y = 0

# Fungsi untuk memasukkan data ke BST
def insert(root, row):
    # Pastikan 'Nama Obat' ada di baris dan tidak kosong
    if 'Nama Obat' not in row or pd.isna(row['Nama Obat']):
        return root # Abaikan baris jika nama obat kosong

    nama_obat_key = str(row['Nama Obat']).strip().lower()
    if not nama_obat_key: # Abaikan jika setelah strip hasilnya string kosong
        return root

    if root is None:
        node = Node(nama_obat_key)
        # Simpan seluruh baris (sebagai dictionary) ke dalam list data node
        node.data.append(row.to_dict() if isinstance(row, pd.Series) else row)
        return node
    
    if nama_obat_key < root.nama_obat:
        root.left = insert(root.left, row)
    elif nama_obat_key > root.nama_obat:
        root.right = insert(root.right, row)
    else:
        # Jika nama obat sama, tambahkan data ke node yang sudah ada
        root.data.append(row.to_dict() if isinstance(row, pd.Series) else row)
    return root

# Fungsi untuk mencari data di BST
def search(root, nama_obat_cari):
    if not nama_obat_cari or not isinstance(nama_obat_cari, str): # Pemeriksaan input
        return None
    nama_obat_key = nama_obat_cari.strip().lower()
    if not nama_obat_key: # Jika string kosong setelah strip
        return None
        
    current = root
    while current is not None:
        if nama_obat_key < current.nama_obat:
            current = current.left
        elif nama_obat_key > current.nama_obat:
            current = current.right
        else:
            return current # Node ditemukan
    return None # Node tidak ditemukan

# Bangun BST
root = None
if not df.empty:
    for _, row in df.iterrows(): # Melakukan looping berdasarkan hasil csv
        root = insert(root, row) # Membangun tree dengan menggunakan fungsi insert
else:
    print("DataFrame kosong, BST tidak dibangun.")

# Ambil daftar nama obat unik untuk dropdown
if not df.empty and 'Nama Obat' in df.columns:
    # Membersihkan, mengubah ke title case, dan mengambil nilai unik
    daftar_obat_unique = sorted(df['Nama Obat'].dropna().astype(str).str.strip().str.title().unique())
    daftar_obat = ["-"] + daftar_obat_unique
else:
    daftar_obat = ["-"] # Default jika DataFrame kosong atau kolom tidak ada

# --- Fungsi untuk Visualisasi BST dengan Matplotlib (Simpan ke File) ---
def _draw_tree_matplotlib_recursive(node, ax):
    """Helper rekursif untuk menggambar node dan edge dengan Matplotlib."""
    if node is None:
        return

    # Tampilkan nama obat dengan kapitalisasi awal dan jumlah data
    # Nama obat di node sudah lower case, jadi kita title() case kan untuk tampilan
    label = f"{node.nama_obat.title()}\n(Data: {len(node.data)})"
    ax.text(node.x, node.y, label, ha='center', va='center',
            bbox=dict(facecolor='skyblue', alpha=0.7, edgecolor='black', boxstyle='round,pad=0.5'))

    if node.left:
        ax.plot([node.x, node.left.x], [node.y, node.left.y], '-', lw=1.5, color='gray') # Garis abu-abu
        _draw_tree_matplotlib_recursive(node.left, ax)
    if node.right:
        ax.plot([node.x, node.right.x], [node.y, node.right.y], '-', lw=1.5, color='gray') # Garis abu-abu
        _draw_tree_matplotlib_recursive(node.right, ax)

def assign_xy(node, current_x_ref, depth=0, y_spacing=1.0, x_spacing=1.0, x_coords_at_depth=None):
    """
    Menetapkan koordinat x dan y untuk node menggunakan pendekatan inorder traversal untuk x
    dan kedalaman untuk y. x_coords_at_depth digunakan untuk mencoba menghindari tumpang tindih.
    """
    if node is None:
        return

    if x_coords_at_depth is None:
        x_coords_at_depth = {}

    # Proses subtree kiri dulu
    assign_xy(node.left, current_x_ref, depth + 1, y_spacing, x_spacing, x_coords_at_depth)

    # Tetapkan posisi y berdasarkan kedalaman
    node.y = -depth * y_spacing  # y negatif agar root di atas

    # Tetapkan posisi x
    # Coba untuk menempatkan node setelah node sebelumnya pada kedalaman yang sama atau setelah subtree kiri
    proposed_x = current_x_ref[0]
    
    # Periksa tumpang tindih dengan node lain pada kedalaman yang sama
    # Ambil x terakhir yang digunakan pada kedalaman ini + spasi
    min_x_at_this_depth = x_coords_at_depth.get(depth, -float('inf')) + (x_spacing * 0.5) # Beri sedikit spasi
    
    node.x = max(proposed_x, min_x_at_this_depth)
    
    current_x_ref[0] = node.x + x_spacing # Update x global untuk node berikutnya
    x_coords_at_depth[depth] = node.x # Catat x yang digunakan pada kedalaman ini

    # Proses subtree kanan
    assign_xy(node.right, current_x_ref, depth + 1, y_spacing, x_spacing, x_coords_at_depth)


def collect_all_nodes(node, nodes_list=None):
    """Mengumpulkan semua node dalam pohon (untuk mendapatkan batas plot)."""
    if nodes_list is None:
        nodes_list = []
    if node:
        nodes_list.append(node)
        collect_all_nodes(node.left, nodes_list)
        collect_all_nodes(node.right, nodes_list)
    return nodes_list

def visualize_bst_matplotlib(tree_root, filename="bst_matplotlib.png", title="Visualisasi BST"):
    """Membuat visualisasi BST menggunakan Matplotlib dan menyimpannya ke file."""
    if tree_root is None:
        print(f"Pohon ({title}) kosong, tidak ada yang divisualisasikan dengan Matplotlib.")
        fig, ax = plt.subplots(figsize=(8, 5)) # Ukuran disesuaikan
        ax.text(0.5, 0.5, f"{title}\n(Kosong)", ha='center', va='center', fontsize=14, color='gray')
        ax.axis('off')
        plt.title(title, fontsize=16)
        try:
            plt.savefig(filename)
            print(f"Gambar '{filename}' untuk pohon kosong telah disimpan.")
        except Exception as e:
            print(f"Gagal menyimpan gambar pohon kosong: {e}")
        plt.close(fig)
        return

    fig, ax = plt.subplots(figsize=(20, 12)) # Ukuran bisa disesuaikan agar lebih lega

    # Mengassign posisi x dan y ke setiap node
    current_x_tracker = [0.0] # List agar bisa diubah by reference dalam rekursi
    x_coords_per_depth = {} # Untuk melacak koordinat x yang sudah digunakan per kedalaman
    
    # Hitung kedalaman maksimum untuk skala y_spacing yang lebih baik jika perlu
    # (Untuk saat ini, y_spacing tetap, tapi ini bisa jadi pengembangan)

    # Fungsi assign_xy akan memodifikasi node.x dan node.y secara langsung
    assign_xy(tree_root, current_x_tracker, depth=0, y_spacing=1.0, x_spacing=1.5, x_coords_at_depth=x_coords_per_depth)

    _draw_tree_matplotlib_recursive(tree_root, ax)

    # Mengatur batas plot agar semua node terlihat
    all_nodes = collect_all_nodes(tree_root)
    if all_nodes:
        all_x = [n.x for n in all_nodes]
        all_y = [n.y for n in all_nodes]
        if all_x and all_y: # Pastikan list tidak kosong
            ax.set_xlim(min(all_x) - 1, max(all_x) + 1)
            ax.set_ylim(min(all_y) - 1, max(all_y) + 1)
    
    ax.axis('off') # Sembunyikan sumbu
    plt.title(title, fontsize=16)
    try:
        plt.savefig(filename)
        print(f"Visualisasi Matplotlib '{title}' disimpan sebagai '{filename}'")
    except Exception as e:
        print(f"Gagal menyimpan visualisasi Matplotlib '{title}': {e}")
    plt.close(fig) # Tutup figure untuk menghemat memori


# Fungsi pencarian untuk Gradio
def cari_obat_gradio(nama_obat_input):
    if not nama_obat_input or str(nama_obat_input).strip() == "-" or not str(nama_obat_input).strip():
        # Mengembalikan DataFrame kosong jika input tidak valid atau "-"
        return pd.DataFrame(columns=['Nama Pemesan', 'Kategori Penyakit', 'Tanggal Pesan']).rename(
            columns={
                'Nama Pemesan': "Nama Pemesan (Silakan pilih atau ketik nama obat untuk dicari)",
                'Kategori Penyakit': "Kategori Penyakit",
                'Tanggal Pesan': "Tanggal Pesan"
            }
        )

    node_hasil = search(root, str(nama_obat_input)) # Pastikan input adalah string
    if node_hasil:
        # Buat DataFrame dari list of dictionaries di node_hasil.data
        hasil_df = pd.DataFrame(node_hasil.data)
        # Pilih dan urutkan kolom yang diinginkan
        kolom_tampil = ['Nama Pemesan', 'Kategori Penyakit', 'Tanggal Pesan']
        # Pastikan semua kolom ada, jika tidak, tambahkan sebagai string kosong
        for kol in kolom_tampil:
            if kol not in hasil_df.columns:
                hasil_df[kol] = ""
        return hasil_df[kolom_tampil]
    else:
        # Mengembalikan DataFrame dengan pesan "Obat tidak ditemukan"
        # Buat DataFrame kosong dulu, lalu isi dengan pesan
        temp_df = pd.DataFrame(columns=['Nama Pemesan', 'Kategori Penyakit', 'Tanggal Pesan'])
        temp_df.loc[0] = [f"Obat '{str(nama_obat_input).title()}' tidak ditemukan.", "", ""]
        return temp_df


# Fungsi untuk mengisi textbox dari dropdown
def isi_textbox_dari_dropdown(pilihan_dropdown):
    if pilihan_dropdown == "-":
        return "" # Kosongkan textbox jika pilihan adalah "-"
    return pilihan_dropdown


# Gradio interface
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# ⚕️ Pencarian Data Pemesan Obat Apotek ⚕️")
    gr.Markdown("Aplikasi ini memungkinkan Anda mencari data pemesan obat dari data yang tersedia.")

    with gr.TabItem("Pencarian Obat"):
        gr.Markdown("## 🔍 Cari Detail Pemesan Berdasarkan Nama Obat")
        with gr.Row():
            input_obat_gradio = gr.Textbox(label="Ketik Nama Obat", placeholder="Contoh: Paracetamol")
            dropdown_obat_gradio = gr.Dropdown(choices=daftar_obat, label="Atau Pilih dari Daftar", value="-")
        
        cari_btn_gradio = gr.Button("Cari Data", variant="primary")
        
        gr.Markdown("### Hasil Pencarian:")
        hasil_pencarian_df_gradio = gr.DataFrame(
            headers=['Nama Pemesan', 'Kategori Penyakit', 'Tanggal Pesan'],
            label="Detail Pesanan Obat"
        )
        
        # Event: dropdown mengisi textbox
        dropdown_obat_gradio.change(fn=isi_textbox_dari_dropdown, inputs=dropdown_obat_gradio, outputs=input_obat_gradio)
        # Event: tombol cari memicu fungsi pencarian
        cari_btn_gradio.click(fn=cari_obat_gradio, inputs=input_obat_gradio, outputs=hasil_pencarian_df_gradio)

    gr.Markdown("---")
    gr.Markdown("Visualisasi keseluruhan struktur data obat (BST) telah dibuat dan disimpan sebagai `bst_keseluruhan_matplotlib.png` saat aplikasi dimulai (jika data tersedia).")


# --- Bagian untuk demonstrasi output Matplotlib saat skrip dijalankan ---
if __name__ == "__main__":
    print("\n--- Membuat Visualisasi BST Keseluruhan (Matplotlib) ---")
    # Panggil visualisasi untuk keseluruhan BST yang telah dibangun dari CSV
    visualize_bst_matplotlib(root, filename="bst_keseluruan", title="BST Obat Keseluruhan")
    
    print("\n--- Menjalankan Aplikasi Web Gradio untuk Pencarian Data ---")
    print("Buka browser Anda dan navigasi ke URL yang ditampilkan di bawah ini.")
    demo.launch()