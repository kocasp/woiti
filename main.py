import network
import socket
import time
from uselect import select
from machine import Pin

#WiFi Settings. Change these before uploading to the Pi Pico
WIFI_SSID = 'cosinus'
WIFI_PASSWORD = 'skotnicka172b'
    
#Set up pins
RED_PIN=28
GREEN_PIN=27
BLUE_PIN=26

red_led =Pin(RED_PIN,Pin.OUT)
green_led =Pin(GREEN_PIN,Pin.OUT)
blue_led =Pin(BLUE_PIN,Pin.OUT)
internal_led = machine.Pin("LED", machine.Pin.OUT)
# OPEN_PIN=19
# CLOSED_PIN=20
# RELAY_PIN=21

#Pulse length in ms
# PULSE_LENGTH=500

#Homekit target and current states
# TARGET_DOOR_STATE_OPEN=0
# TARGET_DOOR_STATE_CLOSED=1
# CURRENT_DOOR_STATE_OPEN = 0
# CURRENT_DOOR_STATE_CLOSED = 1
# CURRENT_DOOR_STATE_OPENING = 2
# CURRENT_DOOR_STATE_CLOSING = 3
# CURRENT_DOOR_STATE_STOPPED = 4


# IGNORE_SENSORS_AFTER_ACTION_FOR_SECONDS=5

#Set initial target and current states
# targetState=TARGET_DOOR_STATE_CLOSED
# currentState=CURRENT_DOOR_STATE_STOPPED

# lastDoorAction=time.time()

#Setup pins for relay and sensors
# relay = Pin(RELAY_PIN, Pin.OUT)
# openSensor=Pin(OPEN_PIN, Pin.IN, Pin.PULL_UP)
# closedSensor=Pin(CLOSED_PIN, Pin.IN, Pin.PULL_UP)

wifi = network.WLAN(network.STA_IF)


def connectWifi():
    global wlan

    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(WIFI_SSID, WIFI_PASSWORD)

    max_wait = 10
    while wifi.status() != 3:
        print('waiting for connection. Status: '+str(wifi.status()))
        time.sleep(1)

    print('connected')
    status = wifi.ifconfig()
    ipAddress=status[0]
    print( 'ip = ' + ipAddress )

connectWifi()

#Set up socket and start listening on port 80
addr = socket.getaddrinfo(wifi.ifconfig()[0], 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

print('listening on', addr)

#Handle an incoming request
def handleRequest(conn, address):
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    request = str(request)

    print(request)

    if request.find('/?red')==6:
        red_led.value(1)
        green_led.value(0)
        blue_led.value(0)
        response="RED"
    elif request.find('/?green')==6:
        red_led.value(0)
        green_led.value(1)
        blue_led.value(0)
        response="GREEN"
    elif request.find('/?blue')==6:
        red_led.value(0)
        green_led.value(0)
        blue_led.value(1)
        response="BLUE"
    else:
        response='UNKNOWN_COMMAND'

    conn.send('HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n')
    conn.send(response)
    conn.close()

#Main Loop
while True:
    #Check if wifi is connected, if not, reconnect
    if wifi.isconnected() == False:
        print('Connecting wifi...')
        connectWifi()

    #Handle incoming HTTP requests in a non-blocking way
    r, w, err = select((s,), (), (), 1)

    #Is there an incoming request? If so, handle the request
    if r:
        for readable in r:
            conn, addr = s.accept()
            try:
                handleRequest(conn, addr)
            except OSError as e:
                pass

