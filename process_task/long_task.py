import sys
import time

from websocketsync import WebSocketClient


def long_task(url):
    with WebSocketClient(url) as client:
        total = 15
        for i in range(1, total+1):
            print(i)
            # import ipdb; ipdb.set_trace()
            client.write(type='progress', value=i, total=total)
            time.sleep(0.05)



if __name__ == '__main__':
    # url = sys.argv[1]
    long_task('ws://localhost:5000/report/')
