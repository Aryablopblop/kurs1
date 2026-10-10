// Ambil elemen-elemen dari halaman
const form = document.getElementById("form-konversi");
const inputJumlah = document.getElementById("jumlah");
const pilihAsal = document.getElementById("asal");
const pilihTujuan = document.getElementById("tujuan");
const tombolTukar = document.getElementById("tukar");
const elPesanError = document.getElementById("pesan-error");
const elStatus = document.getElementById("status");
const elHasilPetunjuk = document.getElementById("hasil-petunjuk");
const elHasilAngka = document.getElementById("hasil-angka");
const elHasilKurs = document.getElementById("hasil-kurs");
const elDaftarRiwayat = document.getElementById("daftar-riwayat");
const elRiwayatKosong = document.getElementById("riwayat-kosong");
const tombolHapusRiwayat = document.getElementById("hapus-riwayat");

const KUNCI_RIWAYAT = "riwayat-konversi";
const MAKS_RIWAYAT = 5;

const TEKS_STATUS = {
  api: "Kurs dari API",
  cache: "Kurs dari cache (API gagal)",
  cadangan: "Kurs cadangan (angka contoh)",
};

let riwayat = bacaRiwayat();

// ---------- Fungsi bantu ----------

function formatAngka(angka) {
  // Angka kecil butuh lebih banyak desimal supaya tidak tampil 0
  const desimal = angka >= 1 ? 2 : 6;
  return new Intl.NumberFormat("id-ID", { maximumFractionDigits: desimal }).format(angka);
}

function tampilkanError(teks) {
  elPesanError.textContent = teks;
  elPesanError.hidden = teks === "";
}

function perbaruiStatus(sumber) {
  elStatus.textContent = TEKS_STATUS[sumber] || "Kurs tidak diketahui";
  elStatus.className = "status status-" + sumber;
}

function bacaRiwayat() {
  try {
    return JSON.parse(localStorage.getItem(KUNCI_RIWAYAT)) || [];
  } catch (e) {
    return [];
  }
}

function simpanRiwayat() {
  try {
    localStorage.setItem(KUNCI_RIWAYAT, JSON.stringify(riwayat));
  } catch (e) {
    // Penyimpanan tidak tersedia: riwayat hanya hidup selama halaman terbuka
  }
}

// ---------- Tampilan ----------

function tampilkanHasil(item, kurs) {
  elHasilPetunjuk.hidden = true;

  elHasilAngka.hidden = false;
  elHasilAngka.textContent = formatAngka(item.hasil);
  const kode = document.createElement("span");
  kode.className = "kode";
  kode.textContent = item.tujuan;
  elHasilAngka.appendChild(kode);

  elHasilKurs.hidden = false;
  elHasilKurs.textContent =
    formatAngka(item.jumlah) + " " + item.asal + " pada kurs 1 " + item.asal +
    " = " + formatAngka(kurs) + " " + item.tujuan;
}

function gambarRiwayat() {
  elDaftarRiwayat.textContent = "";
  for (const item of riwayat) {
    const li = document.createElement("li");
    li.textContent =
      formatAngka(item.jumlah) + " " + item.asal + " = " +
      formatAngka(item.hasil) + " " + item.tujuan;
    elDaftarRiwayat.appendChild(li);
  }
  const adaRiwayat = riwayat.length > 0;
  elRiwayatKosong.hidden = adaRiwayat;
  tombolHapusRiwayat.hidden = !adaRiwayat;
}

// ---------- Memuat daftar mata uang dari backend ----------

async function muatMataUang() {
  try {
    const respons = await fetch("/api/kurs");
    const data = await respons.json();

    for (const kode of data.mata_uang) {
      pilihAsal.add(new Option(kode, kode));
      pilihTujuan.add(new Option(kode, kode));
    }
    // Pilihan awal: USD ke IDR (kalau ada)
    if (data.mata_uang.includes("USD")) pilihAsal.value = "USD";
    if (data.mata_uang.includes("IDR")) pilihTujuan.value = "IDR";

    perbaruiStatus(data.sumber);
  } catch (e) {
    elStatus.textContent = "Server tidak terhubung";
    elStatus.className = "status status-cadangan";
    tampilkanError("Tidak dapat memuat daftar mata uang. Pastikan server Flask sedang berjalan.");
  }
}

// ---------- Aksi pengguna ----------

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  tampilkanError("");

  // Validasi di sisi frontend
  const jumlah = parseFloat(inputJumlah.value);
  if (Number.isNaN(jumlah) || jumlah <= 0) {
    tampilkanError("Jumlah harus berupa angka lebih dari 0.");
    return;
  }
  if (!pilihAsal.value || !pilihTujuan.value) {
    tampilkanError("Pilih mata uang asal dan tujuan.");
    return;
  }

  try {
    const respons = await fetch("/api/konversi", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jumlah: jumlah,
        asal: pilihAsal.value,
        tujuan: pilihTujuan.value,
      }),
    });
    const data = await respons.json();

    if (!respons.ok) {
      tampilkanError(data.error || "Terjadi kesalahan saat konversi.");
      return;
    }

    const item = {
      jumlah: jumlah,
      asal: pilihAsal.value,
      tujuan: pilihTujuan.value,
      hasil: data.hasil,
    };
    tampilkanHasil(item, data.kurs);
    perbaruiStatus(data.sumber);

    riwayat.unshift(item);
    riwayat = riwayat.slice(0, MAKS_RIWAYAT);
    simpanRiwayat();
    gambarRiwayat();
  } catch (err) {
    tampilkanError("Tidak dapat terhubung ke server. Coba lagi.");
  }
});

tombolTukar.addEventListener("click", () => {
  const sementara = pilihAsal.value;
  pilihAsal.value = pilihTujuan.value;
  pilihTujuan.value = sementara;
});

tombolHapusRiwayat.addEventListener("click", () => {
  riwayat = [];
  simpanRiwayat();
  gambarRiwayat();
});

// ---------- Mulai ----------

gambarRiwayat();
muatMataUang();
