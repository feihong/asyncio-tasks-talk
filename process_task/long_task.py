import sys
import time
import json
import random

import websocket


def long_task(url, name):
    ws = websocket.WebSocket()
    ws.connect(url)

    total = 150
    for i in range(1, total+1):
        # print(i)
        data = dict(type='progress', name=name, value=i, total=total)
        ws.send(json.dumps(data))
        time.sleep(0.05)

    ws.close()


if __name__ == '__main__':
    url, name = sys.argv[1:]
    long_task(url, name)
