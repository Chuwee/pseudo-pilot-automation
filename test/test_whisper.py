import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import keyboard
import requests
import tempfile
import time
import os

# =========================
# CONFIG
# =========================

HF_TOKEN = "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"
MODEL = "openai/whisper-large-v3-turbo"

SAMPLE_RATE = 16000
CHANNELS = 1
PTT_KEY = "space"     # tecla para hablar

# =========================

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "audio/wav"
}

recording = False
frames = []

print("PTT listo.")
print(f"Manten pulsada '{PTT_KEY}' para hablar.")
print("Suelta para transcribir.\n")


def callback(indata, frames_count, time_info, status):
    global frames
    if recording:
        frames.append(indata.copy())


def start_recording():
    global recording, frames
    if recording:
        return  # Already recording, ignore key repeat
    frames = []
    recording = True
    print("[REC] Grabando...")


def stop_recording():
    global recording, frames
    recording = False
    print("[...] Procesando...")

    if not frames:
        print("[WARN] Audio vacio")
        return

    audio = np.concatenate(frames, axis=0)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        wav.write(f.name, SAMPLE_RATE, audio)
        audio_path = f.name

    try:
        with open(audio_path, "rb") as f:
            response = requests.post(
                f"https://router.huggingface.co/hf-inference/models/{MODEL}",
                headers=headers,
                data=f.read(),
                timeout=60
            )

        if response.status_code != 200:
            print(f"\n[ERROR] HTTP {response.status_code}: {response.text}")
            return

        if not response.text.strip():
            print("\n[ERROR] Respuesta vacia del servidor")
            return

        result = response.json()

        if isinstance(result, dict) and "text" in result:
            print("\nTranscripcion:")
            print(result["text"])
        elif isinstance(result, dict) and "error" in result:
            print(f"\n[ERROR] API: {result['error']}")
        else:
            print("\n[WARN] Respuesta inesperada:")
            print(result)

    except Exception as e:
        print("[ERROR]", e)

    finally:
        os.remove(audio_path)


# =========================
# Audio stream
# =========================

stream = sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    callback=callback
)

stream.start()

keyboard.on_press_key(PTT_KEY, lambda e: start_recording())
keyboard.on_release_key(PTT_KEY, lambda e: stop_recording())

print("[OK] Sistema armado. Pulsa SPACE para hablar.\n")

try:
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nCerrando...")
    stream.stop()
    stream.close()

