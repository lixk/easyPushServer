# easyPushServer
基于bottle和gevent-websocket的简单消息推送服务器  
### 工作原理：  
通过HTTP的POST或者GET方式向消息推送服务器发送消息，消息包括主题(topic)和数据(data)两部分。然后客户端通过websocket协议连接消息推送服务器并订阅对应主题。当有数据发送到推送服务器时，推送服务器通过websocket推送至客户端，由此实现数据的实时推送功能。

在`server.ini`文件中可以定义推送服务器的应用名称，端口号，推送密码，服务器类型等，示例如下：
```ini
[server]
#应用名称
name=myapp
#服务器端口号
port=8080
#推送密码
password=123456
# 服务器类型，'gevent'或者'wsgi'，默认使用'gevent'
#type=gevent
```
### 使用方式
1. 运行 `easyPushServer.py`文件
2. 客户端订阅主题，以浏览器为例，示例代码：
```html
<!DOCTYPE html>
<html>
<head>
  <script src="topic.js"></script>
</head>
<body>
  <script type="text/javascript">
    //连接推送服务器
    var ws = new WebSocket("ws://127.0.0.1:8080/myapp");
    // 订阅名称为'testTopic'的主题
    ws.subscribe('testTopic', function(data){
      alert(data);
    });
    // 取消订阅名称为'testTopic'的主题
    // ws.unsubscribe('testTopic');
  </script>
</body>
</html>
```
注意，需要引入`topic.js`文件，该文件为浏览器WebSocket原型添加了主题订阅和取消订阅功能 
 
3. 推送消息到推送服务器，以python程序为例：
```python
from urllib import request, parse

data = {'topic': 'testTopic', 'data': 'hello world!'}
r = request.urlopen(url='http://127.0.0.1:8080/myapp/publish', data=parse.urlencode(data).encode('utf-8'))
print(r.read().decode('utf-8'))

```
运行之后，控制台打印出推送返回信息：
```python
{"code": 200, "data": "success!"}
```
此时浏览器界面弹出alert对话框：
![推送结果]('https://github.com/lixk/easyPushServer/blob/master/test/screenshot/alert.jpg')  
表明推送成功。

本推送服务器支持多主题，多服务端同时推送消息，内部采用阻塞队列处理。可应用于需要实时推送数据的场景。