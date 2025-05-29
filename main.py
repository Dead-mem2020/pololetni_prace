# Complete project details at https://RandomNerdTutorials.com/raspberry-pi-pico-web-server-micropython/

# Importování modulů
import network
import socket
import time
import dht
from machine import Pin
from machine import ADC

# Create an LED object on pin 'LED'
relay = Pin(15, Pin.OUT)
relay.value(0)  # relé je z prva vypnuté
soil_sensor = ADC(Pin(26))
soil = soil_sensor.read_u16()
dht_sensor = dht.DHT11(Pin(14))


# Wi-Fi údaje
ssid = 'AndroidAP345' # nebo-li jméno sítě
password = 'Suzibumi' # heslo do té sítě 

auto_mode = False
last_check = 0
check_interval = 10

# HTML template for the webpage
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
        <p>Načtené hodnoty:</p> <br>
        <p><strong>Půda: <strong> {soil}</p> <br>
        <p><strong>Vlhkost vzduchu: <strong> {humidity}%</p> <br>
        <p><strong>Teplota vzduchu: <strong> {temp}°C</p>
    </body>
    </html>
        """
    return str(html)

# Connect to WLAN
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Wait for Wi-Fi connection
connection_timeout = 10
while connection_timeout > 0:
    if wlan.status() >= 3:
        break
    connection_timeout -= 1
    print('Waiting for Wi-Fi connection...')
    time.sleep(1)

# Check if connection is successful
if wlan.status() != 3:
    raise RuntimeError('Failed to establish a network connection')
else:
    print('Connection successful!')
    network_info = wlan.ifconfig()
    print('IP address:', network_info[0])

# Set up socket and start listening
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen()

print('Listening on', addr)

last_auto_water = time.ticks_ms()

soil = "-"
temp = "-"
humidity = "-"

# Main loop to listen for connections
while True:

    if auto_mode = True
        try time.ticks_diff(current_time, last_auto_water) > 10000:
            soil_value = soil_sensor.read_u16()
            if soil_value > 50000:
                relay.value(1)
                time.sleep(2)
                relay.value(0)
            last_auto_water = current_time

        try:
            conn, addr = s.accept()
            print('Got a connection from', addr)
            
            # Receive and parse the request
            request = conn.recv(1024)
            print("Request raw:", repr(request))
            request = str(request)
            print('Request content = %s' % request)


            try:
                request = request.split()[1]
                print('Request:', request)
            except IndexError:
                pass
            

            if request == '/value':
                soil = soil_sensor.read_u16()

                try:
                    dht_sensor.measure()
                    temp = dht_sensor.temperature()
                    humidity = dht_sensor.humidity()
                except Exception as e:
                    print("DHT11 chyba:", e)
                    temp = "chyba"
                    humidity = "chyba"

            elif request == '/water':
                print("Zalévání spuštěno")
                relay.value(1)
                time.sleep(1)
                relay.value(0)


            # odpověď od HTML
            response = webpage(soil)
            response = webpage(temp)
            response = webpage(humidity)  

            # Send the HTTP response and close the connection
            conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            conn.send(response)
            conn.close()

        except OSError as e:
            conn.close()
            print('Connection closed')

        else:
            break