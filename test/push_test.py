from urllib import request, parse

data = {'topic': 'testTopic', 'data': 'hello world!', 'password': '123456'}
r = request.urlopen(url='http://127.0.0.1:8080/myapp/publish', data=parse.urlencode(data).encode('utf-8'))
print(r.read().decode('utf-8'))
