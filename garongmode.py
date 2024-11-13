import requests
import os
import time
from datetime import datetime
import base64
import logging
import re

# Setup logging
logging.basicConfig(filename="auto_update_log.txt", level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Token GitHub Anda (Pastikan token ini tidak dibagikan secara publik)
GITHUB_TOKEN = "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"

# Nama repository GitHub Anda dan nama file yang ingin diupdate
REPO_OWNER = "LadyJ01"  # Ganti dengan username Anda
REPO_NAME = "BETAV1"  # Ganti dengan nama repo V1 Anda
FILE_PATH_GITHUB = "local_proxies.txt"  # File yang akan diperbarui di GitHub
BRANCH_NAME = "main"  # Nama branch (biasanya 'main' atau 'master')

# Path file lokal yang ingin digunakan untuk pembaruan
LOCAL_FILE_PATH = "/data/data/com.termux/files/home/storage/shared/Proxy/file_proxy.txt"

# Fungsi untuk membaca konten dari file lokal
def read_local_file():
    try:
        with open(LOCAL_FILE_PATH, 'r') as file:
            return file.read()
    except FileNotFoundError:
        logging.error(f"File lokal tidak ditemukan: {LOCAL_FILE_PATH}")
        raise
    except Exception as e:
        logging.error(f"Terjadi kesalahan saat membaca file lokal: {e}")
        raise

# Fungsi untuk mendapatkan SHA dan last_modified dari file di GitHub
def get_file_sha():
    try:
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH_GITHUB}?ref={BRANCH_NAME}"
        headers = {'Authorization': f'token {GITHUB_TOKEN}'}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            content_info = response.json()
            return content_info['sha'], content_info['last_modified']
        else:
            logging.warning(f"Gagal mengambil metadata file dari GitHub, Status Code: {response.status_code}")
            return None, None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error saat menghubungi GitHub: {e}")
        raise

# Fungsi untuk memvalidasi dan memastikan format proxy sesuai dengan http://, socks4://, socks5://
def validate_proxy_content(content):
    # Regular expression untuk HTTP, SOCKS4, SOCKS5
    proxy_pattern = r'^(http|socks4|socks5):\/\/[a-zA-Z0-9.-]+(:\d+)?$'
    valid_proxies = []

    # Memisahkan konten menjadi baris dan memvalidasi tiap baris
    for line in content.splitlines():
        line = line.strip()
        # Mengubah ke format yang sesuai
        if re.match(proxy_pattern, line):
            valid_proxies.append(line)
        else:
            logging.warning(f"Baris ini tidak valid: {line}")

    return "\n".join(valid_proxies)

# Fungsi untuk memeriksa apakah konten sudah berubah
def is_content_changed(local_content, github_content):
    if local_content != github_content:
        return True
    return False

# Fungsi untuk mengupdate file di GitHub
def update_file_on_github(content):
    sha, last_modified = get_file_sha()

    if sha:
        try:
            # Membaca waktu terakhir modifikasi file lokal
            local_modified_time = os.path.getmtime(LOCAL_FILE_PATH)
            last_modified_time = datetime.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z").timestamp()

            # Jika file lokal lebih baru, update file GitHub
            if local_modified_time > last_modified_time:
                # Validasi konten proxy
                valid_content = validate_proxy_content(content)

                # Memeriksa apakah konten berubah
                url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH_GITHUB}"
                current_content = read_local_file()  # Ambil konten GitHub yang terbaru
                if is_content_changed(valid_content, current_content):
                    # Encoding konten dalam base64
                    encoded_content = base64.b64encode(valid_content.encode('utf-8')).decode('utf-8')

                    data = {
                        "message": "Auto Update local_proxies.txt from device",
                        "content": encoded_content,
                        "sha": sha,  # SHA untuk file yang ingin diupdate
                        "branch": BRANCH_NAME
                    }

                    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
                    response = requests.put(url, json=data, headers=headers)

                    if response.status_code == 200:
                        logging.info("File berhasil diupdate di GitHub!")
                    else:
                        logging.error(f"Gagal mengupdate file GitHub. Status Code: {response.status_code}")
                        logging.error(response.text)
                else:
                    logging.info("Konten tidak berubah, tidak ada pembaruan yang diperlukan.")
            else:
                logging.info("File lokal tidak lebih baru dari file GitHub. Tidak ada pembaruan yang diperlukan.")
        except Exception as e:
            logging.error(f"Terjadi kesalahan saat mencoba memperbarui file di GitHub: {e}")
            raise
    else:
        logging.warning("SHA file GitHub tidak ditemukan. Pembaruan gagal.")

# Fungsi utama untuk memeriksa dan memperbarui file secara otomatis
def auto_update_file():
    while True:
        try:
            logging.info("Memulai pengecekan file lokal...")
            local_content = read_local_file()  # Membaca konten file lokal
            update_file_on_github(local_content)  # Memperbarui file di GitHub
        except Exception as e:
            logging.error(f"Terjadi kesalahan: {e}")

        # Tunggu selama 5 menit (300 detik) sebelum memeriksa pembaruan lagi
        logging.info("Menunggu 5 menit sebelum pengecekan berikutnya...")
        time.sleep(300)  # Menunggu 5 menit

if __name__ == "__main__":
    logging.info("Memulai auto-update script...")
    auto_update_file()
