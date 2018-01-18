import json
from concurrent import futures

import websocket


def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    ws.send(json.dumps({'topic': 'mytopic', 'action': 'subscribe'}))


def run():
    # ws = websocket.WebSocketApp("ws://118.190.45.196:8888/websocket",
    ws = websocket.WebSocketApp("ws://192.168.56.101:8888/websocket",
    # ws = websocket.WebSocketApp("ws://10.41.2.20:8888/websocket",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()


if __name__ == "__main__":
    pool = futures.ThreadPoolExecutor(max_workers=500)
    for i in range(500):
        pool.submit(run)
        print(i)
