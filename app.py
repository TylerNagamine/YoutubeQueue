from flask import Flask, render_template, redirect, url_for, request
from queue import Queue
from threading import Thread
import subprocess
import os
import time
#import lxml

app = Flask(__name__)

class qobj():
    def __init__(self, status, url, title):
        self.status = status
        self.url = url
        self.title = title

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'submit' in request.form:
            yt = qobj("new", request.form['yourl'], "")
            q.append(yt)
        elif 'remove' in request.form:
            req = request.form['queue']
            for cur in q:
                if cur.url == req:
                    q.remove(cur)
    return render_template('index.html', q=q)

@app.route('/add/<address>')
def embed(address):
    address = "http://www.youtube.com/embed/" + address
    return render_template('page.html', address=address)

@app.route('/test')
def tester():
    url = "https://www.youtube.com/watch?v=zasf5D0SlLI"
    for c in q:
        print(str(c))
    return redirect(url_for('index'))


def RunFlask():
    app.run(debug=False, host='0.0.0.0')

def RunWorker():
    vlc = 0
    while True:
        if not len(q) == 0:
            #EnqueueVLC(q[0].url)
            #q.pop(0)
            if vlc == 0:
                vlc = StartVLC(str(q[0].url))
                q[0].status = "playing"
                vlc.wait()
                q.pop(0)
            elif vlc.poll != None:
                vlc = StartVLC(str(q[0].url))
                q[0].status = "playing"
                vlc.wait()
                q.pop(0)                
        time.sleep(1)

def StartVLC(url):
    vlc = subprocess.Popen(["cvlc", "--vout=none", "--play-and-exit", url])
    return vlc
def EnqueueVLC(url):
    vlc = os.system("vlc --vout=none --one-instance --playlist-enqueue \"" + url + "\"")
    return vlc

if __name__ == '__main__':
    q = [] 
    #app.run(debug=True, host='0.0.0.0')
    
    #commands = Queue()
    
    server = Thread(target=RunFlask, args=())
    worker = Thread(target=RunWorker, args=())
    
    print("Starting server thread")
    server.start()
    print("Starting worker thread")
    worker.start()
