import requests
import time
from datetime import datetime
import os

# URL dari file di GitHub
url = "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt"

# Path file penyimpanan tunggal dan metadata
save_path = "/data/data/com.termux/files/home/storage/shared/Proxy/file_proxy.txt"
metadata_path = "/data/data/com.termux/files/home/storage/shared/Proxy/metadata.txt"

# Fungsi untuk membaca metadata dari file metadata
def read_metadata():
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as file:
            return file.read().strip()
    return None

# Fungsi untuk menyimpan metadata ke file
def save_metadata(metadata):
    with open(metadata_path, 'w') as file:
        file.write(metadata)

# Fungsi untuk mendownload dan memperbarui file jika konten berubah
def download_file():
    try:
        # Membaca metadata sebelumnya
        old_metadata = read_metadata()

        # Melakukan permintaan HEAD untuk mendapatkan metadata terbaru
        response = requests.head(url)
        response.raise_for_status()  # Memeriksa apakah ada kesalahan

        # Mendapatkan ETag atau Last-Modified dari header respons
        new_metadata = response.headers.get('ETag') or response.headers.get('Last-Modified')

        # Mengecek apakah metadata sudah berubah
        if new_metadata == old_metadata:
            print("\nKonten file di sumber tidak berubah. Tidak perlu mendownload.")
            return

        # Jika berubah, maka lakukan download file baru
        response = requests.get(url)
        response.raise_for_status()  # Memeriksa apakah ada kesalahan dalam pengunduhan

        # Menyimpan konten baru ke file dan memperbarui metadata
        with open(save_path, 'wb') as file:
            file.write(response.content)
        
        save_metadata(new_metadata)  # Menyimpan metadata baru
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\nFile berhasil diperbarui pada: {timestamp}")

    except requests.exceptions.RequestException as e:
        print("\nTerjadi kesalahan saat mendownload file:", e)

# Loop untuk melakukan pengecekan dan download setiap 5 menit dengan tampilan countdown
while True:
    download_file()
    print("Menunggu 5 menit sebelum pengecekan berikutnya...")

    # Countdown selama 5 menit (300 detik)
    for remaining in range(300, 0, -1):
        mins, secs = divmod(remaining, 60)
        time_format = f"{mins:02}:{secs:02}"
        print(f"\rWaktu tersisa untuk pengecekan berikutnya: {time_format}", end="")
        time.sleep(1)

    print()  # Baris baru setelah countdown selesai
