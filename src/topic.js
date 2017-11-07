/**
 * subscribe a topic
 */
WebSocket.prototype.subscribe = function(topic, callback){
    var _this = this;
    _this.topics = _this.topics || {};
    _this.topics[topic] = callback;
    _this.newTopicQueue = _this.newTopicQueue || []
    _this.newTopicQueue.push(topic);  //将新订阅的主题加入队列
    _this.onopen = function() {
        setInterval(function(){
            while(_this.newTopicQueue.length > 0){
                var topic = _this.newTopicQueue.shift();
                _this.send(JSON.stringify({"topic": topic, "action": "subscribe"}));
            }
        }, 100);

    }

    _this.onmessage = function(event){
        var data = event.data;
        try {
            data = JSON.parse(data);
            var callback = _this.topics[data.topic];
            callback(data.data);
        }catch(e){
            console.error(data);
        }
    }

    _this.onclose = function(){
        console.info('connection closed!');
    }
    _this.onerror = function(){
        console.error('connection error!');
    }
}

/**
 * unsubscribe a topic
 */
WebSocket.prototype.unsubscribe = function(topic){
    var _this = this;
    _this.topics = _this.topics || {};
    delete _this.topics[topic];
    _this.send(JSON.stringify({"topic": topic, "action": "unsubscribe"}));
    
}