import streamlit as st
from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
import json

def create_dynamic_class(schema):
    class_dict = {}
    exec(f"class DynamicClass:\n    def __init__(self, {', '.join(schema['properties'].keys())}):\n        {'; '.join([f'self.{prop} = {prop}' for prop in schema['properties']])}", class_dict)
    return class_dict['DynamicClass']

def create_json_schema_class(schema):
    schema_str = json.dumps(schema)
    return f'{{"$schema": "http://json-schema.org/draft-04/schema#", "title": "DynamicClass", "type": "object", "properties": {schema_str}, "required": {json.dumps(list(schema["properties"].keys()))}}}'

def create_serializer_function(class_name):
    return f'def {class_name}_to_dict({class_name.lower()}):\n    return {class_name.lower()}.__dict__'

def delivery_report(err, event):
    if err is not None:
        st.error('Delivery failed on reading for {}: {}'.format(event.key().decode("utf8"), err))
    else:
        st.success('Temp reading for {} produced to {}'.format(event.key().decode("utf8"), event.topic()))

# Streamlit UI
st.title('Kafka Producer with Dynamic Schema')

# Input JSON schema
st.header('JSON Schema')
schema_text = st.text_area('Enter JSON Schema')

# Dynamic Dictionary Data
st.header('Dynamic Dictionary Data')
data_text = st.text_area('Enter Dynamic Dictionary Data (JSON format)')

# Submit Button
submit_button = st.button('Produce Messages')

if submit_button:
    try:
        # Parse JSON schema
        schema = json.loads(schema_text)

        # Generate dynamic class, JSON schema, and serializer function
        DynamicClass = create_dynamic_class(schema)
        json_schema = create_json_schema_class(schema)
        serializer_function = create_serializer_function(DynamicClass.__name__)

        # Parse dynamic dictionary data
        dynamic_dictionary_data = json.loads(data_text)

        # Kafka producer configuration
        config = {
            'bootstrap.servers': '<kafka-bootstrap-servers>',
            'security.protocol': 'SASL_SSL',
            'sasl.mechanism': 'PLAIN',
            'sasl.username': '<username>',
            'sasl.password': '<password>',
            'ssl.ca.location': '/path/to/ca.crt',
            'client.id': 'python-producer'
        }

        # Schema Registry configuration
        sr_config = {
            'url': '<schema-registry-url>',
            'basic.auth.user.info': '<username>:<password>'
        }

        # Create Schema Registry client and JSON serializer
        schema_registry_client = SchemaRegistryClient(sr_config)
        json_serializer = JSONSerializer(json_schema, schema_registry_client, eval(serializer_function))

        # Kafka producer setup
        producer = Producer(config)
        topic = 'temp_readings'

        # Produce messages
        for dynamic_data in dynamic_dictionary_data:
            dynamic_object = DynamicClass(**dynamic_data)
            producer.produce(
                topic=topic,
                key=str(dynamic_object.name),
                value=json_serializer(
                    dynamic_object,
                    SerializationContext(topic, MessageField.VALUE)
                ),
                on_delivery=delivery_report
            )

        # Flush producer
        producer.flush()

        st.success('Messages produced successfully!')
    except Exception as e:
        st.error('Error: {}'.format(e))
