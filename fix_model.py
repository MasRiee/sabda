import json
import os
import shutil
import zipfile

input_path = "model/word_classifier.keras"
fixed_path = "model/word_classifier_fixed.keras"


def clean_dict(d):
    if isinstance(d, dict):
        d.pop("quantization_config", None)
        for val in d.values():
            clean_dict(val)
    elif isinstance(d, list):
        for item in d:
            clean_dict(item)


if not os.path.exists(input_path):
    print(f"[ERROR] File '{input_path}' tidak ditemukan. Pastikan path file benar.")
else:
    with (
        zipfile.ZipFile(input_path, "r") as zin,
        zipfile.ZipFile(fixed_path, "w") as zout,
    ):
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "config.json":
                config = json.loads(data.decode("utf-8"))
                clean_dict(config)
                data = json.dumps(config).encode("utf-8")
            zout.writestr(item, data)

    # Ganti file model lama dengan file yang sudah diperbaiki
    shutil.move(fixed_path, input_path)
    print(
        "✅ BERHASIL! Model 'word_classifier.keras' telah diperbaiki dan siap digunakan."
    )