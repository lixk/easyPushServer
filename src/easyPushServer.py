import json
from configparser import ConfigParser
from queue import Queue
import threading

from bottle import request, Bottle, abort, run
from gevent import monkey
from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler

monkey.patch_all()

# read config parameters
config = ConfigParser()
config.read('server.ini')
server_name = config.get("server", "name", fallback='')
if server_name:
    publish_route = '/{}/publish'.format(server_name)
    websocket_route = '/{}'.format(server_name)
else:
    publish_route = '/publish'
    websocket_route = '/'
server_port = config.getint("server", "port", fallback=8080)
server_password = config.get("server", "password", fallback='')
server_type = config.get("server", "type", fallback='gevent')

condition = threading.Condition()
app = Bottle()
message_queue = Queue()
topics = {}


class Message(object):
    """
    message Entity
    
    Args:
        topic: message topic
        data: message data
    """

    def __init__(self, topic, data):
        self.topic = topic
        self.data = data

    def to_json_string(self):
        return json.dumps({'topic': self.topic, 'data': self.data}, ensure_ascii=False)


def json_result(code=200, data=None):
    """
    generate json result string
    
    :param code: return code 200: success, 300: failed, 500: error
    :param data: return data
    :return: 
    """
    return json.dumps({'code': code, 'data': data}, ensure_ascii=False)


@app.route(publish_route, method=['GET', 'POST'])
def publish():
    """
    publish message to the message queue
    """
    try:
        topic = request.params.getunicode('topic')
        data = request.params.getunicode('data')
        # if password is necessary, check the request password
        if server_password and request.params.getunicode('password') != server_password:
            return json_result(300, 'password not right!')
        message_queue.put(Message(topic, data))
        return json_result(200, 'success!')
    except Exception as e:
        return json_result(500, e)


@app.route(websocket_route)
def websocket_handler():
    ws = request.environ.get('wsgi.websocket')
    if not ws:
        abort(400, 'not websocket request.')
    while True:
        try:
            data = ws.receive()
            if not data:
                # remove error client from the topics
                for clients in topics.values():
                    condition.acquire()
                    if ws in clients:
                        clients.remove(ws)
                    condition.release()
                break

            data = json.loads(data)
            topic = data['topic']
            action = data['action']

            # subscribe and unsubscribe topic
            if 'subscribe' == action:
                # if this topic not in the topics dict, add it to the topics dict
                if topic not in topics:
                    topics[topic] = []
                condition.acquire()
                if ws not in topics[topic]:
                    topics[topic].append(ws)
                condition.release()
            elif 'unsubscribe' == action:
                condition.acquire()
                if ws in topics[topic]:
                    topics[topic].remove(ws)
                condition.release()
            else:
                ws.send('error: "action" field can only be "subscribe" or "unsubscribe"')
        except Exception as e:
            try:
                ws.send('error: ' + str(e))
            except WebSocketError as e:
                print('WebSocketError: ' + str(e))


def push_message():
    """
    push message to clients

    """
    while True:
        message = message_queue.get()
        condition.acquire()

        clients = topics.get(message.topic)
        if not clients:
            continue

        # push message to each client
        for i in range(len(clients) - 1, -1, -1):
            client = clients[i]
            try:
                client.send(message.to_json_string())
            except WebSocketError:
                # remove error connection
                clients.pop(i)

        condition.release()


# start a new thread to push message
threading.Thread(target=push_message).start()

# start server
if __name__ == '__main__':
    if server_type == 'wsgi':
        WSGIServer(("0.0.0.0", server_port), app, handler_class=WebSocketHandler).serve_forever()
    else:
        run(app, host='0.0.0.0', port=server_port, server='gevent', handler_class=WebSocketHandler)
