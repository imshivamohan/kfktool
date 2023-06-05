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

# Generate dynamic class, JSON schema, and serializer function
DynamicClass = create_dynamic_class(schema)
json_schema = create_json_schema_class(schema)
serializer_function = create_serializer_function(DynamicClass.__name__)

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
