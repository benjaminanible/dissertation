import threading, subprocess, time, os
import pymedia.audio.sound as sound
import pymedia.audio.acodec as acodec

class DelayedAudioOutput(threading.Thread):
    def __init__(self, audio_stimuli, delay):
        threading.Thread.__init__(self)

        self.audio = audio_stimuli
        self.delay = delay / 1000.0

    def run(self):
        time.sleep(self.delay)

        self.audio.present()

class AudioInput(threading.Thread):
    def __init__(self, audio_id, out_dir='.'):
        threading.Thread.__init__(self)

        self.stop = threading.Event()
        self.recording = threading.Event()
        self.stopped = threading.Event()

        self.filename = out_dir+'/'+audio_id+'.mp3'
        self.encoder = acodec.Encoder({
            'id': acodec.getCodecID('mp3'),
            'bitrate': 96000,
            'sample_rate': 44100,
            'channels': 2
        })
        self.recorder = sound.Input(44100, 2, sound.AFMT_S16_LE)

    def run(self):
        self.open()

        while not self.stop.is_set():
            audio = self.recorder.getData()
            if audio and len(audio):
                for frame in self.encoder.encode(audio):
                    self.out.write(frame)
            else:
                time.sleep(0.003)

        self.close()

    def open(self):
        self.recorder.start()
        self.out = open(self.filename, "wb")

        self.recording.set()

    def close(self):
        self.recorder.stop()
        self.out.close()

        self.stopped.set()

    def convert(self, ffmpeg):
        self.stopped.wait()

        filename = self.filename + '.ogg'
        subprocess.call([ffmpeg, '-i', self.filename, '-y', '-c:a', 'libvorbis', filename])

        os.remove(self.filename)

        return filename
