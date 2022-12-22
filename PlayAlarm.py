import pyaudio
import wave


class Sound:
    def __init__(self, file):
        self.wf = wave.open(file, 'rb')
        # instantiate PyAudio
        self.p = pyaudio.PyAudio()
        # define callback
        self.stream = None

    def play_sound(self):
        self.stream = self.p.open(format=self.p.get_format_from_width(self.wf.getsampwidth()),
                                  channels=self.wf.getnchannels(), rate=self.wf.getframerate(),
                                  output=True, stream_callback=self.callback)

    def callback(self, in_data, frame_count, time_info, status):
        data = self.wf.readframes(frame_count)
        return data, pyaudio.paContinue

    def stop_sound(self):
        # stop stream
        self.stream.stop_stream()
        self.stream.close()
        self.wf.close()
        # close PyAudio
        self.p.terminate()

