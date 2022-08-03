# range.py Test of asynchronous mqtt client with clean session False.
# (C) Copyright Peter Hinch 2017-2019.
# Released under the MIT licence.

# Public brokers https://github.com/mqtt/mqtt.github.io/wiki/public_brokers

# This demo is for wireless range tests. If OOR the red LED will light.
# In range the blue LED will pulse for each received message.
# Uses clean sessions to avoid backlog when OOR.

# red LED: ON == WiFi fail
# blue LED pulse == message received
# Publishes connection statistics.
from mqtt_as_timeout import MQTTClient
#from mqtt_as import MQTTClient,config
from mqtt_as import config

from config import wifi_led, blue_led
import uasyncio as asyncio
import ubinascii
from machine import unique_id,reset_cause,reset
import sys,time
SUB_TOPIC = '/PING'  # For demo publication and last will use same topic
PUB_TOPIC = '/PONG'
outages = 0
bootFlag=False
async def pulse():  # This demo pulses blue LED each time a subscribed msg arrives.
    blue_led(True)
    await asyncio.sleep(1)
    blue_led(False)


def current_time():
    ctime = time.localtime(time.mktime(time.localtime()) + 28800)
    return "{0}/{1}/{2} {3}:{4}:{5}".format(ctime[0], ctime[1], ctime[2], ctime[3], ctime[4], ctime[5])


def sub_cb(topic, msg, retained):
    global bootFlag
    print((topic, msg))
    msg = msg.decode("utf-8")
    if "rtc" in msg:
        import machine
        import utime
        tm = utime.gmtime(int(msg[msg.find(":")+1:]))
        machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
        bootFlag = True
    if bootFlag:
        t = current_time()
        print('publish', t)
        asyncio.create_task(client.publish(PUB_TOPIC, t, qos = 1))

    asyncio.create_task(pulse())

async def wifi_han(state):
    global outages
    wifi_led(not state)  # Light LED when WiFi down
    if state:
        print('We are connected to broker.')
    else:
        outages += 1
        print('WiFi or broker is down.')
    await asyncio.sleep(1)

async def conn_han(client):
    await client.subscribe(SUB_TOPIC, 1)

async def write_log():
    f=open("boot.txt","a+")
    f.write("online, cause:"+str(reset_cause())+", time:"+current_time()+"\n")
    f.close()

async def get_mqtt_ntp():
    global bootFlag
    await client.publish(PUB_TOPIC, "boot", qos = 1)
    while True:
        if (bootFlag):
            break
        print("wait")
        await asyncio.sleep(0.1)
    #ctime = time.localtime(time.mktime(time.localtime()) + 28800)
    #print("type:",type(ctime[0]))
    #print(ctime[0])

async def main(client):
    try:
        await client.connect()
        print("wan")
        wan=await client.wan_ok()
        print(wan)
        await get_mqtt_ntp()
        print("get time finish")
        await write_log()
        print("save startup time")
        await client.publish(PUB_TOPIC, "online, cause:"+str(reset_cause())+", time:"+current_time(), qos = 1)
    except OSError as e:
        sys.print_exception(e)
        print('Connection failed.')
        reset()
        return
    n = 0
    while True:
        await asyncio.sleep(0.1)
        #print('publish', n)
        ## If WiFi is down the following will pause for the duration.
        #await client.publish(TOPIC, '{} repubs: {} outages: {}'.format(n, client.REPUB_COUNT, outages), qos = 1)
        #n += 1

# Define configuration

config['client_id'] = ubinascii.hexlify(unique_id())
print(ubinascii.hexlify(unique_id()))
SUB_TOPIC = config['client_id'].decode("utf-8")+SUB_TOPIC
PUB_TOPIC = config['client_id'].decode("utf-8")+PUB_TOPIC
print("SUB_TOPIC:",SUB_TOPIC)
print("PUB_TOPIC:",PUB_TOPIC)
config['server'] = 'agri.webduino.io'  # Change to suit e.g. 'iot.eclipse.org'
config['server'] = 'r.webduino.io'  # Change to suit e.g. 'iot.eclipse.org'
config['server'] = 'mqtt1.webduino.io'  # Change to suit e.g. 'iot.eclipse.org'
config['user'] = 'webduino'
config['password'] = 'webduino'

# config['server']='b-981017ae-be5e-48d4-afb6-8b0a77bd76bb-1.mq.ap-northeast-2.amazonaws.com'
# config['port']=8883
# config['ssl']=True
# config['clean']=True
# #config['ssl_params']={'server_hostname': 'broker.emqx.io'}
# config['user'] = 'root'
# config['password'] = '3JTYU9QuMPt9wFXx'


# Required on Pyboard D and ESP32. On ESP8266 these may be omitted (see above).
config['ssid'] = 'KingKit_2.4G'
config['wifi_pw'] = 'webduino'
#config['ssid'] = 'webai_qc'
#config['wifi_pw'] = 'webai_qc'



config['subs_cb'] = sub_cb
config['wifi_coro'] = wifi_han
config['will'] = (PUB_TOPIC, 'offline', True, 0)
config['connect_coro'] = conn_han
config['keepalive'] = 10

# Set up client. Enable optional debug statements.
MQTTClient.DEBUG = True
client = MQTTClient(config)
try:
    asyncio.run(main(client))
except Exception as e:
    print(sys.print_exception(e))
    reset()
finally:  # Prevent LmacRxBlk:1 errors.
    client.close()
    blue_led(True)
    asyncio.new_event_loop()




# Rst cause No. Cause                    GPIO state
# 0             Power reboot             Changed
# 1             Hardware WDT reset       Changed
# 2             Fatal exception          Unchanged
# 3             Software watchdog reset  Unchanged
# 4             Software reset           Unchanged
# 5             Deep-sleep               Changed
# 6             Hardware reset           Changed