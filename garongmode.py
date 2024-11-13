import requests

# URL dari file di GitHub
url = "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt"

# Path untuk menyimpan file hasil download
save_path = "/storage/emulated/0/Proxy/file.txt"

# Mendownload file
try:
    response = requests.get(url)
    response.raise_for_status()  # Memeriksa apakah ada kesalahan dalam pengunduhan

    # Menyimpan file
    with open(save_path, 'wb') as file:
        file.write(response.content)
    print("File berhasil didownload dan disimpan di:", save_path)

except requests.exceptions.RequestException as e:
    print("Terjadi kesalahan saat mendownload file:", e)