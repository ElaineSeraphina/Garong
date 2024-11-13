import requests
import time
from datetime import datetime
import os

# URL dari file di GitHub
url = "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt"

# Path file penyimpanan tunggal
save_path = "/data/data/com.termux/files/home/storage/shared/Proxy/file_proxy.txt"

# Fungsi untuk membaca konten file
def read_file_content(file_path):
    try:
        with open(file_path, 'rb') as file:
            return file.read()
    except FileNotFoundError:
        # Jika file belum ada, maka anggap konten kosong
        return None

# Fungsi untuk mendownload dan memperbarui file jika konten berubah
def download_file():
    try:
        # Mendapatkan konten file dari URL
        response = requests.get(url)
        response.raise_for_status()  # Memeriksa apakah ada kesalahan dalam pengunduhan
        new_content = response.content

        # Mengecek konten file sebelumnya
        old_content = read_file_content(save_path)

        # Memperbarui file hanya jika konten berbeda
        if old_content == new_content:
            print("\nKonten file sama seperti sebelumnya. Tidak ada perubahan.")
        else:
            with open(save_path, 'wb') as file:
                file.write(new_content)
            # Menambahkan timestamp ke output untuk menunjukkan waktu pembaruan terakhir
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\nFile berhasil diperbarui pada: {timestamp}")

    except requests.exceptions.RequestException as e:
        print("\nTerjadi kesalahan saat mendownload file:", e)

# Loop untuk melakukan download setiap 5 menit dengan tampilan countdown
while True:
    download_file()
    print("Menunggu 5 menit sebelum download berikutnya...")

    # Countdown selama 5 menit (300 detik)
    for remaining in range(300, 0, -1):
        mins, secs = divmod(remaining, 60)
        time_format = f"{mins:02}:{secs:02}"
        print(f"\rWaktu tersisa untuk download berikutnya: {time_format}", end="")
        time.sleep(1)

    print()  # Baris baru setelah countdown selesai
