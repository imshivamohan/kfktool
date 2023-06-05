from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
import json
import jsonschema


config = {
    'bootstrap.servers': '<kafka-bootstrap-servers>',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': '<username>',
    'sasl.password': '<password>',
    'ssl.ca.location': '/path/to/ca.crt',
    'client.id': 'python-producer'
}

sr_config = {
    'url': '<schema-registry-url>',
    'basic.auth.user.info': '<username>:<password>'
}


def generate_class_from_schema(schema_str):
    # Load the JSON schema
    schema = json.loads(schema_str)

    # Generate the class name using standard naming conventions
    title = schema.get("title", "UnknownClass")
    class_name = "".join(x.capitalize() or "_" for x in title.split("_"))

    # Generate the class properties and initializer
    properties = schema.get("properties", {})
    properties_str = ""
    initializer_args = ""
    initializer_assignments = ""
    for prop_name, prop_schema in properties.items():
        prop_type = prop_schema.get("type", "UnknownType")
        properties_str += f'    {prop_name} = None\n'
        initializer_args += f'{prop_name}, '
        initializer_assignments += f'        self.{prop_name} = {prop_name}\n'

    # Generate the class definition
    class_definition = f'class {class_name}(object):\n'
    class_definition += properties_str
    class_definition += '\n    def __init__(self, ' + initializer_args.rstrip(', ') + '):\n'
    class_definition += initializer_assignments.rstrip('\n') + '\n\n'
    class_definition += '    def to_dict(self):\n'
    class_definition += '        return {\n'
    for prop_name in properties.keys():
        class_definition += f'            "{prop_name}": self.{prop_name},\n'
    class_definition += '        }'

    return class_definition


def generate_serializer(class_obj):
    class_name = class_obj.__name__

    # Generate the serializer function definition
    serializer_def = f'def serialize_{class_name}(obj, serialization_context):\n'

    # Generate the function body
    serializer_body = f'    if isinstance(obj, {class_name}):\n'
    serializer_body += '        return obj.to_dict()\n'
    serializer_body += '    else:\n'
    serializer_body += '        return {}\n'

    # Generate the full serializer function
    serializer_func = serializer_def + serializer_body

    return serializer_func


def delivery_report(err, event):
    if err is not None:
        print(f'Delivery failed on reading for {event.key().decode("utf8")}: {err}')
    else:
        print(f'Temp reading for {event.key().decode("utf8")} produced to {event.topic()}')


if __name__ == '__main__':
    schema_str = """
    {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "Employee",
        "type": "object",
        "properties": {
            "name": {
                "type": "string"
            },
            "age": {
                "type": "integer"
            }
        },
        "required": [
            "name",
            "age"
        ]
    }
    """

    # Generate the class from the schema
    generated_class = generate_class_from_schema(schema_str)

    # Execute the generated class dynamically
    namespace = {}
    exec(generated_class, namespace)
    GeneratedClass = namespace['GeneratedClass']

    # Generate the serializer function for the generated class
    serializer_func = generate_serializer(GeneratedClass)

    # Execute the generated serializer function dynamically
    exec(serializer_func, namespace)
    serializer = namespace[f'serialize_{GeneratedClass.__name__}']

    # Sample data
    data = [
        {"name": "John", "age": 30},
        {"name": "Jane", "age": 25}
    ]

    topic = 'temp_readings'
    schema_registry_client = SchemaRegistryClient(sr_config)

    json_serializer = JSONSerializer(schema_str, schema_registry_client, serializer)

    producer = Producer(config)
    for employee_data in data:
        employee = GeneratedClass(employee_data['name'], employee_data['age'])
        producer.produce(
            topic=topic,
            key=str(employee.name),
            value=json_serializer(
                employee,
                SerializationContext(topic, MessageField.VALUE)
            ),
            on_delivery=delivery_report
        )

    producer.flush()
