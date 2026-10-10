# Konversi Mata Uang

Website konversi mata uang. Backend memakai Python (Flask), frontend memakai HTML, CSS, dan JavaScript.

## Cara menjalankan

1. Pasang Flask:

       pip install -r requirements.txt

2. Jalankan server dari folder ini:

       python app.py

3. Buka http://127.0.0.1:5000 di browser.

## Struktur

    konversi-mata-uang/
    |-- app.py               backend: route, cache kurs, validasi, perhitungan
    |-- requirements.txt
    |-- templates/
    |   `-- index.html       halaman utama
    `-- static/
        |-- style.css        tampilan
        `-- script.js        validasi form, panggil backend, riwayat

## Alur singkat

1. Browser membuka `/`, lalu JavaScript memanggil `GET /api/kurs` untuk mengisi daftar mata uang.
2. Pengguna mengisi form, lalu JavaScript memvalidasi jumlah dan memanggil `POST /api/konversi`.
3. Backend memvalidasi lagi, mengambil kurs (API, cache, atau cadangan), menghitung hasil, dan mengirim JSON.
4. JavaScript menampilkan hasil dan menyimpan riwayat di browser (localStorage).

## Catatan

- `API_URL` di `app.py` perlu dicocokkan dengan dokumentasi API kurs yang dipakai.
- Angka di `KURS_CADANGAN` hanya contoh, bukan kurs sebenarnya.
