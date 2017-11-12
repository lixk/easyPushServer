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
    ws = websocket.WebSocketApp("ws://localhost:8080/myapp",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()


if __name__ == "__main__":
    pool = futures.ThreadPoolExecutor(max_workers=500)
    for i in range(500):
        pool.submit(run)
