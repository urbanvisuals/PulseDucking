#!/usr/bin/python3

import json
import threading
import time

import inputs
import react
import reader

with open('config.json', 'r') as f:
    config = json.load(f)

watchingIndices = []

class Supervisor:
    def onPlayStateChange(self, playing, master_index):
        react.onPlayStateChange(playing, master_index)
    def onClose(self, input):
        watchingIndices.remove(input.index)
        react.onPlayStateChange(False, input.index, master_index)
        print(f"Stopped watching {input}")

supervisorInstance = Supervisor()

def updateWatches():
    inputsList = inputs.get()

    namesToWatch = [a['name'] for a in config['applications'] if a['role'] == 'master']
    namesToDuck = [a['name'] for a in config['applications'] if a['role'] == 'slave']

    inputsToWatch = [i for i in inputsList if i.name in namesToWatch]
    inputsToDuck = [i for i in inputsList if i.name in namesToDuck]
    inputToDuck = inputsToDuck[0]
    inputsToWatchNew = [i for i in inputsToWatch if i.index not in watchingIndices]


    for inputToWatch in inputsToWatchNew:
        print(f"Started watching {inputToWatch}")    
        t = threading.Thread(target=reader.monitor, args=[inputToWatch, inputToDuck.index, supervisorInstance])    # added inputToDuck to duck first and only slave. 
        t.start()
        watchingIndices.append(inputToWatch.index)

while True:
    updateWatches()
    time.sleep(config['preferences']['sourcesUpdateInterval'])
