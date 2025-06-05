import network
import socket
import time
import dht
from machine import Pin
from machine import ADC


relay = Pin(3, Pin.OUT)
relay.value(0)
soil_sensor = ADC(Pin(26))
soil = soil_sensor.read_u16()
dht_sensor = dht.DHT11(Pin(1))


ssid = 'AndroidAP345' 
password = 'Suzibumi' 

auto_mode = False
last_auto_water = time.ticks_ms()
last_check = 0
check_interval = 10 

def webpage(soil, temp, humidity, auto):
    auto_state = "Zapnutý" if auto else "Vypnutý"
    toggle_text = "Vypnout auto-režim" if auto else "Zapnout auto-režim"
    html = f"""
                <!DOCTYPE html>
    <html lang="cs">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Web pro květináč</title>

        <style>
                    h1, h2 {{
                font-size: clamp(28px, 8vw, 30px);
                text-align: center;
            }}

            h3{{
                font-size: clamp(23px, 5vw, 26px);
                text-align: center;
            }}

            form{{
                display: grid;
            }}

            form:active{{
                color: white;
                background-color: green;
            }}

            p{{
                text-align: center;
                font-size: clamp(18px, 3vw, 21px);
            }}
        </style>

    </head>
    <body>
            <h1>Raspberry Pi Pico Web Server</h1>
            <br>
            <h2>Zap/Vyp květináč</h2>
            <form action="/toggle">
                <input type="submit" value="{toggle_text}" method="get"/>
            </form>
            <br>
            <br>
            <h3>Zalít rostlinu</h3>
            <form action="/water">
                <input type="submit" value="Zalít teď!" method="get"/>
            </form>
            <br>
            <h3>Dostat nové hodnoty</h3>
            <form action="/value">
                <input type="submit" value="Získat hodnoty" method="get"/>
            </form>
            <br>
            <p><strong>Vlhkost půdy: <strong> {soil}</p> <br>
            <p><strong>Vlhkost vzduchu: <strong> {humidity}%</p> <br>
            <p><strong>Teplota vzduchu: <strong> {temp}°C</p>
    </body>
    </html>
        """
    return str(html)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

connection_timeout = 20
while connection_timeout > 0:
    if wlan.status() >= 3:
        break
    connection_timeout -= 1
    print('Waiting for Wi-Fi connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('Failed to establish a network connection')
else:
    print('Connection successful!')
    network_info = wlan.ifconfig()
    print('IP address:', network_info[0])

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen()

print('Listening on', addr)


while True:

    soil = soil_sensor.read_u16()
    current_time = time.ticks_ms()
    temp = dht_sensor.temperature()
    humidity = dht_sensor.humidity()
    

    if auto_mode is True and time.ticks_diff(current_time, last_auto_water) > 10000:
            if soil > 50000:
                relay.value(1)
                if soil > 45000:
                    relay.value(0)
                    last_auto_water = current_time

    try:
        conn, addr = s.accept()
        print('Got a connection from', addr)

        request = conn.recv(1024)
        print("Request raw:", repr(request))
        request = str(request)
        print('Request content = %s' % request)

        try:
            request = request.split()[1]
            print('Request:', request)
        except IndexError:
            request = '/'


        if request == '/' or request == '/value':
            try:
                soil = soil_sensor.read_u16()

            except Exception as e:
                print("Soil chyba:", e)
                soil = "chyba"

            try:
                dht_sensor.measure()
                temp = dht_sensor.temperature()
                humidity = dht_sensor.humidity()

            except Exception as e:
                print("DHT11 chyba:", e)
                temp = "chyba"
                humidity = "chyba"

        if request == '/water':
            relay.value(1)
            time.sleep(1)
            relay.value(0)

        elif request == '/toggle':
            auto_mode = not auto_mode
            print("Režim přepnutý")
            print("Režim nyní: ", auto_mode)
            

        response = webpage(soil, temp, humidity, auto_mode)


        conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        conn.send(response)
        conn.close()

    except OSError as e:
        print("Chyba připojení:", e)
        try:
            conn.close()
        except:
            pass