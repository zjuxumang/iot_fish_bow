import sys
from linkkit import linkkit
import threading
import time
import RPi.GPIO as GPIO
import random

lk = linkkit.LinkKit(
    host_name="cn-shanghai",
    product_key="a1ZQ5vcZGjQ",
    device_name="my_device",
    device_secret="DcvU31CVQ4QyDXxkZs4IpdVYxT5nWdVP")

def on_connect(session_flag, rc, userdata):
    print("on_connect:%d,rc:%d" % (session_flag, rc))
    pass


def on_disconnect(rc, userdata):
    print("on_disconnect:rc:%d,userdata:" % rc)


def on_topic_message(topic, payload, qos, userdata):
    global p
    print("on_topic_message:" + topic + " payload:" + str(payload) + " qos:" + str(qos))
    if topic.endwith('cmd'):
        p.ChangeDutyCycle(10)
        time.sleep(1)
        p.ChangeDutyCycle(5)
        time.sleep(1)
        p.ChangeDutyCycle(0)


def on_subscribe_topic(mid, granted_qos, userdata):
    print("on_subscribe_topic mid:%d, granted_qos:%s" %
          (mid, str(','.join('%s' % it for it in granted_qos))))
    pass


def on_unsubscribe_topic(mid, userdata):
    print("on_unsubscribe_topic mid:%d" % mid)
    pass


def on_publish_topic(mid, userdata):
    print("on_publish_topic mid:%d" % mid)

def on_thing_enable(userdata):
    print("on_thing_enable")

def on_thing_disable(userdata):
    print("on_thing_disable")
def on_thing_prop_post(request_id, code, data, message,userdata):
    print("on_thing_prop_post request id:%s, code:%d, data:%s message:%s" %(request_id, code, str(data), message))
def on_thing_prop_changed(params, userdata):
    print("on_thing_prop_changed params:" + str(params))

lk.on_connect = on_connect
lk.on_disconnect = on_disconnect
lk.on_topic_message = on_topic_message
lk.on_subscribe_topic = on_subscribe_topic
lk.on_unsubscribe_topic = on_unsubscribe_topic
lk.on_publish_topic = on_publish_topic
lk.on_thing_enable = on_thing_enable
lk.on_thing_disable = on_thing_disable
lk.on_thing_prop_post = on_thing_prop_post
lk.on_thing_prop_changed = on_thing_prop_changed

lk.thing_setup("reducedModel.json")
lk.config_device_info("Eth|03ACDEFF0032|Eth|03ACDEFF0031")
lk.connect_async()
lk.start_worker_loop()
while lk.check_state()!=lk.LinkKitState.CONNECTED:
    time.sleep(1)

rc, mid = lk.subscribe_topic(lk.to_full_topic("user/cmd"))
if rc == 0:
    print("subscribe topic success:%r, mid:%r" % (rc, mid))
else:
    print("subscribe topic fail:%d" % rc)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(8,GPIO.OUT)
p = GPIO.PWM(8,50)
p.start(0)
time.sleep(1)
p.ChangeDutyCycle(5)
time.sleep(1)
p.ChangeDutyCycle(0)

while True:
    try:
        prop_data = {
            "WaterTemperature": 25,
            "LEDSwitch": 0
        }
        lk.thing_post_property(prop_data)
        time.sleep(5)
    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit()
      
