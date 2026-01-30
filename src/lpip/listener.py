"""
Push-to-Talk Audio Listener with Whisper Transcription
Captura de audio mediante PTT y transcripción usando Whisper via HuggingFace API
"""

import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import keyboard
import requests
import tempfile
import os
from typing import Optional, Callable
from src.common.logger import get_logger

logger = get_logger(__name__)


class PushToTalkListener:
    """
    Push-to-Talk audio listener with Whisper transcription via HuggingFace API
    """
    
    def __init__(
        self, 
        ptt_key: str = "space",
        sample_rate: int = 16000,
        channels: int = 1,
        hf_token: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Inicializa el listener de audio con push-to-talk
        
        Args:
            ptt_key: Tecla para activar grabación (por defecto: "space")
            sample_rate: Frecuencia de muestreo en Hz
            channels: Número de canales de audio
            hf_token: Token de HuggingFace (se lee de .env si no se proporciona)
            model: Modelo de Whisper (se lee de .env si no se proporciona)
        """
        self.ptt_key = ptt_key
        self.sample_rate = sample_rate
        self.channels = channels
        
        # Read from environment variables if not provided
        self.hf_token = hf_token or os.getenv("WHISPER_API_KEY", "")
        self.model = model or os.getenv("WHISPER_MODEL", "openai/whisper-large-v3-turbo")
        
        if not self.hf_token:
            logger.warning("No WHISPER_API_KEY found in environment or parameters")
        
        self.recording = False
        self.frames = []
        self.stream = None
        self.transcription_callback: Optional[Callable[[str], None]] = None
        
        self.headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "audio/wav"
        }
        
        logger.info(f"PushToTalkListener initialized (key: {ptt_key}, model: {model})")
    
    def _audio_callback(self, indata, frames_count, time_info, status):
        """Callback para el stream de audio"""
        if self.recording:
            self.frames.append(indata.copy())
    
    def _start_recording(self):
        """Inicia la grabación de audio"""
        if self.recording:
            return  # Already recording, ignore key repeat
        
        self.frames = []
        self.recording = True
        logger.info("[REC] Recording...")
        print("[REC] Grabando...")
    
    def _stop_recording(self):
        """Detiene la grabación y procesa el audio"""
        self.recording = False
        logger.info("[...] Processing...")
        print("[...] Procesando...")
        
        if not self.frames:
            logger.warning("[WARN] Empty audio")
            print("[WARN] Audio vacío")
            return
        
        # Concatenate all audio frames
        audio = np.concatenate(self.frames, axis=0)
        
        # Save to temporary WAV file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            wav.write(f.name, self.sample_rate, audio)
            audio_path = f.name
        
        try:
            # Send to HuggingFace API for transcription
            with open(audio_path, "rb") as f:
                response = requests.post(
                    f"https://router.huggingface.co/hf-inference/models/{self.model}",
                    headers=self.headers,
                    data=f.read(),
                    timeout=60
                )
            
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"[ERROR] {error_msg}")
                return
            
            if not response.text.strip():
                logger.error("[ERROR] Empty response from server")
                return
            
            result = response.json()
            
            if isinstance(result, dict) and "text" in result:
                transcription = result["text"]
                logger.info(f"Transcription: {transcription}")
                
                # Call callback if registered
                if self.transcription_callback:
                    self.transcription_callback(transcription)
                    
            elif isinstance(result, dict) and "error" in result:
                logger.error(f"[ERROR] API: {result['error']}")
            else:
                logger.warning(f"[WARN] Unexpected response: {result}")
        
        except Exception as e:
            logger.error(f"[ERROR] {e}")
        
        finally:
            # Clean up temporary file
            os.remove(audio_path)
    
    def set_transcription_callback(self, callback: Callable[[str], None]):
        """
        Registra un callback para recibir transcripciones
        
        Args:
            callback: Función que recibe el texto transcrito
        """
        self.transcription_callback = callback
        logger.info("Transcription callback registered")
    
    def start(self):
        """Inicia el sistema de push-to-talk"""
        # Create and start audio stream
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=self._audio_callback
        )
        
        self.stream.start()
        
        # Register keyboard handlers
        keyboard.on_press_key(self.ptt_key, lambda e: self._start_recording())
        keyboard.on_release_key(self.ptt_key, lambda e: self._stop_recording())
        
        logger.info(f"[OK] Push-to-talk system armed. Press {self.ptt_key.upper()} to speak")
    
    def stop(self):
        """Detiene el sistema de push-to-talk"""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        # Unhook keyboard handlers
        keyboard.unhook_all()
        
        logger.info("Push-to-talk system stopped")
    
    def is_running(self):
        """Verifica si el sistema está activo"""
        return self.stream is not None and self.stream.active
