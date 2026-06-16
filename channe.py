#!/usr/bin/env python3
import urllib.request
import re
import sys

# URL playlist asli
PLAYLIST_URL = "https://raw.githubusercontent.com/dhasap/dhanytv/main/dhanytv.m3u"

# Daftar channel yang diinginkan - PASTIKAN NAMA SAMA PERSIS dengan di playlist!
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
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"ERROR: Gagal mengunduh playlist: {e}")
        sys.exit(1)

def parse_and_filter(content):
    lines = content.splitlines()
    filtered_blocks = []
    current_block = []
    inside_entry = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('#'):
            current_block.append(stripped)
            inside_entry = True
        else:
            if inside_entry:
                current_block.append(stripped)
                # Cek nama channel
                found = False
                for block_line in current_block:
                    if block_line.startswith('#EXTINF'):
                        match = re.search(r',([^,]+)$', block_line)
                        if match:
                            channel_name = match.group(1).strip()
                            if channel_name in CHANNEL_NAMES:
                                filtered_blocks.append(current_block)
                                found = True
                                break
                # Reset untuk blok berikutnya
                current_block = []
                inside_entry = False
            else:
                continue

    # Jika tidak ada channel ditemukan, tampilkan daftar nama yang ada di playlist
    if not filtered_blocks:
        print("ERROR: Tidak ada channel yang cocok.")
        print("Channel yang ditemukan di playlist:")
        for line in lines:
            if line.startswith('#EXTINF'):
                match = re.search(r',([^,]+)$', line)
                if match:
                    print(f"  - {match.group(1).strip()}")
        sys.exit(2)  # exit code 2 untuk menunjukkan error

    return filtered_blocks

def save_playlist(blocks, output_file="my_channels.m3u"):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U url-tvg="https://raw.githubusercontent.com/dhasap/dhanytv/main/epg.xml"\n\n')
        for block in blocks:
            for line in block:
                f.write(line + '\n')
            f.write('\n')
    print(f"✅ Playlist berhasil disimpan ke {output_file}")

def main():
    print("Mengunduh playlist asli...")
    content = fetch_playlist(PLAYLIST_URL)
    print("Memfilter channel yang dipilih...")
    blocks = parse_and_filter(content)
    print(f"Ditemukan {len(blocks)} channel.")
    save_playlist(blocks)

if __name__ == "__main__":
    main()
