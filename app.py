from flask import Flask, render_template, redirect, url_for, request
from queue import Queue
from threading import Thread
import subprocess
import os
import time
import vlc

app = Flask(__name__)

#Structure for holding data in the queue
class qobj():
    def __init__(self, status, url, title):
        self.status = status
        self.url = url
        self.title = title

# Main page.  Does most of the work
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

# Two routes I used for testing
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

# Flask function to pass to thread
def RunFlask():
    app.run(debug=False, host='0.0.0.0')

# Worker role for the thread.
# For now, opens a new instance of VLC
# media player with the given URL
# ToDo: Figure out VLC Python API
# on RBP
def RunWorker():
    vlc = 0
    while True:
        if not len(q) == 0:
            #EnqueueVLC(q[0].url)
            #q.pop(0)
            if vlc == 0:
                vlc = StartVLC(str(q[0].url))
                # Set status so the site can show it's playing
                q[0].status = "playing"
                # Wait for it to close, then remove from queue
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

# Playing with trying to not open a new VLC every tmie
# Big bottleneck 
def EnqueueVLC(url):
    vlc = os.system("vlc --vout=none --one-instance --playlist-enqueue \"" + url + "\"")
    return vlc

# Playing with the VLC bindings.
# Library problem with RBP, or using bindings wrong?
# Video starts playing but stops immediately
def TestVLC():
    media = "https://www.youtube.com/watch?v=wgxzQVGkTHk"
    media2 = "https://www.youtube.com/watch?v=2igVmtKtaWk"
    
    instance = vlc.Instance()
    player = instance.media_player_new()
    print(vlc.libvlc_media_player_get_state(player))
    player.set_mrl(media2)
    print(player.get_title())
    player.play()

    

    c = 0
    while c < 40:
        print(str(c),)
        print(vlc.libvlc_media_player_get_state(player))
        time.sleep(1)
        c += 1


# Main; start threads
if __name__ == '__main__':
    q = []
    #TestVLC()
    #app.run(debug=True, host='0.0.0.0')
    
    #commands = Queue()
    
    server = Thread(target=RunFlask, args=())
    worker = Thread(target=RunWorker, args=())
    
    print("Starting server thread")
    server.start()
    print("Starting worker thread")
    worker.start()
