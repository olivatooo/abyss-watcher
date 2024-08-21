import threading
import os

tick = os.environ.get("TICKRATE") or 0.1

def Watcher():
    log("starting event loop")
    while True:



def Lit():
    threading.Thread(target=Watcher, name="Watcher").start()
