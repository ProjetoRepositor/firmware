import serial
import json
import subprocess
import os

serial_port = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

def configure_wifi(ssid, password):
    config_lines = [
        'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev',
        'update_config=1',
        'country=BR',
        '\n',
        'network={',
        '\tssid="{}"'.format(ssid),
        '\tpsk="{}"'.format(password),
        '\tkey_mgmt=WPA-PSK',
        '}'
        ]
    config = '\n'.join(config_lines)
    
    #give access and writing. may have to do this manually beforehand
    os.popen("sudo chmod a+w /etc/wpa_supplicant/wpa_supplicant.conf")
    
    #writing to file
    with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as wifi:
        wifi.write(config)
    
    print("Wifi config added. Refreshing configs")
    ## refresh configs
    os.popen("sudo wpa_cli -i wlan0 reconfigure")

while True:
    # Verifica se há dados disponíveis para leitura
    if serial_port.in_waiting > 0:
        # Lê os dados recebidos da porta serial
        serial_data = serial_port.readline().decode('utf-8')
        try:
            # Tenta interpretar os dados recebidos como um JSON
            data = json.loads(serial_data)
            print(data)
            ssid = data.get('ssid')
            password = data.get('password')
            token = data.get('token')
            if ssid and password and token:
                # Configura o Wi-Fi com os dados recebidos
                configure_wifi(ssid, password)
                print(os.system(f'sudo echo "{token}" > /home/victor/token.txt'))
        except json.JSONDecodeError:
            print("Erro ao decodificar JSON")

