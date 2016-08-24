import sys
import time
import json

import websocket


def long_task(url):
    ws = websocket.WebSocket()
    ws.connect(url)

    total = 150
    for i in range(1, total+1):
        print(i)
        data = dict(type='progress', value=i, total=total)
        ws.send(json.dumps(data))
        time.sleep(0.05)

    ws.close()


if __name__ == '__main__':
    # url = sys.argv[1]
    long_task('ws://localhost:5000/report/')
