from flask import Flask, render_template, request, redirect, url_for
import socket
from datetime import datetime
import json
import os

app = Flask(__name__)

# Перевірка наявності директорії для збереження даних
if not os.path.exists('storage'):
    os.makedirs('storage')

# Функція для збереження повідомлення у файл data.json
def save_message(username, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    data = {
        timestamp: {
            "username": username,
            "message": message
        }
    }
    with open('storage/data.json', 'a+') as file:
        file.seek(0)
        data_list = json.load(file)
        data_list.update(data)
        file.seek(0)
        json.dump(data_list, file, indent=4)

# Головна сторінка
@app.route('/')
def index():
    return render_template('index.html')

# Сторінка для введення повідомлення
@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form['username']
        message = request.form['message']
        save_message(username, message)
        return redirect(url_for('index'))
    return render_template('message.html')

# Сторінка для обробки помилки 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

# Socket сервер для обробки даних
def socket_server():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, addr = sock.recvfrom(1024)
        data = data.decode('utf-8').split(',')
        save_message(data[0], data[1])

if __name__ == '__main__':
    # Запускаємо socket сервер у окремому потоці
    import threading
    socket_thread = threading.Thread(target=socket_server)
    socket_thread.start()
    # Запускаємо веб-додаток на порті 3000
    app.run(port=3000)
