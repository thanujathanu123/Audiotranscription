# VoxScribe: offline audio transcription

Browser page -> Flask (app.py) -> ffmpeg -> whisper.cpp. Runs fully offline after setup.

## Setup on a new computer (needs internet once)
1. Install Python 3.9+ from python.org (tick "Add python.exe to PATH").
2. In this folder: `python -m pip install -r requirements.txt`
3. Install ffmpeg: `winget install ffmpeg` (then reopen the terminal).
4. Create folders `models` and `source\whisper.cpp-master\build\bin`.
5. Download `whisper-bin-x64.zip` from the whisper.cpp GitHub releases (an older release such as v1.9.2 has it).
   Extract it and copy `whisper-cli.exe` plus all `.dll` files into `source\whisper.cpp-master\build\bin`.
6. Download the model into `models`:
   https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin

## Run
Double-click `start.bat`, or run `python app.py` and open http://127.0.0.1:5000
