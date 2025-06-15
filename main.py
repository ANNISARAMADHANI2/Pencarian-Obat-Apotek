import pandas as pd
import gradio as gr
import matplotlib.pyplot as plt # Untuk visualisasi dengan Matplotlib
import numpy as np # Diperlukan untuk beberapa kalkulasi posisi di Matplotlib

# Baca file CSV
try:
    df = pd.read_csv("Data SDA.csv")
except FileNotFoundError:
    print("Error: File 'Data SDA.csv' tidak ditemukan. Pastikan file tersebut ada di direktori yang sama.")
    df = pd.DataFrame(columns=['Nama Obat', 'Nama Pemesan', 'Kategori Penyakit', 'Tanggal Pesan'])

# Kelas Node BST
class Node:
    def __init__(self, nama_obat):
        self.nama_obat = nama_obat
        self.data = []
        self.left = None
        self.right = None
        # Atribut untuk Matplotlib (posisi x, y)
        self.x = 0
        self.y = 0

# Fungsi untuk memasukkan data ke BST
def insert(root, row):
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

# Fungsi untuk mencari data di BST
def search(root, nama_obat):
    nama_obat_key = str(nama_obat).strip().lower()
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

# Bangun BST
root = None
if not df.empty:
    for _, row in df.iterrows():
        root = insert(root, row)
else:
    print("DataFrame kosong, BST tidak dibangun.")

# Ambil daftar nama obat unik untuk dropdown
if not df.empty and 'Nama Obat' in df.columns:
    daftar_obat_unique = sorted(df['Nama Obat'].dropna().astype(str).str.strip().str.title().unique())
    daftar_obat = ["-"] + daftar_obat_unique
else:
    daftar_obat = ["-"]

# --- Fungsi untuk Visualisasi BST di Terminal (Teks, Terurut Menurun) ---
def print_tree_terminal(node, prefix="", is_last_child_from_parent=True):
    """
    Mencetak struktur pohon ke terminal secara visual,
    dengan urutan node dari terbesar ke terkecil (descending) jika dibaca dari atas ke bawah.
    Menggunakan traversal Right-Node-Left.
    Args:
        node: Node BST saat ini.
        prefix: String untuk indentasi dan garis cabang.
        is_last_child_from_parent: Boolean, True jika 'node' ini adalah anak terakhir
                                     yang dicetak oleh parent-nya dalam urutan traversal ini.
                                     Ini menentukan jenis konektor ('L--' atau '|--').
    """
    if node is None:
        return

    # Tentukan prefix untuk anak-anak dari node saat ini.
    # Jika node saat ini adalah anak terakhir yang dicetak oleh parent-nya,
    # maka garis vertikal tidak perlu dilanjutkan untuk sibling dari node ini.
    # Sebaliknya, jika node ini bukan anak terakhir, garis vertikal ('|') harus ada.
    prefix_for_children = prefix + ("    " if is_last_child_from_parent else "|   ")

    # 1. Traverse anak kanan (nilai lebih besar)
    if node.right:
        # Anak kanan diproses terlebih dahulu. Dalam traversal Right-Node-Left,
        # anak kanan bukanlah anak "terakhir" yang diproses oleh 'node' ini
        # (karena 'node' sendiri dan anak kiri akan diproses setelahnya).
        print_tree_terminal(node.right, prefix_for_children, False)

    # 2. Cetak node saat ini
    connector = "L-- " if is_last_child_from_parent else "|-- "
    display_nama_obat = node.nama_obat.title()
    print(prefix + connector + f"{display_nama_obat} (Data: {len(node.data)})")

    # 3. Traverse anak kiri (nilai lebih kecil)
    if node.left:
        # Anak kiri diproses terakhir oleh 'node' ini.
        # Jadi, ia adalah 'last_child_from_parent' relatif terhadap 'node'.
        print_tree_terminal(node.left, prefix_for_children, True)


# --- Fungsi untuk Visualisasi BST dengan Matplotlib (Simpan ke File) ---
# Fungsi _assign_positions_recursive, _draw_tree_matplotlib_recursive, 
# visualize_bst_matplotlib, dan collect_all_nodes tetap sama.
def _assign_positions_recursive(node, x=0, y=0, x_dist=1.0, y_dist=1.0, positions=None, depth=0, x_coords_at_depth=None):
    """Helper rekursif untuk menentukan posisi node untuk Matplotlib."""
    if node is None:
        return x 

    if positions is None:
        positions = {}
    if x_coords_at_depth is None:
        x_coords_at_depth = {}

    left_x_offset = x
    if node.left:
        left_x_offset = _assign_positions_recursive(node.left, x, y - y_dist, x_dist / 2, y_dist, positions, depth + 1, x_coords_at_depth)
    
    current_x = left_x_offset
    if node.left: 
        current_x += x_dist / (2**(depth+1)) 

    while x_coords_at_depth.get(depth, -float('inf')) >= current_x :
        current_x += 0.2 

    node.x = current_x
    node.y = y
    positions[node.nama_obat] = (node.x, node.y)
    x_coords_at_depth[depth] = current_x 

    right_x_start = current_x
    if node.right:
        if node.left: 
            right_x_start += x_dist / (2**(depth+1))
        else: 
            right_x_start += x_dist / (2**(depth+1)) 
        _assign_positions_recursive(node.right, right_x_start, y - y_dist, x_dist / 2, y_dist, positions, depth + 1, x_coords_at_depth)
    
    return max(current_x, right_x_start + (x_dist / (2**(depth+1)) if node.right else 0) )


def _draw_tree_matplotlib_recursive(node, ax):
    """Helper rekursif untuk menggambar node dan edge dengan Matplotlib."""
    if node is None:
        return

    label = f"{node.nama_obat.title()}\n(Data: {len(node.data)})"
    ax.text(node.x, node.y, label, ha='center', va='center',
            bbox=dict(facecolor='skyblue', alpha=0.7, edgecolor='black', boxstyle='round,pad=0.5'))

    if node.left:
        ax.plot([node.x, node.left.x], [node.y, node.left.y], 'k-', lw=1.5, color='gray')
        _draw_tree_matplotlib_recursive(node.left, ax)
    if node.right:
        ax.plot([node.x, node.right.x], [node.y, node.right.y], 'k-', lw=1.5, color='gray')
        _draw_tree_matplotlib_recursive(node.right, ax)

def visualize_bst_matplotlib(tree_root, filename="bst_matplotlib.png", title="Visualisasi BST"):
    """Membuat visualisasi BST menggunakan Matplotlib dan menyimpannya ke file."""
    if tree_root is None:
        print(f"Pohon ({title}) kosong, tidak ada yang divisualisasikan dengan Matplotlib.")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.text(0.5, 0.5, f"{title} Kosong", ha='center', va='center', fontsize=12)
        ax.axis('off')
        plt.title(title)
        plt.savefig(filename)
        plt.close(fig)
        print(f"Gambar '{filename}' untuk pohon kosong telah disimpan.")
        return

    fig, ax = plt.subplots(figsize=(15, 10)) 
    
    node_positions = {}
    x_coords_by_depth = {} 
    
    max_depth = [0]
    def get_max_depth(node, current_depth):
        if not node: return
        max_depth[0] = max(max_depth[0], current_depth)
        get_max_depth(node.left, current_depth + 1)
        get_max_depth(node.right, current_depth + 1)
    get_max_depth(tree_root, 0)

    current_x = [0] 
    def assign_xy(node, depth=0, y_spacing=1):
        if not node:
            return
        
        assign_xy(node.left, depth + 1, y_spacing)
        
        node.x = current_x[0]
        node.y = -depth * y_spacing 
        current_x[0] += 1 
        
        assign_xy(node.right, depth + 1, y_spacing)

    assign_xy(tree_root) 

    _draw_tree_matplotlib_recursive(tree_root, ax)

    all_x = [n.x for n in collect_all_nodes(tree_root)]
    all_y = [n.y for n in collect_all_nodes(tree_root)]
    if all_x and all_y:
        ax.set_xlim(min(all_x) - 1, max(all_x) + 1)
        ax.set_ylim(min(all_y) - 1, max(all_y) + 1)
    
    ax.axis('off') 
    plt.title(title, fontsize=16)
    plt.savefig(filename)
    plt.close(fig) 
    print(f"Visualisasi Matplotlib '{title}' disimpan sebagai '{filename}'")

def collect_all_nodes(node, nodes_list=None):
    """Mengumpulkan semua node dalam pohon (untuk mendapatkan batas plot)."""
    if nodes_list is None:
        nodes_list = []
    if node:
        nodes_list.append(node)
        collect_all_nodes(node.left, nodes_list)
        collect_all_nodes(node.right, nodes_list)
    return nodes_list


# Fungsi pencarian untuk Gradio
def cari_obat_gradio(nama_obat_input):
    if not nama_obat_input or str(nama_obat_input).strip() == "-" or not str(nama_obat_input).strip():
        return pd.DataFrame([{
            "Nama Pemesan": "Silakan pilih atau ketik nama obat untuk dicari.",
            "Kategori Penyakit": "",
            "Tanggal Pesan": ""
        }])
    
    node_hasil = search(root, str(nama_obat_input))
    if node_hasil:
        hasil_df = pd.DataFrame(node_hasil.data)
        kolom_tampil = ['Nama Pemesan', 'Kategori Penyakit', 'Tanggal Pesan']
        for kol in kolom_tampil:
            if kol not in hasil_df.columns:
                hasil_df[kol] = ""
        return hasil_df[kolom_tampil]
    else:
        return pd.DataFrame([{
            "Nama Pemesan": f"Obat '{str(nama_obat_input)}' tidak ditemukan.",
            "Kategori Penyakit": "",
            "Tanggal Pesan": ""
        }])

# Fungsi untuk mengisi textbox dari dropdown
def isi_textbox_dari_dropdown(pilihan_dropdown):
    if pilihan_dropdown == "-":
        return ""
    return pilihan_dropdown


# Gradio interface (hanya untuk pencarian data)
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# ⚕️ Pencarian Data Pemesan Obat Apotek ⚕️")
    gr.Markdown("Aplikasi ini memungkinkan Anda mencari data pemesan obat.")

    with gr.TabItem("Pencarian Obat"):
        gr.Markdown("## 🔍 Cari Pemesan Obat")
        with gr.Row():
            input_obat = gr.Textbox(label="Ketik Nama Obat", placeholder="Contoh: Paracetamol")
            dropdown_obat = gr.Dropdown(choices=daftar_obat, label="Atau Pilih dari Daftar", value="-")
        
        cari_btn = gr.Button("Cari Data", variant="primary")
        
        gr.Markdown("### Hasil Pencarian:")
        hasil_pencarian_df = gr.DataFrame(
            headers=['Nama Pemesan', 'Kategori Penyakit', 'Tanggal Pesan'],
            label="Detail Pesanan"
        )
        
        dropdown_obat.change(fn=isi_textbox_dari_dropdown, inputs=dropdown_obat, outputs=input_obat)
        cari_btn.click(fn=cari_obat_gradio, inputs=input_obat, outputs=hasil_pencarian_df)

# --- Bagian untuk demonstrasi output terminal dan Matplotlib ---
if __name__ == "__main__":
    print("\n--- Visualisasi BST Keseluruhan (Terminal - Terurut Menurun) ---")
    if root:
        # Panggilan awal untuk root, dianggap sebagai 'last_child_from_parent' 
        # agar tidak ada konektor yang tidak perlu di level paling atas.
        print_tree_terminal(root, prefix="", is_last_child_from_parent=True)
    else:
        print("BST kosong.")
    
    print("\n--- Membuat Visualisasi BST Keseluruhan (Matplotlib) ---")
    visualize_bst_matplotlib(root, filename="bst_keseluruhan_matplotlib.png", title="BST Obat Keseluruhan")

    # Contoh pencarian dan visualisasi subtree
    nama_obat_dicari = "Paracetamol" # Ganti dengan nama obat yang ada di data Anda untuk tes
    print(f"\n--- Mencari '{nama_obat_dicari}' dan Visualisasi Subtree-nya (Terminal - Terurut Menurun) ---")
    node_hasil_pencarian = search(root, nama_obat_dicari)

    if node_hasil_pencarian:
        print(f"\nSubtree untuk '{nama_obat_dicari.title()}' (Terminal - Terurut Menurun):")
        print_tree_terminal(node_hasil_pencarian, prefix="", is_last_child_from_parent=True)
        
        print(f"\nMembuat Visualisasi Subtree untuk '{nama_obat_dicari.title()}' (Matplotlib):")
        visualize_bst_matplotlib(node_hasil_pencarian, 
                                 filename=f"subtree_{nama_obat_dicari.lower().replace(' ','_')}_matplotlib.png",
                                 title=f"Subtree Obat: {nama_obat_dicari.title()}")
    else:
        print(f"Obat '{nama_obat_dicari}' tidak ditemukan dalam BST.")

    # Menjalankan aplikasi Gradio (jika ingin tetap ada antarmuka web untuk pencarian)
    print("\n--- Menjalankan Aplikasi Web Gradio untuk Pencarian Data ---")
    print("Visualisasi pohon telah dicetak di terminal (terurut menurun) dan/atau disimpan sebagai file gambar.")
    demo.launch()