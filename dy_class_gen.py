import json
import jsonschema

def generate_class_from_schema(schema_str):
    # Load the JSON schema
    schema = json.loads(schema_str)

    # Generate the class name
    class_name = schema.get("title", "UnknownClass")

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

# Define the schema string and sample example

schema_str = """
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Food Delivery Order",
  "type": "object",
  "properties": {
    "orderId": {
      "type": "string",
      "description": "The unique identifier of the order"
    },
    "customerName": {
      "type": "string",
      "description": "The name of the customer who placed the order"
    },
    "customerAddress": {
      "type": "string",
      "description": "The delivery address of the customer"
    },
    "items": {
      "type": "array",
      "description": "The list of items in the order",
      "items": {
        "type": "object",
        "properties": {
          "itemId": {
            "type": "string",
            "description": "The unique identifier of the item"
          },
          "itemName": {
            "type": "string",
            "description": "The name of the item"
          },
          "quantity": {
            "type": "integer",
            "description": "The quantity of the item in the order"
          },
          "price": {
            "type": "number",
            "description": "The price of the item"
          }
        },
        "required": ["itemId", "itemName", "quantity", "price"]
      }
    },
    "totalPrice": {
      "type": "number",
      "description": "The total price of the order"
    },
    "deliveryInstructions": {
      "type": "string",
      "description": "Any special instructions for the delivery"
    },
    "paymentMethod": {
      "type": "string",
      "description": "The payment method used for the order"
    }
  },
  "required": ["orderId", "customerName", "customerAddress", "items", "totalPrice", "paymentMethod"]
}
"""

"""
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
"""
"""
sample_example = """
class Employee(object):
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def to_dict(self):
        return {
            "name": self.name,
            "age": self.age
        }
"""
"""


# Generate the class from the schema
generated_class = generate_class_from_schema(schema_str)

# Print the generated class
print(generated_class)
"""
# Validate the generated class against the sample example
try:
    exec(generated_class)
    sample_instance = Employee("John Doe", 30)
    sample_dict = sample_instance.to_dict()
    assert sample_dict == {"name": "John Doe", "age": 30}
    print("Generated class is valid and produces the expected output.")
except Exception as e:
    print("Generated class validation failed:", e)
"""