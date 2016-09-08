import sys
import time
import json
import websocket


def main():
    ws_url, name = sys.argv[1:]
    long_task(url, name)


def long_task(ws_url, name):
    ws = websocket.WebSocket()
    ws.connect(ws_url)

    total = 150
    for i in range(1, total+1):
        # print(i)
        data = dict(type='progress', name=name, value=i, total=total)
        ws.send(json.dumps(data))
        time.sleep(0.05)

    ws.close()


if __name__ == '__main__':
    main()
