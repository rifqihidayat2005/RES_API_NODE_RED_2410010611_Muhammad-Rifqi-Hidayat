# IoT Dashboard Monitoring Sensor

Proyek demonstrasi monitoring sensor IoT menggunakan Node-RED, MQTT, SQLite,
dan dashboard web. Data suhu dan kelembaban dapat disimulasikan dari komputer,
diterima oleh Node-RED, disimpan sebagai riwayat, lalu ditampilkan pada
dashboard. Dashboard juga menyediakan pengaturan ambang sensor dan kontrol
lampu melalui MQTT.

> **Catatan biodata:** ganti semua teks `[Isi ...]` di bawah dengan data Anda
> sendiri sebelum mengunggah proyek ini ke GitHub. Jangan menambahkan data
> pribadi yang tidak ingin dipublikasikan.

## Biodata

| Informasi | Keterangan |
|---|---|
| Nama | [Muhammad Rifqi Hidayat] |
| NIM | [2410010611] |
| Program studi | [Teknik Informatika] |
| Fakultas | [Teknologi Informasi] |

## Fitur

- Menampilkan suhu dan kelembaban terbaru.
- Menampilkan status koneksi sensor dan status ambang (threshold).
- Mengatur batas suhu dan kelembaban serta menampilkan peringatan jika batas
  terlampaui.
- Menampilkan grafik 20 pembacaan sensor terakhir pada sesi halaman.
- Menyimpan dan menampilkan 10 data sensor terakhir dari SQLite.
- Mengirim perintah menyalakan atau mematikan lampu melalui MQTT.
- Menampilkan log aktivitas serta menyediakan notifikasi browser.
- Menyediakan simulator data sensor untuk pengujian tanpa perangkat ESP32.

## Struktur proyek

```text
.
├── dashboard.html       # Dashboard web mandiri (HTML, CSS, dan JavaScript)
├── flow1.json           # Flow Node-RED: MQTT, REST API, SQLite, dan dashboard
├── simulasi_esp32.py    # Simulator sensor yang mengirim data melalui MQTT
└── README.md            # Dokumentasi proyek
```

## Teknologi dan prasyarat

- Node.js dan Node-RED.
- Broker MQTT Mosquitto yang berjalan di `localhost:1883`.
- Node `node-red-node-sqlite` pada instalasi Node-RED.
- Python 3 dan paket Python `paho-mqtt`.
- Browser modern dengan akses internet untuk memuat Chart.js dari CDN.

Konfigurasi flow saat ini menggunakan Node-RED pada `http://127.0.0.1:1880`,
broker MQTT tanpa TLS pada `localhost:1883`, serta database SQLite
`./sensor.db`. Pastikan layanan-layanan tersebut berjalan pada alamat dan port
yang sesuai, atau sesuaikan konfigurasi flow dan dashboard.

## Menjalankan proyek di Windows

### 1. Siapkan broker MQTT

Pasang dan jalankan Mosquitto. Konfigurasi bawaan proyek memakai broker lokal
tanpa autentikasi pada port `1883`. Pastikan Node-RED dan simulator dapat
mengakses broker tersebut.

### 2. Siapkan Node-RED

1. Pasang `node-red-node-sqlite` melalui **Menu → Manage palette → Install**
   pada editor Node-RED jika node SQLite belum tersedia.
2. Jalankan Node-RED, lalu buka editor di `http://127.0.0.1:1880`.
3. Pilih **Menu → Import**, lalu impor file `flow1.json`.
4. Klik **Deploy**.
5. Pastikan node MQTT memakai broker `localhost:1883` dan node SQLite berhasil
   membuat atau membuka `sensor.db`.

Flow menyimpan database dengan path relatif `./sensor.db`; lokasi aktualnya
mengikuti direktori kerja/user directory Node-RED. Pastikan Node-RED memiliki
izin menulis pada lokasi tersebut.

### 3. Pasang dependensi simulator

Buka PowerShell pada direktori proyek:

```powershell
py -m pip install paho-mqtt
```

### 4. Jalankan simulator sensor

Di PowerShell pada direktori proyek:

```powershell
py .\simulasi_esp32.py
```

Simulator menerbitkan pembacaan baru setiap tiga detik. Hentikan dengan
`Ctrl+C`. Untuk menggunakan ESP32 sungguhan, perangkat harus menerbitkan
payload yang kompatibel ke topik `iot/sensor`; program firmware ESP32 tidak
termasuk dalam repository ini.

### 5. Buka dashboard

`dashboard.html` merupakan dashboard mandiri dan dapat disajikan dari direktori
proyek dengan server HTTP sederhana:

```powershell
py -m http.server 8000
```

Kemudian buka `http://127.0.0.1:8000/dashboard.html`. Dashboard memanggil API
Node-RED di `http://127.0.0.1:1880/api`.

Flow juga mempunyai halaman dashboard lain yang ditanam sebagai template
Node-RED di route `http://127.0.0.1:1880/dashboard`. Halaman route tersebut
berasal dari node template di `flow1.json`, bukan dari file `dashboard.html`.

## Alur data

1. Simulator membuat nilai suhu dan kelembaban acak beserta timestamp.
2. Simulator menerbitkannya sebagai JSON ke topik MQTT `iot/sensor`.
3. Node-RED menerima pesan, menambahkan waktu penerimaan, dan menyimpan data
   terbaru pada flow context.
4. Flow memproses pembacaan untuk penyimpanan SQLite, pengiriman data melalui
   WebSocket, dan pemeriksaan ambang suhu.
5. Dashboard mandiri mengambil pembacaan terbaru dan riwayat melalui REST API.
6. Ketika pengguna mengirim perintah kontrol, Node-RED meneruskan pesannya ke
   topik `iot/kontrol`. Perangkat yang mendengarkan topik tersebut dapat
   menjalankan aksi terkait.

## Penjelasan kode

### `dashboard.html`

File ini memuat keseluruhan antarmuka mandiri: markup HTML, gaya CSS, dan
JavaScript.

**Bagian HTML dan CSS**

- Ringkasan kartu menampilkan suhu, kelembaban, status sensor, dan status
  threshold.
- Form threshold menerima batas suhu dan kelembaban.
- Panel peringatan menyediakan status peringatan dan tombol izin notifikasi
  browser.
- Elemen grafik memakai elemen `<canvas>` dan Chart.js.
- Panel kontrol menyediakan tombol lampu, tabel riwayat, dan area log.
- CSS mengatur warna status, tata letak panel/kartu, grafik, tabel, tombol, dan
  penyesuaian tampilan untuk layar kecil.

**Bagian JavaScript**

- `API_BASE` menentukan alamat API Node-RED; `API_KEY` mengisi header
  `x-api-key` pada permintaan API.
- `aktifkanNotifikasi()` meminta izin notifikasi browser, sedangkan
  `kirimNotifikasi()` menampilkan notifikasi jika izin telah diberikan.
- Inisialisasi `sensorChart` menyiapkan grafik garis suhu dan kelembaban.
- `getHeaders()` membentuk header JSON dan API key.
- `log()` menambahkan pesan bertimestamp ke panel log.
- `updateStatus(online)` mengubah indikator sensor online/offline.
- `simpanThreshold()` memvalidasi nilai batas, lalu mengirim batas suhu ke API
  `PUT /api/threshold`. Batas kelembaban saat ini hanya disimpan di memori
  halaman dan tidak dikirim ke Node-RED.
- `cekThreshold(suhu, kelembaban)` membandingkan data dengan kedua batas,
  memperbarui badge/peringatan, mencatat perubahan status, dan memicu notifikasi.
- `updateChart()` menambahkan pembacaan ke grafik dan mempertahankan maksimal
  20 titik.
- `fetchSensor()` mengambil data terbaru dari `GET /api/suhu`, memvalidasi
  angka, lalu memperbarui tampilan, threshold, dan grafik.
- `fetchHistory()` mengambil riwayat dari `GET /api/history`, kemudian membuat
  baris tabel untuk maksimal 10 data. Sel tabel dibuat sebagai elemen DOM dan
  nilainya ditambahkan sebagai teks.
- `kontrol(device, action)` mengirim perintah JSON ke `POST /api/kontrol`.
- Saat halaman dimulai, dashboard langsung mengambil sensor dan riwayat,
  selanjutnya mengambil data sensor setiap 3 detik dan riwayat setiap 5 detik.

### `simulasi_esp32.py`

1. Mengimpor pustaka MQTT, JSON, waktu, angka acak, dan tanggal/waktu.
2. Menetapkan broker `localhost:1883` dan topik `iot/sensor` serta
   `iot/kontrol`.
3. Membuat client MQTT dan menghubungkan ke broker.
4. Di dalam loop, menghasilkan suhu acak `25–32 °C`, kelembaban acak
   `55–80%`, dan timestamp ISO; data diubah menjadi JSON dan diterbitkan setiap
   tiga detik.
5. `Ctrl+C` menghentikan simulasi. Blok `finally` menghentikan loop MQTT dan
   menutup koneksi.

Program ini hanya mensimulasikan pengiriman data sensor. Program belum
berlangganan ke `iot/kontrol` dan tidak mengendalikan perangkat fisik.

### `flow1.json`

File ini adalah ekspor flow Node-RED. Komponen utamanya:

- **MQTT sensor** berlangganan ke `iot/sensor`, mem-parsing data, menambahkan
  waktu penerimaan, dan menyimpan pembacaan terbaru pada flow context.
- **Proses sensor** memeriksa nilai suhu/kelembaban, menulis riwayat ke
  `sensor_history` pada SQLite, mengirim data sensor ke WebSocket `/ws/sensor`,
  dan menerbitkan notifikasi MQTT ke `iot/notifikasi` ketika suhu baru melewati
  batas.
- **Inisialisasi SQLite** membuat tabel `sensor_history` berisi kolom id, suhu,
  kelembaban, waktu, dan data JSON. Riwayat yang diberikan oleh API dibatasi
  hingga 10 baris terbaru.
- **`GET /api/suhu`** memeriksa API key dan mengembalikan pembacaan terakhir
  (atau nilai null jika belum ada data).
- **`GET /api/history`** memeriksa API key, membaca riwayat dari SQLite, dan
  mengembalikan data dalam format JSON.
- **`POST /api/kontrol`** memeriksa API key dan keberadaan `device` serta
  `action`, lalu menerbitkan payload tersebut ke `iot/kontrol`.
- **`PUT /api/threshold`** memeriksa API key, memvalidasi angka threshold
  positif, dan menyimpannya pada flow context sebagai batas suhu.
- **CORS** menangani preflight `OPTIONS /api/*` dan mengizinkan metode GET,
  POST, PUT, dan OPTIONS.
- **`GET /dashboard`** menyajikan dashboard HTML yang disimpan di node
  template. Dashboard bawaan flow ini terpisah dari `dashboard.html`.
- **WebSocket** menggunakan route `/ws/sensor`; dashboard mandiri di
  `dashboard.html` menggunakan REST polling dan tidak menggunakan WebSocket.

### Endpoint API

Semua endpoint API di bawah memakai header `x-api-key`. API mengembalikan JSON.

| Metode dan path | Kegunaan | Payload / hasil utama |
|---|---|---|
| `GET /api/suhu` | Membaca sensor terakhir | `{"status":"success","data":{"suhu":...,"kelembaban":...}}` |
| `GET /api/history` | Membaca maksimal 10 data terakhir | `{"status":"success","count":...,"data":[...]}` |
| `POST /api/kontrol` | Menerbitkan perintah perangkat | Kirim `{"device":"lamp","action":"on"}` atau `off` |
| `PUT /api/threshold` | Mengatur batas suhu pada flow | Kirim `{"threshold":30}` |

Nilai `device` dan `action` pada contoh kontrol mengikuti tombol pada dashboard.
Node-RED meneruskan nilai tersebut ke MQTT; integrasi dengan perangkat sungguhan
perlu menangani topik `iot/kontrol` di perangkat.

## Konfigurasi dan batasan yang diketahui

- Default `API_BASE` pada dashboard adalah `http://127.0.0.1:1880/api`.
- API key demo saat ini adalah `KULIAH-API-2026`. Untuk mengubahnya, samakan
  nilai `API_KEY` di `dashboard.html` dan pada node validasi API key untuk
  masing-masing endpoint di `flow1.json`. Jangan memakai nilai demo ini untuk
  deployment publik.
- Batas suhu dashboard dimulai dari `30 °C`, sedangkan proses sensor Node-RED
  memakai nilai awal `35 °C` sampai threshold baru disimpan melalui API.
- Batas kelembaban hanya diterapkan oleh dashboard, bukan disimpan atau
  diperiksa oleh flow Node-RED.
- Flow menyediakan WebSocket serta dashboard template tersendiri selain
  dashboard mandiri. Dashboard mandiri memakai REST API secara berkala.
- Notifikasi browser memerlukan izin pengguna dan dukungan browser.
- Grafik hanya menyimpan titik selama halaman terbuka; riwayat permanen disimpan
  melalui SQLite.

## Keamanan

Konfigurasi ini ditujukan untuk demonstrasi lokal, bukan server publik:

- API key ditanam langsung di file proyek dan bukan mekanisme penyimpanan
  rahasia yang aman.
- CORS mengizinkan origin `*`.
- MQTT menggunakan koneksi lokal tanpa TLS maupun autentikasi.
- Jangan mengekspos Node-RED, broker, atau API ke internet tanpa menambahkan
  autentikasi, enkripsi, pembatasan akses, dan pengelolaan rahasia yang layak.

## Lisensi

Belum ada file lisensi pada proyek ini. Tambahkan file `LICENSE` dan pilih
lisensi yang sesuai sebelum mengizinkan penggunaan ulang oleh publik.
