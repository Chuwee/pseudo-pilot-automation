import sounddevice as sd
import numpy as np
from piper import PiperVoice
from scipy import signal
from piper import SynthesisConfig


class VoicePlayback:
    def __init__(self, voice_model_path: str = "/Users/ignacio.demiguel@feverup.com/Desktop/pseudo-pilot-automation/voices/en_US-norman-medium.onnx"):
        """
        Initialize the voice playback system with Piper TTS.
        
        Args:
            voice_model_path: Path to the Piper voice model (.onnx file)
        """
        self.voice = PiperVoice.load(voice_model_path)
    
    def _apply_radio_effects(self, audio_array: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Apply radio distortion effects to make audio sound like aircraft radio transmission.
        
        Effects applied:
        - Bandpass filter (300-3400 Hz, typical radio bandwidth)
        - Background static noise
        - Light compression
        
        Args:
            audio_array: Input audio as numpy array
            sample_rate: Sample rate of the audio
            
        Returns:
            Processed audio array with radio effects
        """
        # Convert to float for processing
        audio_float = audio_array.astype(np.float32) / 32768.0
        
        # 1. Bandpass filter (300-3400 Hz - typical radio bandwidth)
        nyquist = sample_rate / 2
        low_cutoff = 300 / nyquist
        high_cutoff = 3400 / nyquist
        
        # Design butterworth bandpass filter
        sos = signal.butter(4, [low_cutoff, high_cutoff], btype='band', output='sos')
        audio_filtered = signal.sosfilt(sos, audio_float)
        
        # 2. Add radio static/noise (very subtle)
        noise_level = 0.003
        static_noise = np.random.normal(0, noise_level, len(audio_filtered))
        audio_with_static = audio_filtered + static_noise
        
        # 3. Light compression (reduce dynamic range)
        threshold = 0.3
        ratio = 3.0
        audio_compressed = np.where(
            np.abs(audio_with_static) > threshold,
            np.sign(audio_with_static) * (threshold + (np.abs(audio_with_static) - threshold) / ratio),
            audio_with_static
        )
        
        # 4. Normalize to prevent clipping
        max_val = np.abs(audio_compressed).max()
        if max_val > 0:
            audio_compressed = audio_compressed * 0.95 / max_val
        
        # Convert back to int16
        audio_processed = (audio_compressed * 32768.0).astype(np.int16)
        
        return audio_processed
    
    def play(self, text: str, speed: float = 0.675) -> None:
        """
        Synthesize text to speech and play it immediately with radio effects.
        
        Args:
            text: The text to speak
            speed: Playback speed multiplier (default 1.5 for faster ATC speech)
        """
        # Collect audio chunks from the generator
        audio_chunks = []
        syn_config = SynthesisConfig(
            length_scale=speed,
            noise_scale=1.0,
            noise_w_scale=1.0,
            normalize_audio=True
        )
        for audio_chunk in self.voice.synthesize(text, syn_config=syn_config):
            # AudioChunk has audio_int16_bytes with raw PCM bytes
            audio_chunks.append(audio_chunk.audio_int16_bytes)
        
        # Combine all chunks
        audio_bytes = b''.join(audio_chunks)
        
        # Convert bytes to numpy array (int16 PCM format)
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
        
        # Get sample rate from voice config
        base_sample_rate = self.voice.config.sample_rate
        
        # Apply radio effects
        audio_processed = self._apply_radio_effects(audio_array, base_sample_rate)
        
        # Adjust playback speed by modifying sample rate
        # Playing at higher sample rate = faster speech
        playback_sample_rate = int(base_sample_rate * 1)
        
        # Play audio with radio effects and speed adjustment
        sd.play(audio_processed, playback_sample_rate)
        sd.wait()  # Wait until audio finishes playing


if __name__ == "__main__":
    # Test the voice playback with radio effects
    print("Initializing voice...")
    voice_playback = VoicePlayback()
    print("Playing message with radio effects...")
    voice_playback.play("Roger that, Iberia fivefivenine maintain flight level two five zero.")
    print("Done!")
