import threading
import cv2
import subprocess
import os

class VideoInput(threading.Thread):
    def __init__(self, device, subject_id, trial_name):
        threading.Thread.__init__(self)

        self.stop = threading.Event()
        self.recording = threading.Event()
        self.stopped = threading.Event()

        self.device = device
        self.filename = 'output-' + str(subject_id) + '-' + trial_name + '.avi'
        self.mirror = False

    def run(self):
        self.open()

        while not self.stop.is_set():
            ret, frame = self.device.read()
            if ret == True:
                if self.mirror:
                    frame = cv2.flip(frame, 1)
                self.out.write(frame)

        self.close()

    def open(self):
        if not self.device.isOpened():
            self.device.open(0)

        while not self.device.isOpened():
            pass

        self.out = cv2.VideoWriter(self.filename, cv2.cv.CV_FOURCC(*'XVID'), 20.0, (640, 480))

        self.recording.set()

    def close(self):
        self.out.release()
        self.device.release()

        while self.device.isOpened():
            pass

        self.stopped.set()

    def convert(self, ffmpeg, delete=True):
        self.stopped.wait()

        filename = self.filename + '.mpeg'
        subprocess.call([ffmpeg, '-i', self.filename, '-f', 'mpeg1video', '-c:v', 'mpeg1video', filename])

        if delete:
            os.remove(self.filename)

        return filename
