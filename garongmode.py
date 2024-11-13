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
        print(f"\nFile berhasil didownload dan disimpan di: {save_path}")

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
