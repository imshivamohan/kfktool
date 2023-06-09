from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer

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

class Employee(object):
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def to_dict(self):
        return {
            "name": self.name,
            "age": self.age
        }

schema_str = """{
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
}"""

def employee_to_dict(employee, ctx):
    return employee.to_dict()

data = [
    {"name": "siva", "age": 30},
    {"name": "Mohan", "age": 25}
]

def delivery_report(err, event):
    if err is not None:
        print(f'Delivery failed on reading for {event.key().decode("utf8")}: {err}')
    else:
        print(f'Temp reading for {event.key().decode("utf8")} produced to {event.topic()}')

if __name__ == '__main__':
    topic = 'temp_readings'
    schema_registry_client = SchemaRegistryClient(sr_config)

    json_serializer = JSONSerializer(schema_str, schema_registry_client, employee_to_dict)

    producer = Producer(config)
    for employee_data in data:
        employee = Employee(employee_data['name'], employee_data['age'])
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
