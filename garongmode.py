import requests
import time
from datetime import datetime
import os
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# URL dari file di GitHub
url = "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt"

# Path file penyimpanan tunggal dan metadata
save_path = "/data/data/com.termux/files/home/storage/shared/Proxy/file_proxy.txt"
metadata_path = "/data/data/com.termux/files/home/storage/shared/Proxy/metadata.txt"

# Setup logging
logging.basicConfig(
    filename="download_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

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

# Setup session dengan retry
def requests_session_with_retries(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# Fungsi untuk mendownload dan memperbarui file jika konten berubah
def download_file():
    session = requests_session_with_retries()  # Membuat sesi dengan retry otomatis

    try:
        old_metadata = read_metadata()
        
        # Permintaan HEAD untuk mendapatkan metadata
        response = session.head(url, timeout=10)
        response.raise_for_status()

        # Mendapatkan ETag atau Last-Modified dari header respons
        new_metadata = response.headers.get('ETag') or response.headers.get('Last-Modified')

        if old_metadata == new_metadata:
            logging.info("Konten file di sumber tidak berubah. Tidak perlu mendownload.")
            print("Konten file di sumber tidak berubah. Tidak perlu mendownload.")
            return

        # Jika berubah, unduh file baru
        logging.info("Pembaruan terdeteksi. Mengunduh file...")
        file_response = session.get(url, timeout=20)
        file_response.raise_for_status()

        # Menyimpan file dan metadata baru
        with open(save_path, 'wb') as file:
            file.write(file_response.content)

        save_metadata(new_metadata)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Menampilkan notifikasi keberhasilan di terminal dan log
        success_message = f"File berhasil diperbarui pada: {timestamp}"
        logging.info(success_message)
        print(success_message)  # Menampilkan notifikasi di terminal

    except requests.ConnectionError:
        logging.error("Kesalahan koneksi. Memastikan jaringan stabil dan mencoba ulang.")
    except requests.Timeout:
        logging.error("Permintaan melebihi batas waktu. Periksa koneksi Anda.")
    except requests.RequestException as e:
        logging.error(f"Terjadi kesalahan saat mendownload file: {e}")

# Loop untuk melakukan pengecekan dan download setiap 5 menit dengan countdown
while True:
    download_file()
    logging.info("Menunggu 5 menit sebelum pengecekan berikutnya...")

    # Countdown selama 5 menit (300 detik)
    for remaining in range(300, 0, -1):
        mins, secs = divmod(remaining, 60)
        time_format = f"{mins:02}:{secs:02}"
        print(f"\rWaktu tersisa untuk pengecekan berikutnya: {time_format}", end="")
        time.sleep(1)

    print()  # Baris baru setelah countdown selesai
