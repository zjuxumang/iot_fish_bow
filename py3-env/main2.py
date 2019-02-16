# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import time
import hashlib
import hmac
import random
import json
import RPi.GPIO as GPIO
import sys
from w1thermsensor import W1ThermSensor
options = {
    'productKey':'a1ZQ5vcZGjQ',
    'deviceName':'my_device',
    'deviceSecret':'DcvU31CVQ4QyDXxkZs4IpdVYxT5nWdVP',
    'regionId':'cn-shanghai'
}

HOST = options['productKey'] + '.iot-as-mqtt.'+options['regionId']+'.aliyuncs.com'
PORT = 1883 
PUB_TOPIC = "/sys/" + options['productKey'] + "/" + options['deviceName'] + "/thing/event/property/post";
EVENT_TOPIC = "/sys/" + options['productKey'] + "/" + options['deviceName'] + "/thing/event/feed_finish/post";


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    global CONNECTED
    print("Connected with result code "+str(rc))
    CONNECTED = True
    # client.subscribe("the/topic")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    topic=str(msg.topic)
    if topic.endswith('property/set'):
        global ledstate
        setjson = json.loads(str(msg.payload,encoding="utf8"))
        try:
            ledstate = setjson['params']['LEDSwitch']
            print("turn light on" if ledstate==1 else "turn light off")
            
        except:
            pass
    elif topic.endswith('service/feed'):
        print("feed")
        feed(1)
    
def feed(t):
    p.ChangeDutyCycle(10)
    time.sleep(0.5*t)
    p.ChangeDutyCycle(5)
    time.sleep(0.5)
    p.ChangeDutyCycle(0)


def hmacsha1(key, msg):
    return hmac.new(key.encode(), msg.encode(), hashlib.sha1).hexdigest()

def getAliyunIoTClient():
    timestamp = str(int(time.time()))
    CLIENT_ID = "paho.py|securemode=3,signmethod=hmacsha1,timestamp="+timestamp+"|"
    CONTENT_STR_FORMAT = "clientIdpaho.pydeviceName"+options['deviceName']+"productKey"+options['productKey']+"timestamp"+timestamp
    # set username/password.
    USER_NAME = options['deviceName']+"&"+options['productKey']
    PWD = hmacsha1(options['deviceSecret'],CONTENT_STR_FORMAT)
    client = mqtt.Client(client_id=CLIENT_ID, clean_session=False)
    client.username_pw_set(USER_NAME, PWD)
    return client


if __name__ == '__main__':

    CONNECTED = False
    client = getAliyunIoTClient()
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.connect(HOST, 1883, 300)

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(8,GPIO.OUT)
    p = GPIO.PWM(8,50)
    p.start(0)
    time.sleep(0.5)
    p.ChangeDutyCycle(5)
    time.sleep(1)
    p.ChangeDutyCycle(0) 
    
    try:
        sensor = W1ThermSensor()
    except:
        print("ThermSensor is not connected!")
    ledstate=0
    last_feed_tm=0
    client.loop_start()

    while True:
        try:
            if CONNECTED:
                payload_json = {
                        'id': int(time.time()),
                        'params': {
                            'WaterTemperature': random.randint(20, 30),
                            'LEDSwitch': ledstate
                            },
                        'method': "thing.event.property.post"
                        }
                #print('send data to iot server: ' + str(payload_json))
                client.publish(PUB_TOPIC,payload=str(payload_json),qos=1)
                time.sleep(5)
            else:
                time.sleep(1)
            localtime=time.localtime()
            if localtime.tm_hour in [9,13,18]:
                if localtime.tm_hour != last_feed_tm:
                    feed(1)
                    last_feed_tm=localtime.tm_hour;
                    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    print("last feed time: "+now_time) 
                    payload_json = {
                        'id': int(time.time()),
                        'params': {
                            'feed_time': now_time
                            },
                        'method': "thing.event.feed_finish.post"
                        }
                    #print('send data to iot server: ' + str(payload_json))
                    client.publish(EVENT_TOPIC,payload=str(payload_json),qos=1)

        except KeyboardInterrupt:
            client.loop_stop()
            client.disconnect()
            GPIO.cleanup()
            sys.exit()
