import random
import string
import threading

import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, redirect, url_for, jsonify

from sendmail import send_email

app = Flask(__name__)

url = "https://frixx.ge/code"
generated_codes = set()
process_thread = None
running = False


def check_codes(code):
    cookies = {
        'PHPSESSID': '81r4d8et5jg2obau4q836bjg75',
        # '_fbc': 'fb.1.1718391549391.IwZXh0bgNhZW0CMTAAAR1PY1LQngY_fGQNdyFZiELBYwC1xEYtcihacLebiaNMaEb1DyEeH3zlwy4_aem_ZmFrZWR1bW15MTZieXRlcw',
        '_fbp': 'fb.1.1718897614930.208149441986148181',
        '_ga': 'GA1.1.1577307525.1718897615',
        f"_ga_7ZV1YGSDY0": 'GS1.1.1720275473.7.1.1720275495.0.0.0'
    }

    session = requests.Session()
    session.cookies.update(cookies)
    try:
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form', id='myForm')
        form_data = {'code': code, 'submit': 'პრიზის ნახვა'}
        form_action = form.get('action', url)
        response = session.post(form_action, data=form_data)
        if not "კოდი არასწორია..." in response.text:
            print(f'You Win with code: {code}')
            send_email('Congrats', f'You Win with code: {code}', 'akogachechiladze22@gmail.com')
    except Exception:
        print(code)


def generate_random_code(length=6):
    characters = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choice(characters) for _ in range(length))
        if code not in generated_codes:
            generated_codes.add(code)
            return code


def run_code():
    global running
    num_codes = 1000000
    for i in range(num_codes):
        if not running:
            break
        if i % 1000 == 0:
            print(i)
        random_code = generate_random_code()
        try:
            check_codes(random_code)
        except Exception:
            continue


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start', methods=['POST'])
def start():
    global process_thread, running
    if not running:
        running = True
        process_thread = threading.Thread(target=run_code)
        process_thread.start()
    return redirect(url_for('index'))


@app.route('/stop', methods=['POST'])
def stop():
    global running
    running = False
    if process_thread:
        process_thread.join()
    return redirect(url_for('index'))


@app.route('/status', methods=['GET'])
def status():
    global running
    return jsonify(running=running)


if __name__ == '__main__':
    app.run(debug=True)
