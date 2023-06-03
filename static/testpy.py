import csv
import os
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getschema')
def get_schema():
    return render_template('getschema.html')

@app.route('/producer')
def producer():
    return render_template('producer.html')

@app.route('/consumer')
def consumer():
    return render_template('consumer.html')

@app.route('/setconfig')
def set_config():
    return render_template('setconfig.html')

@app.route('/saveconfig', methods=['POST'])
def save_config():
    username = request.form['username']
    password = request.form['password']
    api_key = request.form['api_key']
    api_secret = request.form['api_secret']
    schema_api_key = request.form['schema_api_key']
    schema_api_secret = request.form['schema_api_secret']
    schema_url = request.form['schema_url']
    bootstrap_server = request.form['bootstrap_server']

    config_data = {
        'Username': username,
        'Password': password,
        'API Key': api_key,
        'API Secret': api_secret,
        'Schema API Key': schema_api_key,
        'Schema API Secret': schema_api_secret,
        'Schema URL': schema_url,
        'Bootstrap Server': bootstrap_server
    }

    fieldnames = list(config_data.keys())

    # Remove existing config file if it exists
    if os.path.exists('config.csv'):
        os.remove('config.csv')

    with open('config.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write the header row
        writer.writeheader()

        # Write the config data
        writer.writerow(config_data)

    return 'Configuration saved successfully!'


@app.route('/getconfig')
def get_config():
    config_data = {}

    with open('config.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            config_data = row

    return render_template('getconfig.html', config_data=config_data)

if __name__ == '__main__':
    app.run(debug=True)