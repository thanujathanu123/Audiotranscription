"""VoxScribe backend: Flask -> ffmpeg -> whisper.cpp. Runs fully offline."""
import re, shutil, subprocess, tempfile, time
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parent
MODEL = ROOT / "models" / "ggml-base.en.bin"
OUT = ROOT / "output"
BIN = ROOT / "source" / "whisper.cpp-master" / "build" / "bin"
OUT.mkdir(exist_ok=True)

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024


def find_cli():
    for name in ("whisper-cli.exe", "whisper-cli"):
        for p in (ROOT / "source").rglob(name):
            return p
    return None


@app.get("/")
def index():
    return send_from_directory(ROOT / "frontend", "index.html")


@app.post("/api/transcribe")
def transcribe():
    f = request.files.get("file")
    if not f or not f.filename:
        return jsonify(error="No audio file was uploaded."), 400
    cli = find_cli()
    if not cli:
        return jsonify(error="whisper-cli not found. Build whisper.cpp first (see README)."), 500
    if not MODEL.is_file():
        return jsonify(error=f"Model not found at {MODEL}."), 500

    stem = re.sub(r"[^A-Za-z0-9_-]+", "_", Path(f.filename).stem)[:60] or "audio"
    stem = f"{time.strftime('%Y%m%d_%H%M%S')}_{stem}"
    lang = (request.form.get("language") or "auto").strip()

    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / ("input" + Path(f.filename).suffix.lower())
        f.save(src)
        wav = Path(tmp) / "audio.wav"
        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg:
            r = subprocess.run([ffmpeg, "-y", "-i", str(src), "-ar", "16000", "-ac", "1",
                                "-c:a", "pcm_s16le", str(wav)], capture_output=True, text=True)
            if r.returncode != 0:
                return jsonify(error="ffmpeg could not read this audio file."), 400
        elif src.suffix == ".wav":
            wav = src
        else:
            return jsonify(error="ffmpeg is not installed, so only WAV files work."), 400

        cmd = [str(cli), "-m", str(MODEL), "-f", str(wav), "-l", lang, "-nt",
               "-otxt", "-of", str(OUT / stem)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        txt = OUT / f"{stem}.txt"
        if r.returncode != 0 or not txt.is_file():
            return jsonify(error="whisper.cpp failed: " + (r.stderr or "")[-300:]), 500

    return jsonify(text=txt.read_text(encoding="utf-8", errors="replace").strip(), saved=txt.name)


if __name__ == "__main__":
    print("VoxScribe running at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
