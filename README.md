# SABDA — Aplikasi Desktop (PyQt6)

Skeleton aplikasi untuk alat bantu belajar bicara SABDA, disesuaikan dengan
model lip reading yang sudah fix dipakai tim (notebook *Vowel Lip-Shape
Detection Using MediaPipe — Updated to Tasks API*, Bagian 2: klasifikasi kata
dari sequence landmark bibir via GRU).

## Struktur

```
sabda/
├── backend/
│   ├── app_controller.py      # state machine utama (IDLE -> SHOW_WORD -> LISTENING -> SHOW_RESULT)
│   ├── model_manager/
│   │   ├── lip_reading.py     # FaceLandmarker (Tasks API) + model GRU — porting dari notebook
│   │   └── word_validator.py  # cocokkan prediksi vs kata target
│   ├── sensor_manager/
│   │   ├── camera.py          # QThread capture kamera + ekstraksi fitur + trigger prediksi
│   │   ├── frame_buffer.py    # sliding window 24 frame + resample interpolasi (persis Step 12 notebook)
│   │   └── microphone.py      # skeleton untuk modul pitch, belum diisi
│   └── hardware_manager/
│       ├── haptic.py          # kirim sinyal motor getar via serial
│       └── joystick.py        # baca input navigasi via serial (mock: pakai keyboard)
├── ui/
│   ├── main_window.py         # QStackedWidget, switch layar sesuai state
│   ├── screens/                # menu, word, listening, result
│   └── components/
│       └── camera_feed.py     # live preview kamera
├── model/                      # taruh file model di sini (lihat "Setup Model" di bawah)
├── assets/words/word_list.json
├── scripts/download_face_landmarker.py
├── config.py                   # SEMUA nilai environment-spesifik ada di sini
├── main.py
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt --break-system-packages   # kalau di lingkungan Linux terbatas
```

## Setup Model (sebelum matikan MOCK MODE)

1. **FaceLandmarker**:
   ```bash
   python scripts/download_face_landmarker.py
   ```
   Hasil: `model/face_landmarker.task`

2. **Model kata (GRU)** — dari notebook, setelah Step 15 selesai jalan,
   download 2 file berikut dari Colab lalu taruh di `model/`:
   - `word_classifier.keras`
   - `word_labels.json`

3. **Selaraskan kosakata**: `assets/words/word_list.json` (kata yang
   ditampilkan ke user secara berurutan) idealnya SAMA ISINYA dengan
   `TARGET_WORDS` yang dipakai saat training (`word_labels.json`) — kalau
   beda, aplikasi bisa menampilkan instruksi kata yang modelnya belum pernah
   dilatih untuk mengenalinya.

4. Di `config.py`, ubah:
   ```python
   MODEL_MOCK_MODE = False
   HARDWARE_MOCK_MODE = False   # kalau mikrokontroler & motor sudah tersambung
   ```

## Menjalankan

```bash
python main.py
```

Mode default (`MODEL_MOCK_MODE=True`, `HARDWARE_MOCK_MODE=True`) bisa
langsung dijalankan tanpa kamera/model/mikrokontroler asli — berguna untuk
tes alur UI & state machine dari hari pertama, sebelum semua komponen siap.

Navigasi tanpa joystick fisik (mode mock): **Enter/Space** = tombol SELECT,
**Esc** = kembali ke menu.

## Catatan penting soal MediaPipe

Kode ini pakai **MediaPipe Tasks API** (`mediapipe.tasks.python.vision.FaceLandmarker`),
BUKAN `mp.solutions.face_mesh` yang sudah deprecated. Titik landmark
(`LIP_CONTOUR_POINTS`, `LIP_POINTS`, `REF_POINTS` di `config.py`) dan urutan
perhitungan fitur di `lip_reading.py` HARUS PERSIS SAMA dengan yang dipakai
saat training di notebook — kalau ada yang diubah di salah satu sisi
(notebook atau `config.py`), model akan menerima fitur yang berbeda dari
yang dipelajarinya saat training dan prediksinya akan salah/acak.

## Titik yang masih perlu dikerjakan tim

- [ ] `backend/model_manager/pitch_extractor.py` — FFT+cepstrum, Transformasi
      Radon, Viterbi (bagian ERIC, belum ada file-nya, tinggal dibuat mengikuti
      pola `lip_reading.py`)
- [ ] Uji `HARDWARE_MOCK_MODE=False` dengan mikrokontroler asli — sesuaikan
      protokol serial di `haptic.py`/`joystick.py` dengan firmware yang dipakai
      tim elektronik
- [ ] Rekam data & training ulang notebook untuk kosakata final (bukan cuma
      3 kata contoh: kucing/babi/daun)
- [ ] Test end-to-end di MiniPC Linux (device index kamera, port serial,
      instalasi `portaudio19-dev` untuk PyAudio — semua sudah dipisah di
      `config.py`, tinggal disesuaikan nilainya)
