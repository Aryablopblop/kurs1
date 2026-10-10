import json
import math
import time
import urllib.request

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Kurs cadangan (terhadap 1 USD). Angka hanya contoh, bukan kurs sebenarnya.
# Dipakai kalau API gagal dan belum ada kurs yang pernah berhasil diambil.
KURS_CADANGAN = {
    "USD": 1.0,
    "IDR": 16000.0,
    "EUR": 0.92,
    "JPY": 150.0,
    "SGD": 1.35,
}

# Ganti sesuai dokumentasi API kurs yang kamu pakai (mis. Frankfurter).
# Kalau URL salah atau API gagal, program tetap jalan dengan kurs cache/cadangan.
API_URL = "https://api.frankfurter.dev/v1/latest?base=USD"

# Kurs dianggap masih segar selama 10 menit (600 detik).
MASA_CACHE = 600

# Tempat menyimpan kurs terakhir yang berhasil diambil dari API.
cache = {"kurs": None, "waktu": 0.0}


def ambil_dari_api():
    """Panggil API kurs, kembalikan dictionary {kode_mata_uang: kurs terhadap USD}."""
    with urllib.request.urlopen(API_URL, timeout=5) as respons:
        data = json.load(respons)
    kurs = dict(data["rates"])
    kurs["USD"] = 1.0  # API biasanya tidak menyertakan mata uang dasarnya
    return kurs


def dapatkan_kurs():
    """Kembalikan (kurs, sumber). Sumber: 'api', 'cache', atau 'cadangan'."""
    sekarang = time.time()

    # 1. Pakai cache kalau masih segar
    if cache["kurs"] and sekarang - cache["waktu"] < MASA_CACHE:
        return cache["kurs"], "api"

    # 2. Coba ambil kurs terbaru dari API
    try:
        kurs = ambil_dari_api()
        cache["kurs"] = kurs
        cache["waktu"] = sekarang
        return kurs, "api"
    except Exception:
        # 3. API gagal: pakai kurs terakhir yang tersimpan kalau ada
        if cache["kurs"]:
            return cache["kurs"], "cache"
        # 4. Belum pernah berhasil: pakai kurs cadangan
        return KURS_CADANGAN, "cadangan"


def hitung(jumlah, asal, tujuan, kurs):
    """Ubah ke USD dulu, lalu ke mata uang tujuan."""
    return jumlah / kurs[asal] * kurs[tujuan]


def pesan_error(teks, kode=400):
    return jsonify({"error": teks}), kode


@app.route("/")
def beranda():
    return render_template("index.html")


@app.route("/api/kurs")
def api_kurs():
    kurs, sumber = dapatkan_kurs()
    return jsonify({"mata_uang": sorted(kurs.keys()), "sumber": sumber})


@app.route("/api/konversi", methods=["POST"])
def api_konversi():
    data = request.get_json(silent=True) or {}

    # Validasi jumlah
    try:
        jumlah = float(data.get("jumlah"))
    except (TypeError, ValueError):
        return pesan_error("Jumlah harus berupa angka")
    if not math.isfinite(jumlah) or jumlah <= 0:
        return pesan_error("Jumlah harus lebih dari 0")

    # Validasi mata uang
    kurs, sumber = dapatkan_kurs()
    asal = str(data.get("asal", "")).upper()
    tujuan = str(data.get("tujuan", "")).upper()
    if asal not in kurs or tujuan not in kurs:
        return pesan_error("Mata uang tidak dikenal")

    hasil = hitung(jumlah, asal, tujuan, kurs)
    return jsonify(
        {
            "hasil": hasil,
            "kurs": kurs[tujuan] / kurs[asal],
            "sumber": sumber,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
