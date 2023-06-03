import csv
from flask import Flask, render_template, request
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSchema

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

    config_data = [
        username, password, api_key, api_secret,
        schema_api_key, schema_api_secret, schema_url, bootstrap_server
    ]
    with open('config.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(config_data)

    return 'Configuration saved successfully!'

@app.route('/getconfig')
def get_config():
    config_data = []
    with open('config.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            config_data.append(row)
    
    return render_template('getconfig.html', config_data=config_data)

if __name__ == '__main__':
    app.run(debug=True)
