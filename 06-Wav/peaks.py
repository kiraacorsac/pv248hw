import wave
import sys
import numpy


def isPeak(sample, average):
    return sample >= average * 20



wavefile = wave.open(sys.argv[1], 'r')

channel_n = wavefile.getnchannels()
samples_n = wavefile.getnframes() * channel_n
integer_data = wave.struct.unpack("%ih" % samples_n, wavefile.readframes(wavefile.getnframes()))
sample_w = wavefile.getsampwidth()
framerate = wavefile.getframerate()

channels = [[] for time in range(channel_n)]

for index, data in enumerate(integer_data):
    channel = index % channel_n
    channels[channel].append(data)

audio = []
if channel_n == 2:
    audio = [(l // 2) + (r // 2) for (l, r) in zip(channels[0], channels[1])]
else:
    audio = channels[0]

min = None
max = None
for sample_i in range(len(audio) // framerate):
    rfft = numpy.fft.rfft(audio[sample_i * framerate:(sample_i + 1) * framerate])
    amplitudes = numpy.abs(rfft)
    average = numpy.mean(amplitudes)

    for amp, freq in zip(amplitudes, numpy.fft.rfftfreq(framerate)):
        r_freq = int(round(freq * framerate))
        if isPeak(amp, average):
            if min is None or r_freq < min:
                min = r_freq
            if max is None or r_freq > max:
                max = r_freq

if min is None or max is None:
    print("no peaks")
else:
    print("low =", int(min), "high =", int(max))



    


        