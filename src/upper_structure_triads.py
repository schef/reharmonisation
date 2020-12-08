#!/usr/bin/env python

import subprocess
from time import sleep
import os
import random
import sys

chordLists = {
    ##### dominant chords #####
    "13b9": ["c3", "g3", "b-3", "e4", "a4", "c#5"],
    "7#9": ["c3", "g3", "b-3", "e4", "g4", "b-4", "e-5"],
    "13#11": ["c3", "g3", "b-3", "e4", "fis4", "a4", "d5"],
    "7#9#5": ["c3", "b-3", "e4", "a-4", "c5", "e-5"],
    "7#11b9": ["c3", "g3", "b-3", "e4", "g-4", "b-4", "d-5"],
    ##### major chords #####
    #"M13#11" : ["c3", "g3", "b3", "e4", "f#4", "a4", "d5"],
    #"M9" : ["c3", "g3", "b3", "e4", "a4", "d5"],
    ##### minor chords #####
    #"m11" : ["c3", "e-3", "g3", "f4", "b-4", "d5"],
    #"mM9" : ["c3", "e-3", "g3", "b3", "d4", "g4"],
    ##### weird ones #####
    #"" : ["", "", "", "", "", "", ""],
    #"" : ["", "", "", "", "", "", ""],
    #"" : ["", "", "", "", "", "", ""]
}


def runBashCmd(cmd, showOutput=True):
    process = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lines = []
    while process.poll() is None:
        for line in process.stdout:
            decodedLine = line.decode('UTF-8').strip()
            if showOutput:
                print("STDIN:", decodedLine)
            lines.append(decodedLine)
        sleep(0.1)
    return lines


def writeLinesToFile(lines, filename):
    print("writeLinesToFile " + filename)
    with open(filename, 'w') as f:
        f.write("\n".join(lines))


def readLinesFromFile(filename):
    lines = []
    with open('./' + filename, 'r') as f:
        lines = f.readlines()
    return lines


##### check for music21 start #####
try:
    from music21 import *
except ModuleNotFoundError:
    print("Module not found. Please install using next command:")
    print("    pip install --user music21")
    sys.exit(1)

##### check for music21 end #####
##### check for pmidi and set virmidi start #####
def startSndVirMidi():
    if ("snd_virmidi" not in "\n".join(runBashCmd("lsmod", False))):
        print("starting snd_virmidi")
        runBashCmd("sudo modprobe snd_virmidi")


def getVirmidiPort():
    port = "0:0"
    try:
        output = runBashCmd("aconnect -il", False)
        lineMatch = 0
        for e,line in enumerate(output):
            if "virtual raw midi" in line.lower():
                lineMatch = e
                break
        portPre = output[lineMatch].split(" ")[1]
        portPost = output[lineMatch + 1].split(" ")[0]
        port = portPre + portPost
    except:
        print("Can't parse port, try to enter in manualy.")
        pass
    return port

try:
    subprocess.call(["pmidi"], stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL)
    environment.set('midiPath', '/usr/bin/pmidi')
    startSndVirMidi()
    os.environ['ALSA_OUTPUT_PORTS'] = getVirmidiPort()
except OSError as e:
    print("Missing midi player. Install next app using your package manager:")
    print("    pmidi")
    sys.exit(1)

try:
    subprocess.call(["musescore", "-v"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    environment.set('musicxmlPath', '/usr/bin/musescore')
except:
    pass
##### check for pmidi and set virmidi end #####


def sendStreamToMusescore(stream):
    stream.show()


def playStreamAsMidi(stream):
    stream.show('midi')


def playChordName(chordName, changeOctave=1):
    streamPlay = stream.Stream()
    pitchList = [pitch.Pitch(p) for p in chordLists[chordName]]
    for p in pitchList:
        p.octave = p.octave + changeOctave
    chordPlay = chord.Chord(pitchList, duration=duration.Duration("whole"))
    streamPlay.append(chordPlay)
    playStreamAsMidi(streamPlay)


def startPractice():
    print("Listen and name the chord, practice based on 8bit music theory")
    print("Listen to port 20:0 or Virtual RAW MIDI 0 on your midi sequencer")
    try:
        chordName = random.choice(list(chordLists))
        playChordName(chordName)
        while True:
            c = input("enter chord name or [?nrhq]: ")
            if c == "?":
                print("possible chord names", list(chordLists))
            elif c == "n":
                print("next")
                chordName = random.choice(list(chordLists))
                playChordName(chordName)
            elif c == "r":
                print("repeat")
                playChordName(chordName)
            elif c == "h":
                print("help, chord name is", chordName)
            elif c == "q":
                print("quit")
                sys.exit(0)
            else:
                if c == chordName:
                    print("good, next")
                    chordName = random.choice(list(chordLists))
                    playChordName(chordName)
                else:
                    print("wrong, try again")
                    playChordName(chordName)

    except KeyboardInterrupt:
        print("keyboard interupt")


if __name__ == "__main__":
    startPractice()
