import requests
import time
from datetime import datetime

# URL dari file di GitHub
url = "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt"

# Folder penyimpanan
save_folder = "/data/data/com.termux/files/home/storage/shared/Proxy/"

# Fungsi untuk mendownload file dengan timestamp di namanya
def download_file():
    try:
        # Mendapatkan waktu sekarang untuk keterangan pada nama file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = f"{save_folder}file_{timestamp}.txt"

        # Mendownload file
        response = requests.get(url)
        response.raise_for_status()  # Memeriksa apakah ada kesalahan dalam pengunduhan

        # Menyimpan file dengan timestamp di nama file
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"File berhasil didownload dan disimpan di: {save_path}")

    except requests.exceptions.RequestException as e:
        print("Terjadi kesalahan saat mendownload file:", e)

# Loop untuk melakukan download setiap 5 menit
while True:
    download_file()
    print("Menunggu 5 menit sebelum download berikutnya...")
    time.sleep(300)  # Menunggu 300 detik (5 menit)
