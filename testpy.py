import csv
from flask import Flask, render_template, request, redirect, url_for
import requests
import json

app = Flask(__name__)

# Function to fetch the JSON schema from the Confluent Schema Registry
def fetch_schema(schema_url, schema_api_key, schema_api_secret, topic):
    headers = {
        "Content-Type": "application/vnd.schemaregistry.v1+json",
        "Accept": "application/vnd.schemaregistry.v1+json",
        "Authorization": f"Basic {schema_api_key}:{schema_api_secret}"
    }
    url = f"{schema_url}/subjects/{topic}/versions/latest"
    response = requests.get(url, headers=headers)
    return response.json()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getschema', methods=['GET', 'POST'])
def get_schema():
    if request.method == 'POST':
        # Read config data from CSV file
        config_data = {}
        with open('config.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                config_data = row

        # Extract required values
        schema_api_key = config_data.get('Schema API Key')
        schema_api_secret = config_data.get('Schema API Secret')
        schema_url = config_data.get('Schema URL')
        topic = request.form['topic']

        # Fetch JSON schema from Schema Registry
        response = fetch_schema(schema_url, schema_api_key, schema_api_secret, topic)

        return render_template('getschema.html', response=json.dumps(response, indent=4))

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

    with open('config.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(config_data)

    return redirect(url_for('get_config', message='Configuration saved successfully!'))



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
