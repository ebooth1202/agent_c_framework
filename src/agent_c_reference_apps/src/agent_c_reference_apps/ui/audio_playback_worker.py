import base64
import time
import queue
import pyaudio
import threading

from agent_c.models.events.chat import AudioDeltaEvent




class AudioPlaybackWorker:
    def __init__(self, sample_rate=16000, channels=1):
        """
        Initializes the audio playback worker.

        Args:
            sample_rate (int): The sample rate of the PCM16 audio.
            channels (int): Number of audio channels.
            frames_per_buffer (int): Number of frames per audio buffer.
        """
        self.sample_rate = sample_rate
        self.channels = channels
        #self.frames_per_buffer = frames_per_buffer

        # Create a thread-safe queue for incoming PCM16 audio chunks.
        self.audio_queue = queue.Queue()
        self.running = True

        # Initialize PyAudio.
        self.pyaudio_instance = pyaudio.PyAudio()
        self.stream = self.pyaudio_instance.open(
            format=pyaudio.paInt16,  # PCM16
            channels=self.channels,
            rate=self.sample_rate,
            output=True
        )

        # Start the worker thread.
        self.audio_thread = threading.Thread(target=self._process_audio)
        self.audio_thread.daemon = True
        self.audio_thread.start()

    def push_chunk(self, audio_chunk: bytes):
        """
        Push a PCM16 audio chunk to be played.

        Args:
            audio_chunk (bytes): A chunk of PCM16 audio data.
        """
        self.audio_queue.put(audio_chunk)

    def push_delta(self, delta: AudioDeltaEvent):
        """
        Push a PCM16 audio chunk to be played.

        Args:
            delta (AudioDeltaEvent): A chunk of PCM16 audio data in delta fromat.
        """
        self.audio_queue.put(base64.b64decode(delta.content))


    def _process_audio(self):
        """
        The worker thread method that continuously polls the queue for audio chunks and plays them.
        """
        while self.running:
            try:
                # Wait up to 0.1 seconds for an audio chunk.
                chunk = self.audio_queue.get(timeout=0.1)
                if chunk is None:
                    break

                # Write the audio data to the output stream.
                self.stream.write(chunk)
                self.audio_queue.task_done()
            except queue.Empty:
                # No audio data received in the timeout period; loop again.
                continue

    def stop(self):
        """
        Stops the audio playback worker gracefully.
        """
        self.running = False
        # Put a sentinel value in the queue to ensure the thread unblocks.
        self.audio_queue.put(None)
        self.audio_thread.join()
        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio_instance.terminate()


# Example usage:
if __name__ == "__main__":
    # Create an instance of the audio playback worker.
    audio_worker = AudioPlaybackWorker(sample_rate=16000, channels=1, frames_per_buffer=1024)

    try:
        # Simulate pushing audio chunks.
        # In a real application, these chunks would come from your audio modality pipeline.
        # For demonstration, we'll simulate with silence (zeroed PCM16 data).
        for _ in range(100):
            # Create a buffer of silence (PCM16: 2 bytes per sample).
            silence_chunk = (b'\x00\x00' * 512)  # Adjust size as needed.
            audio_worker.push_chunk(silence_chunk)
            time.sleep(0.01)  # Simulate a short delay between audio chunks.
    finally:
        # Ensure we clean up the audio resources.
        audio_worker.stop()
