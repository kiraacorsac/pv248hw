import sys
import wave

freq = sys.argv[1]
file = sys.argv[2]

music = wave.open(file, 'rb')

fi