#!/usr/bin/env python3
import urllib.request
import re
import os

# URL playlist asli
PLAYLIST_URL = "https://raw.githubusercontent.com/dhasap/dhanytv/main/dhanytv.m3u"

# Daftar channel yang diinginkan (sesuai nama yang muncul di #EXTINF)
CHANNEL_NAMES = {
    "TVRI (Piala Dunia 2026)",
    "TVRI Sports (Piala Dunia 2026)",
    "TransTV HD",
    "Trans7 HD",
    "Metro TV",
    "RCTI HD (V+)",
    "MNC TV (V+)",
    "GTV (V+)",
    "Indosiar (V+)",
    "SCTV (V+)",
    "Kompas TV HD (V+)",
    "CNN Indonesia",
    "TVOne (V+)",
    "RTV",
    "ANTV HD (V+)",
    "HBO",
    "HBO Hits",
    "HBO Family",
    "Cinemax",
    "Hits (V+)",
    "HitsMovies (V+)",
    "STUDIO UNIVERSAL (V+)",
    "AXN (V+)",
    "BBC Earth (V+)",
    "History HD (V+)",
    "Discovery Channel",
    "Warner TV",
}

def fetch_playlist(url):
    """Ambil konten playlist dari URL."""
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Gagal mengunduh playlist: {e}")
        return None

def parse_and_filter(content):
    """
    Parsing konten M3U, mengelompokkan setiap entri channel (properti + URL),
    lalu hanya menyimpan channel yang namanya ada di CHANNEL_NAMES.
    """
    lines = content.splitlines()
    filtered_blocks = []
    current_block = []
    inside_entry = False

    for line in lines:
        stripped = line.strip()
        # Abaikan baris kosong, tapi pertahankan sebagai pemisah? Kita akan skip.
        if not stripped:
            continue

        # Jika baris adalah #EXTINF atau baris properti (dimulai dengan #),
        # maka itu bagian dari entri channel.
        if stripped.startswith('#'):
            # Mulai blok baru jika sebelumnya tidak ada blok atau baris sebelumnya adalah URL?
            # Kita akan mengumpulkan semua baris yang dimulai dengan # sampai bertemu baris bukan # (URL).
            # Jadi kita kumpulkan ke current_block.
            current_block.append(stripped)
            inside_entry = True
        else:
            # Baris yang tidak dimulai dengan # dianggap sebagai URL, akhiri blok.
            if inside_entry:
                current_block.append(stripped)  # tambahkan URL
                # Sekarang kita punya blok lengkap, periksa apakah nama channel ada di daftar
                # Nama channel ada di baris #EXTINF setelah koma terakhir
                for block_line in current_block:
                    if block_line.startswith('#EXTINF'):
                        # Ambil nama setelah koma terakhir
                        match = re.search(r',([^,]+)$', block_line)
                        if match:
                            channel_name = match.group(1).strip()
                            if channel_name in CHANNEL_NAMES:
                                filtered_blocks.append(current_block)
                                break
                # Reset untuk blok berikutnya
                current_block = []
                inside_entry = False
            else:
                # Baris URL tanpa header sebelumnya? (jarang terjadi) abaikan
                continue

    # Jika ada sisa blok (misal EOF tanpa URL), tapi tidak mungkin
    return filtered_blocks

def save_playlist(blocks, output_file="my_channels.m3u"):
    """Simpan blok yang sudah difilter ke file M3U dengan header."""
    with open(output_file, 'w', encoding='utf-8') as f:
        # Tulis header (ambil dari baris pertama konten asli, atau hardcode)
        f.write('#EXTM3U url-tvg="https://raw.githubusercontent.com/dhasap/dhanytv/main/epg.xml"\n\n')
        for block in blocks:
            for line in block:
                f.write(line + '\n')
            f.write('\n')  # tambahkan baris kosong antar channel agar rapi
    print(f"Playlist berhasil disimpan ke {output_file}")

def main():
    print("Mengunduh playlist asli...")
    content = fetch_playlist(PLAYLIST_URL)
    if not content:
        return

    print("Memfilter channel yang dipilih...")
    blocks = parse_and_filter(content)
    if not blocks:
        print("Tidak ada channel yang cocok ditemukan. Periksa nama channel.")
        return

    print(f"Ditemukan {len(blocks)} channel.")
    save_playlist(blocks)

if __name__ == "__main__":
    main()