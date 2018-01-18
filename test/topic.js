/**
 * subscribe a topic
 */
WebSocket.prototype.subscribe = function(topic, callback){
    var _this = this;
    _this.topics = _this.topics || {};
    _this.topics[topic] = callback;
    _this.topicQueue = _this.topicQueue || []
    _this.topicQueue.push({"topic": topic, "action": "subscribe"});  // put this topic to the queue

    _this.onopen = function() {
        setInterval(function(){
            while(_this.topicQueue.length > 0){
                var data = _this.topicQueue.shift();  // take a topic from the queue
                _this.send(JSON.stringify(data));
            }
        }, 100);

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
}

/**
 * unsubscribe a topic
 */
WebSocket.prototype.unsubscribe = function(topic){
    var _this = this;
    _this.topics = _this.topics || {};
    // remove the topic
    delete _this.topics[topic];
    _this.topicQueue = _this.topicQueue || []
    _this.topicQueue.push({"topic": topic, "action": "unsubscribe"});  // put this topic to the queue
    
}