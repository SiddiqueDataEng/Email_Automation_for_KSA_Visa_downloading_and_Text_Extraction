"""
Audio Announcer for Visa Processing
Announces new visa processing using text-to-speech
"""
import threading
import queue
import time

# Try to import TTS libraries
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("WARNING: pyttsx3 not available. Audio announcements disabled.")

class AudioAnnouncer:
    def __init__(self):
        self.enabled = TTS_AVAILABLE
        self.queue = queue.Queue()
        self.engine = None
        self.worker_thread = None
        
        if self.enabled:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 150)  # Speed
                self.engine.setProperty('volume', 0.9)  # Volume
                
                # Start worker thread
                self.worker_thread = threading.Thread(target=self._worker, daemon=True)
                self.worker_thread.start()
                print("SUCCESS: Audio announcer initialized")
            except Exception as e:
                print(f"WARNING: Could not initialize audio: {e}")
                self.enabled = False
    
    def _worker(self):
        """Background worker to process announcements"""
        while True:
            try:
                message = self.queue.get()
                if message is None:
                    break
                
                if self.engine:
                    self.engine.say(message)
                    self.engine.runAndWait()
                
                self.queue.task_done()
                time.sleep(0.5)  # Small delay between announcements
            except Exception as e:
                print(f"Audio error: {e}")
    
    def announce(self, message):
        """Add announcement to queue"""
        if self.enabled:
            self.queue.put(message)
    
    def announce_visa(self, name, visa_no=None):
        """Announce a new visa"""
        if visa_no:
            message = f"Visa of {name}, number {visa_no}, issued"
        else:
            message = f"Visa of {name} issued"
        self.announce(message)
    
    def shutdown(self):
        """Shutdown the announcer"""
        if self.worker_thread:
            self.queue.put(None)
            self.worker_thread.join(timeout=2)

# Global instance
announcer = AudioAnnouncer()
