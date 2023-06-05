from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
import json

def create_dynamic_class(schema):
    class_dict = {}
    exec(f"class DynamicClass:\n    def __init__(self, {', '.join(schema['properties'].keys())}):\n        {'; '.join([f'self.{prop} = {prop}' for prop in schema['properties']])}", class_dict)
    return class_dict['DynamicClass']

def dynamicClass_to_dict(dynamic_class):
    return dynamic_class.__dict__

def delivery_report(err, event):
    if err is not None:
        print('Delivery failed on reading for {}: {}'.format(event.key().decode("utf8"), err))
    else:
        print('Temp reading for {} produced to {}'.format(event.key().decode("utf8"), event.topic()))

# Input JSON schema
schema = {
    "title": "Employee",
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}
    },
    "required": ["name", "age"]
}

# Dynamic Dictionary Data
dynamic_dictionary_data = [
    {"name": "John", "age": 30},
    {"name": "Jane", "age": 25}
]

# Generate dynamic class
DynamicClass = create_dynamic_class(schema)

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
json_serializer = JSONSerializer(schema, schema_registry_client, dynamicClass_to_dict)

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
