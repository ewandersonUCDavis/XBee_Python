import paho.mqtt.client as mqtt

def on_connect(mqttc, obj, flags, rc):
    print("on_connect")
    print("rc: " + str(rc))
    apple = mqttc.publish(topicAttr, '{"turbineOnOff_switch":True}', qos=1, retain=True)
    print('published: '+str(apple.is_published()))
    apple.wait_for_publish()
    print('published: '+str(apple.is_published()))


def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))
    pass


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)
    
mqttClientId     = "ewanderson" #This can be anything, but you have to pick a unique Id so thingsboard can keep track of what messages it has already sent you.
mqttBroker = "192.155.83.191" #This is the instance of thingsboard that we installed on ???
mqttUserName     = "OKYS34HzHCWOHWSckxL4" #this is the access token for the thingsboard gateway device
topicAttr = "v1/devices/me/attributes" #This is the topic for sending attributes through a gateway in thingsboard  
rpcTopic = "v1/devices/me/rpc/request/+"  #This is the topic that Thingsboard switches will publish to.


mqttc = mqtt.Client(mqttClientId,clean_session=False)
mqttc.username_pw_set(mqttUserName) 
mqttc.connect(mqttBroker)
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe



mqttc.loop_start()


apple = mqttc.publish(topicAttr, '{"turbineOnOff_switch":True}', qos=1, retain=True)
print('published: '+str(apple.is_published()))
apple.wait_for_publish()
print('published: '+str(apple.is_published()))

