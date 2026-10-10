import json
import math
import time
import urllib.request

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


KURS_CADANGAN = {
    "USD": 1.0,
    "IDR": 16000.0,
    "EUR": 0.92,
    "JPY": 150.0,
    "SGD": 1.35,
}


API_URL = "https://api.frankfurter.dev/v1/latest?base=USD"


MASA_CACHE = 600


cache = {"kurs": None, "waktu": 0.0}


def ambil_dari_api():
    """Panggil API kurs, kembalikan dictionary {kode_mata_uang: kurs terhadap USD}."""
   
    permintaan = urllib.request.Request(
        API_URL, headers={"User-Agent": "Mozilla/5.0 (tugas-alpro-konversi)"}
    )
    with urllib.request.urlopen(permintaan, timeout=10) as respons:
        data = json.load(respons)
    kurs = dict(data["rates"])
    kurs["USD"] = 1.0  
    return kurs


def dapatkan_kurs():
    """Kembalikan (kurs, sumber). Sumber: 'api', 'cache', atau 'cadangan'."""
    sekarang = time.time()

    
    if cache["kurs"] and sekarang - cache["waktu"] < MASA_CACHE:
        return cache["kurs"], "api"

  
    try:
        kurs = ambil_dari_api()
        cache["kurs"] = kurs
        cache["waktu"] = sekarang
        return kurs, "api"
    except Exception as error:    
        print("API gagal dipanggil:", error)
        if cache["kurs"]:
            return cache["kurs"], "cache"
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

 
    try:
        jumlah = float(data.get("jumlah"))
    except (TypeError, ValueError):
        return pesan_error("Jumlah harus berupa angka")
    if not math.isfinite(jumlah) or jumlah <= 0:
        return pesan_error("Jumlah harus lebih dari 0")

  
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
