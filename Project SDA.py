import pandas as pd
import gradio as gr
import matplotlib.pyplot as plt # Untuk visualisasi dengan Matplotlib
import numpy as np # Diperlukan untuk beberapa kalkulasi posisi di Matplotlib

# Baca file CSV
df = pd.read_csv("Data SDA.csv")

# Kelas Node BST Inisialisasi class Tree 
class Node:
    def __init__(self, nama_obat):
        self.nama_obat = nama_obat
        self.data = []
        self.left = None
        self.right = None
        # Atribut untuk Matplotlib (posisi x, y)
        self.x = 0
        self.y = 0

def insert(root, row):
    nama_obat = row['Nama Obat'].strip().lower()
    if root is None:
        node = Node(nama_obat)
        node.data.append(row)
        return node
    if nama_obat < root.nama_obat:
        root.left = insert(root.left, row)
    elif nama_obat > root.nama_obat:
        root.right = insert(root.right, row)
    else:
        root.data.append(row)
    return root

def search(root, nama_obat):
    nama_obat = nama_obat.strip().lower()
    if root is None:
        return None
    if nama_obat < root.nama_obat:
        return search(root.left, nama_obat)
    elif nama_obat > root.nama_obat:
        return search(root.right, nama_obat)
    else:
        return root

# Bangun BST # Merubah dataset kedalam bentuk tree 
root = None
if not df.empty:
    for _, row in df.iterrows(): # Melakukan looping berdasarkan hasil csv
        root = insert(root, row) # Membangun tree dengan menggunakan fungsi insert
else:
    print("DataFrame kosong, BST tidak dibangun.")

# Ambil daftar nama obat unik
daftar_obat = ["-"] + sorted(df['Nama Obat'].dropna().str.strip().str.title().unique())

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

# Fungsi pencarian
def cari_obat(nama_obat):
    if nama_obat.strip() == "-" or not nama_obat.strip():
        return pd.DataFrame([{
            "Nama Pemesan": "Silakan pilih atau ketik nama obat",
            "Kategori Penyakit": "",
            "Tanggal Pesan": ""
        }])
    
    node = search(root, nama_obat)
    if node:
        hasil_df = pd.DataFrame(node.data)[['Nama Pemesan', 'Kategori Penyakit', 'Tanggal Pesan']]
        return hasil_df
    else:
        return pd.DataFrame([{
            "Nama Pemesan": "Obat tidak ditemukan",
            "Kategori Penyakit": "",
            "Tanggal Pesan": ""
        }])

# Fungsi untuk mengisi textbox dari dropdown
def isi_textbox(dari_dropdown):
    return dari_dropdown

# Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("## 🔍 Cari Pemesan Obat Apotek")

    with gr.Row():
        input_obat = gr.Textbox(label="Ketik nama obat")
        dropdown_obat = gr.Dropdown(choices=daftar_obat, label="Pilih dari daftar")

    hasil = gr.Dataframe(label="Hasil Pencarian")
    cari_btn = gr.Button("Cari")

    # Event: dropdown mengisi textbox
    dropdown_obat.change(fn=isi_textbox, inputs=dropdown_obat, outputs=input_obat)
    cari_btn.click(fn=cari_obat, inputs=input_obat, outputs=hasil)

demo.launch()
