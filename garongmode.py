import requests
import time
import os
import logging
import threading
from datetime import datetime
import re

# Konfigurasi
CHECK_INTERVAL = 300  # Waktu cek (5 menit)
URL = "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt"
SAVE_PATH = "/data/data/com.termux/files/home/storage/shared/Proxy/file_proxy.txt"
METADATA_PATH = "/data/data/com.termux/files/home/storage/shared/Proxy/metadata.txt"
METADATA_BACKUP_PATH = "/data/data/com.termux/files/home/storage/shared/Proxy/metadata_backup.txt"
VALID_PROXY_FORMATS = [r"^http://", r"^socks4://", r"^socks5://"]

# Logging setup
logging.basicConfig(
    filename="proxy_update_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Fungsi untuk membaca metadata dari file
def read_metadata():
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, 'r') as file:
            return file.read().strip()
    return None

# Fungsi untuk menyimpan metadata baru dan backup metadata lama
def save_metadata(metadata):
    if os.path.exists(METADATA_PATH):
        os.replace(METADATA_PATH, METADATA_BACKUP_PATH)  # Membuat backup
    with open(METADATA_PATH, 'w') as file:
        file.write(metadata)

# Fungsi untuk memvalidasi konten proxy
def validate_proxy_content(content):
    proxies = content.splitlines()
    valid_proxies = []
    for proxy in proxies:
        if any(re.match(fmt, proxy) for fmt in VALID_PROXY_FORMATS):
            valid_proxies.append(proxy)
    return valid_proxies

# Fungsi untuk uji konektivitas proxy (fungsi threading)
def test_proxy(proxy, active_proxies):
    proxy_type = proxy.split("://")[0]
    proxies = {proxy_type: proxy}
    try:
        response = requests.get("http://www.google.com", proxies=proxies, timeout=5)
        if response.status_code == 200:
            active_proxies.append(proxy)
            logging.info(f"Proxy aktif: {proxy}")
    except:
        logging.warning(f"Proxy tidak aktif: {proxy}")

# Fungsi untuk memfilter hanya proxy yang aktif
def filter_active_proxies(valid_proxies):
    active_proxies = []
    threads = []
    for proxy in valid_proxies:
        thread = threading.Thread(target=test_proxy, args=(proxy, active_proxies))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    return active_proxies

# Fungsi untuk mendownload dan memperbarui file jika konten berubah
def download_file():
    try:
        old_metadata = read_metadata()

        # Mendapatkan metadata terbaru melalui HEAD
        response = requests.head(URL, timeout=10)
        response.raise_for_status()

        # Menggunakan ETag atau Last-Modified untuk metadata
        new_metadata = response.headers.get('ETag') or response.headers.get('Last-Modified')

        # Cek apakah konten berubah
        if new_metadata == old_metadata:
            logging.info("Konten tidak berubah. Tidak perlu mengunduh ulang.")
            print("\nKonten tidak berubah. Tidak perlu mengunduh ulang.")
            return

        # Mengunduh konten baru
        response = requests.get(URL, timeout=10)
        response.raise_for_status()

        # Validasi konten yang diunduh
        valid_proxies = validate_proxy_content(response.text)
        if not valid_proxies:
            logging.warning("Konten yang diunduh tidak valid atau tidak mengandung proxy yang sesuai format.")
            print("\nKonten yang diunduh tidak valid.")
            return

        # Filter hanya proxy yang aktif
        active_proxies = filter_active_proxies(valid_proxies)
        if not active_proxies:
            logging.warning("Tidak ada proxy aktif yang ditemukan setelah uji koneksi.")
            print("\nTidak ada proxy aktif yang ditemukan.")
            return

        # Simpan konten yang valid dan aktif ke file
        os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
        with open(SAVE_PATH, 'w') as file:
            file.write("\n".join(active_proxies))

        # Update metadata setelah berhasil menyimpan
        save_metadata(new_metadata)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"File berhasil diperbarui pada {timestamp}")
        print(f"\nFile berhasil diperbarui pada: {timestamp}")

    except requests.ConnectionError:
        logging.error("Koneksi internet gagal.")
        print("\nKoneksi internet gagal.")
    except requests.Timeout:
        logging.error("Permintaan ke server waktu habis.")
        print("\nPermintaan ke server waktu habis.")
    except requests.HTTPError as e:
        logging.error(f"HTTP error: {e}")
        print(f"\nHTTP error: {e}")
    except Exception as e:
        logging.error(f"Kesalahan umum: {e}")
        print(f"\nKesalahan umum: {e}")

# Fungsi untuk menunggu interval dengan countdown
def wait_interval():
    print("Menunggu 5 menit sebelum pengecekan berikutnya...")
    for remaining in range(CHECK_INTERVAL, 0, -1):
        mins, secs = divmod(remaining, 60)
        time_format = f"{mins:02}:{secs:02}"
        print(f"\rWaktu tersisa untuk pengecekan berikutnya: {time_format}", end="", flush=True)
        time.sleep(1)
    print()

# Loop utama untuk melakukan pengecekan secara berkala
while True:
    download_file()
    wait_interval()
