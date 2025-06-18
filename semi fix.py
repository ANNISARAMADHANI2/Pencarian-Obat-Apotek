import pandas as pd
import gradio as gr
import matplotlib.pyplot as plt
import numpy as np

try:
    df = pd.read_csv("Data SDA.csv")
except FileNotFoundError:
    print("Error: File 'Data SDA.csv' tidak ditemukan. Pastikan file tersebut ada di direktori yang sama.")
    df = pd.DataFrame(columns=['Nama Obat', 'Nama Pemesan', 'Kategori Penyakit', 'Tanggal Pesan'])

class Node:
    def __init__(self, nama_obat):
        self.nama_obat = nama_obat
        self.data = []
        self.left = None
        self.right = None
        self.x = 0
        self.y = 0

def insert(root, row):
    if 'Nama Obat' not in row or pd.isna(row['Nama Obat']):
        return root
    nama_obat_key = str(row['Nama Obat']).strip().lower()
    if not nama_obat_key:
        return root 

    if root is None:
        node = Node(nama_obat_key)
        node.data.append(row.to_dict() if isinstance(row, pd.Series) else row)
        return node 

    if nama_obat_key < root.nama_obat:
        root.left = insert(root.left, row)
    elif nama_obat_key > root.nama_obat:
        root.right = insert(root.right, row)
    else:
        root.data.append(row.to_dict() if isinstance(row, pd.Series) else row)
    return root 

def search(root, nama_obat_cari):
    if not nama_obat_cari or not isinstance(nama_obat_cari, str):
        return None
    nama_obat_key = nama_obat_cari.strip().lower()
    if not nama_obat_key:
        return None

    current = root
    while current is not None:
        if nama_obat_key < current.nama_obat:
            current = current.left 
        elif nama_obat_key > current.nama_obat:
            current = current.right 
        else:
            return current 
    return None

root = None
if not df.empty:
    for _, row in df.iterrows():
        root = insert(root, row)
else:
    print("DataFrame kosong, BST tidak dibangun.")

if not df.empty and 'Nama Obat' in df.columns:
    daftar_obat_unique = sorted(df['Nama Obat'].dropna().astype(str).str.strip().str.title().unique())
    daftar_obat = ["-"] + daftar_obat_unique
else:
    daftar_obat = ["-"]

# --- Fungsi untuk Visualisasi BST dengan Matplotlib (Simpan ke File) ---

def _draw_tree_matplotlib_recursive(node, ax):
    if node is None: 
        return

    label = f"{node.nama_obat.title()}\n(Data: {len(node.data)})"
    ax.text(node.x, node.y, label, ha='center', va='center',
            bbox=dict(facecolor='skyblue', alpha=0.7, edgecolor='black', boxstyle='round,pad=0.5'))

    if node.left:
        ax.plot([node.x, node.left.x], [node.y, node.left.y], '-', lw=1.5, color='gray')
        _draw_tree_matplotlib_recursive(node.left, ax)
    if node.right:
        ax.plot([node.x, node.right.x], [node.y, node.right.y], '-', lw=1.5, color='gray')
        _draw_tree_matplotlib_recursive(node.right, ax)

def assign_xy(node, current_x_ref, depth=0, y_spacing=1.0, x_spacing=1.0, x_coords_at_depth=None):
    if node is None: 
        return

    if x_coords_at_depth is None: 
        x_coords_at_depth = {}

    assign_xy(node.left, current_x_ref, depth + 1, y_spacing, x_spacing, x_coords_at_depth)

    node.y = -depth * y_spacing

    proposed_x = current_x_ref[0]

    min_x_at_this_depth = x_coords_at_depth.get(depth, -float('inf')) + (x_spacing * 0.5)

    node.x = max(proposed_x, min_x_at_this_depth)

    current_x_ref[0] = node.x + x_spacing
    x_coords_at_depth[depth] = node.x

    assign_xy(node.right, current_x_ref, depth + 1, y_spacing, x_spacing, x_coords_at_depth)


def collect_all_nodes(node, nodes_list=None):
    if nodes_list is None: 
        nodes_list = []
    if node: 
        nodes_list.append(node) 
        collect_all_nodes(node.left, nodes_list) 
        collect_all_nodes(node.right, nodes_list) 
    return nodes_list 

def visualize_bst_matplotlib(tree_root, filename="bst_matplotlib.png", title="Visualisasi BST"):
    if tree_root is None: 
        print(f"Pohon ({title}) kosong, tidak ada yang divisualisasikan dengan Matplotlib.")
        fig, ax = plt.subplots(figsize=(8, 5))
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

    fig, ax = plt.subplots(figsize=(20, 12))

    current_x_tracker = [0.0]
    x_coords_per_depth = {}

    assign_xy(tree_root, current_x_tracker, depth=0, y_spacing=1.0, x_spacing=1.5, x_coords_at_depth=x_coords_per_depth)

    _draw_tree_matplotlib_recursive(tree_root, ax)

    all_nodes = collect_all_nodes(tree_root)
    if all_nodes:
        all_x = [n.x for n in all_nodes]
        all_y = [n.y for n in all_nodes]
        if all_x and all_y: 
            ax.set_xlim(min(all_x) - 1, max(all_x) + 1)
            ax.set_ylim(min(all_y) - 1, max(all_y) + 1)

    ax.axis('off') 
    plt.title(title, fontsize=16) 
    try:
        plt.savefig(filename) 
        print(f"Visualisasi Matplotlib '{title}' disimpan sebagai '{filename}'")
    except Exception as e: 
        print(f"Gagal menyimpan visualisasi Matplotlib '{title}': {e}")
    plt.close(fig) 


def cari_obat_gradio(nama_obat_input):
    if not nama_obat_input or str(nama_obat_input).strip() == "-" or not str(nama_obat_input).strip():
        return pd.DataFrame(columns=['Nama Pemesan', 'Kategori Penyakit', 'Tanggal Pesan']).rename(
            columns={
                'Nama Pemesan': "Nama Pemesan (Silakan pilih atau ketik nama obat untuk dicari)",
                'Kategori Penyakit': "Kategori Penyakit",
                'Tanggal Pesan': "Tanggal Pesan"
            }
        )

    node_hasil = search(root, str(nama_obat_input))
    if node_hasil:
        hasil_df = pd.DataFrame(node_hasil.data)
        kolom_tampil = ['Nama Pemesan', 'Kategori Penyakit', 'Tanggal Pesan']
        for kol in kolom_tampil:
            if kol not in hasil_df.columns:
                hasil_df[kol] = ""
        return hasil_df[kolom_tampil]
    else: 
        temp_df = pd.DataFrame(columns=['Nama Pemesan', 'Kategori Penyakit', 'Tanggal Pesan'])
        temp_df.loc[0] = [f"Obat '{str(nama_obat_input).title()}' tidak ditemukan.", "", ""]
        return temp_df


def isi_textbox_dari_dropdown(pilihan_dropdown):
    if pilihan_dropdown == "-": 
        return "" 
    return pilihan_dropdown 


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

        dropdown_obat_gradio.change(fn=isi_textbox_dari_dropdown, inputs=dropdown_obat_gradio, outputs=input_obat_gradio)
        cari_btn_gradio.click(fn=cari_obat_gradio, inputs=input_obat_gradio, outputs=hasil_pencarian_df_gradio)

    gr.Markdown("---")
    gr.Markdown("Visualisasi keseluruhan struktur data obat (BST) telah dibuat dan disimpan sebagai `bst_keseluruhan_matplotlib.png` saat aplikasi dimulai (jika data tersedia).")


if __name__ == "__main__":
    print("\n--- Membuat Visualisasi BST Keseluruhan (Matplotlib) ---")
    visualize_bst_matplotlib(root, filename="obat.png", title="BST Obat Keseluruhan") 

    print("\n--- Menjalankan Aplikasi Web Gradio untuk Pencarian Data ---")
    print("Buka browser Anda dan navigasi ke URL yang ditampilkan di bawah ini.")
    demo.launch()
    
    