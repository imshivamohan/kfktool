import json
import re

class_template = """
public class {class_name} {{
{properties}
}}
"""

def convert_to_valid_identifier(name):
    # Remove special characters and spaces
    name = re.sub(r"[^\w]", "", name)
    # Handle leading digits by appending underscore
    if name[0].isdigit():
        name = "_" + name
    return name

def generate_java_code(schema, class_name):
    properties = ""

    for property_name, property_info in schema.items():
        # Convert property name to valid Java identifier
        java_property_name = convert_to_valid_identifier(property_name)

        if "type" in property_info and property_info["type"] == "object":
            nested_class_name = property_name.capitalize()
            nested_class_code = generate_java_code(property_info["properties"], nested_class_name)
            properties += f"  public {nested_class_name} {java_property_name};\n\n"
            properties += nested_class_code  # Add nested class code
        elif "type" in property_info and property_info["type"] == "array":
            if "items" in property_info:
                if "type" in property_info["items"]:
                    array_type = property_info["items"]["type"]
                    if array_type == "object":
                        nested_class_name = property_name.capitalize()
                        nested_class_code = generate_java_code(property_info["items"]["properties"], nested_class_name)
                        properties += f"  public {nested_class_name}[] {java_property_name};\n\n"
                        properties += nested_class_code  # Add nested class code
                    else:
                        properties += f"  public {array_type}[] {java_property_name};\n\n"
                        # Generate separate class for array items
                        array_item_class_name = property_name.capitalize() + "Item"
                        array_item_properties = {property_name: property_info["items"]}
                        array_item_code = generate_java_code(array_item_properties, array_item_class_name)
                        properties += array_item_code
                else:
                    properties += f"  public Object[] {java_property_name};\n\n"
            else:
                properties += f"  public Object[] {java_property_name};\n\n"
        elif "oneOf" in property_info:
            oneof_classes = []
            for oneof_property in property_info["oneOf"]:
                ref_id = oneof_property["$ref"].split("/")[-1]
                oneof_class_name = convert_to_valid_identifier(ref_id.capitalize())
                oneof_class_code = generate_java_code(definitions[ref_id]["properties"], oneof_class_name)
                oneof_classes.append(oneof_class_name)
                properties += oneof_class_code
            properties += f"  public OneOf<{', '.join(oneof_classes)}> {java_property_name};\n\n"
        else:
            property_type = property_info.get("type", "Object")
            properties += f"  public {property_type} {java_property_name};\n\n"

    return class_template.format(class_name=class_name, properties=properties)


def generate_java_pojos(json_schema):
    schema = json.loads(json_schema)
    definitions = schema.get("definitions", {})
    java_code = generate_java_code(schema["properties"], "Root")
    with open("Root.java", "w") as file:
        file.write(java_code)


# Example JSON schema
json_schema = """
{
  "type": "object",
  "properties": {
    "header": {
      "$ref": "#/definitions/Header"
    },
    "payload": {
      "$ref": "#/definitions/Payload"
    }
  },
  "definitions": {
    "Header": {
      "type": "object",
      "properties": {
        "publishername": {
          "type": "string"
        },
        "eventname": {
          "type": "string"
        }
      },
      "required": ["publishername", "eventname"]
    },
    "Payload": {
      "type": "object",
      "properties": {
        "applicationinitiated": {
          "oneOf": [
            {"$ref": "#/definitions/ApplicationInitiatedType1"},
            {"$ref": "#/definitions/ApplicationInitiatedType2"},
            {"$ref": "#/definitions/ApplicationInitiatedType3"}
          ]
        }
      }
    },
    "ApplicationInitiatedType1": {
      "type": "object",
      "properties": {
        "property1": {
          "type": "string",
          "enum": ["value1", "value2", "value3"]
        },
        "nestedobj": {
          "$ref": "#/definitions/NestedObject"
        }
      }
    },
    "ApplicationInitiatedType2": {
      "type": "object",
      "properties": {
        "property2": {
          "type": "string",
          "enum": ["value4", "value5", "value6"]
        }
      }
    },
    "ApplicationInitiatedType3": {
      "type": "object",
      "properties": {
        "property3": {
          "type": "string",
          "enum": ["value7", "value8", "value9"]
        }
      }
    },
    "NestedObject": {
      "type": "object",
      "properties": {
        "nestedproperty": {
          "type": "string"
        }
      }
    }
  }
}
"""

generate_java_pojos(json_schema)

#######################




































from jinja2 import Environment, Template
import requests

def fetch_json_schema(url):
    """
    Fetches the JSON schema from the provided URL.
    Returns the JSON schema as a dictionary.
    """
    response = requests.get(url)
    response.raise_for_status()
    json_schema = response.json()
    return json_schema

def generate_java_type(property_schema):
    """
    Generates the Java type for a given property schema,
    considering custom type mappings and handling arrays.
    """
    if "type" in property_schema:
        prop_type = property_schema["type"]
        if prop_type == "array":
            items_schema = property_schema.get("items", {})
            if "$ref" in items_schema:
                ref_type = items_schema["$ref"].split("/")[-1]
                return f"List<{ref_type}>"
            elif "type" in items_schema:
                item_type = generate_java_type(items_schema)
                return f"List<{item_type}>"
        elif prop_type == "object":
            if "$ref" in property_schema:
                ref_type = property_schema["$ref"].split("/")[-1]
                return ref_type
            else:
                return "Object"
        elif prop_type in custom_type_mappings:
            return custom_type_mappings[prop_type]

    # Default to Object type if no specific mapping found
    return "Object"

def generate_class_properties(properties, indent=""):
    """
    Generates the Java class properties code block recursively,
    considering nested objects and arrays.
    """
    code = ""
    for prop, prop_schema in properties.items():
        prop_type = generate_java_type(prop_schema)
        if prop_type:
            code += f"{indent}private {prop_type} {prop};\n"

        if "properties" in prop_schema:
            nested_props = prop_schema["properties"]
            code += generate_class_properties(nested_props, indent)

    return code

def generate_getters_setters(properties, indent=""):
    """
    Generates the Java getters and setters code block recursively,
    considering nested objects and arrays.
    """
    code = ""
    for prop, prop_schema in properties.items():
        prop_type = generate_java_type(prop_schema)
        if prop_type:
            code += f"\n{indent}public {prop_type} get{prop.capitalize()}() {{\n"
            code += f"{indent}    return {prop};\n"
            code += f"{indent}}}\n"

            code += f"\n{indent}public void set{prop.capitalize()}({prop_type} {prop}) {{\n"
            code += f"{indent}    this.{prop} = {prop};\n"
            code += f"{indent}}}\n"

        if "properties" in prop_schema:
            nested_props = prop_schema["properties"]
            code += generate_getters_setters(nested_props, indent)

    return code

# URL for fetching the JSON schema
json_schema_url = "https://example.com/json-schema"

# Fetch the JSON schema from the schema registry
json_schema = fetch_json_schema(json_schema_url)

# Custom type mappings (JSON type to Java type)
custom_type_mappings = {
    "integer": "int",
    "string": "String",
    "boolean": "boolean",
    "number": "double"
}

# Extract the class name from the title or use a default class name
title = json_schema.get("title", "Newgenpojoclass")
class_name_parts = title.split()
class_name = class_name_parts[0].capitalize()

# Define the Jinja2 template for the Java POJO
template_str = """
public class {{ class_name }} {
    {% for prop, prop_schema in properties.items() %}
    private {{ generate_java_type(prop_schema) }} {{ prop }};
    {% endfor %}

    public {{ class_name }}() {
    }

    public {{ class_name }}({% for prop, prop_schema in properties.items() %}{{ generate_java_type(prop_schema) }} {{ prop }}{% if not loop.last %}, {% endif %}{% endfor %}) {
        super();
        {% for prop, prop_schema in properties.items() %}
        this.{{ prop }} = {{ prop }};
        {% endfor %}
    }

    {% for prop, prop_schema in properties.items() %}
    public {{ generate_java_type(prop_schema) }} get{{ prop.capitalize() }}() {
        return {{ prop }};
    }

    public void set{{ prop.capitalize() }}({{ generate_java_type(prop_schema) }} {{ prop }}) {
        this.{{ prop }} = {{ prop }};
    }
    {% endfor %}

    @Override
    public String toString() {
        return "{{ class_name }} ("
                {% for prop, prop_schema in properties.items() %}
                + "{{ prop }}=" + {{ prop }} + ", "
                {% endfor %}
                + "]";
    }

    public void validate() throws IllegalArgumentException {
        {% for prop in required_fields %}
        if ({{ prop }} == null || {{ prop }}.isEmpty()) {
            throw new IllegalArgumentException("{{ prop }} must not be null or empty.");
        }
        {% endfor %}
    }
}
"""

# Create a Jinja2 environment and register the custom functions as filters
env = Environment()
env.filters["generate_java_type"] = generate_java_type

# Create a Jinja2 template object
template = env.from_string(template_str)

# Get the list of required fields
required_fields = json_schema.get("required", [])

# Render the template with the data from the JSON schema
rendered_code = template.render(
    class_name=class_name,
    properties=json_schema['properties'],
    required_fields=required_fields
)

# Print the generated Java code
print(rendered_code)
###################################

















from jinja2 import Environment, Template
import json

# JSON schema as a string
json_schema_str = '''
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Employee",
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "email": {"type": "string"}
    },
    "required": ["name", "age"]
}
'''

# Custom type mappings (JSON type to Java type)
custom_type_mappings = {
    "integer": "int",
    "string": "String",
    "boolean": "boolean",
    "number": "double"
}

# Parse the JSON schema string into a dictionary
json_schema = json.loads(json_schema_str)


def generate_java_type(property_schema):
    """
    Generates the Java type for a given property schema,
    considering custom type mappings and handling arrays.
    """
    if "type" in property_schema:
        prop_type = property_schema["type"]
        if prop_type == "array":
            items_schema = property_schema.get("items", {})
            if "type" in items_schema:
                item_type = generate_java_type(items_schema)
                return f"List<{item_type}>"
        elif prop_type in custom_type_mappings:
            return custom_type_mappings[prop_type]

    # Default to Object type if no specific mapping found
    return "Object"


def generate_class_properties(properties, indent=""):
    """
    Generates the Java class properties code block recursively,
    considering nested objects.
    """
    code = ""
    for prop, prop_schema in properties.items():
        prop_type = generate_java_type(prop_schema)
        if prop_type:
            code += f"{indent}private {prop_type} {prop};\n"

        if "properties" in prop_schema:
            nested_props = prop_schema["properties"]
            code += generate_class_properties(nested_props, indent)

    return code


def generate_getters_setters(properties, indent=""):
    """
    Generates the Java getters and setters code block recursively,
    considering nested objects.
    """
    code = ""
    for prop, prop_schema in properties.items():
        prop_type = generate_java_type(prop_schema)
        if prop_type:
            code += f"\n{indent}public {prop_type} get{prop.capitalize()}() {{\n"
            code += f"{indent}    return {prop};\n"
            code += f"{indent}}}\n"

            code += f"\n{indent}public void set{prop.capitalize()}({prop_type} {prop}) {{\n"
            code += f"{indent}    this.{prop} = {prop};\n"
            code += f"{indent}}}\n"

        if "properties" in prop_schema:
            nested_props = prop_schema["properties"]
            code += generate_getters_setters(nested_props, indent)

    return code


# Extract the class name from the title or use a default class name
title = json_schema.get("title", "Newgenpojoclass")
class_name_parts = title.split()
class_name = class_name_parts[0].capitalize()

# Define the Jinja2 template for the Java POJO
template_str = """
public class {{ class_name }} {
    {% set indent = "    " %}

    {{ properties | generate_class_properties(indent) }}

    public {{ class_name }}() {
    }

    public {{ class_name }}(
        {% for prop, prop_schema in properties.items() %}
        {{ prop_schema | generate_java_type }} {{ prop }}{% if not loop.last %}, {% endif %}
        {% endfor %}
    ) {
        super();
        {% for prop, prop_schema in properties.items() %}
        this.{{ prop }} = {{ prop }};
        {% endfor %}
    }

    {{ properties | generate_getters_setters(indent) }}

    @Override
    public String toString() {
        return "{{ class_name }} ("
                {% for prop, prop_schema in properties.items() %}
                + "{{ prop }}=" + {{ prop }} + ", "
                {% endfor %}
                + "]";
    }

    public void validate() throws IllegalArgumentException {
        {% for prop in required_fields %}
        if ({{ prop }} == null || {{ prop }}.isEmpty()) {
            throw new IllegalArgumentException("{{ prop }} must not be null or empty.");
        }
        {% endfor %}
    }
}
"""

# Create a Jinja2 environment and register the custom functions as filters
env = Environment()
env.filters["generate_class_properties"] = generate_class_properties
env.filters["generate_getters_setters"] = generate_getters_setters
env.filters["generate_java_type"] = generate_java_type

# Create a Jinja2 template object
template = env.from_string(template_str)

# Get the list of required fields
required_fields = json_schema.get("required", [])

# Render the template with the data from the JSON schema
rendered_code = template.render(
    class_name=class_name,
    properties=json_schema['properties'],
    required_fields=required_fields
)

# Print the generated Java code
print(rendered_code)














import json


def generate_pojo_class(class_name, properties):
    class_code = f'public class {class_name} {{\n\n'

    for prop_name, prop_details in properties.items():
        prop_type = prop_details['type']

        if prop_type == 'array':
            item_type = prop_details['items']['type']
            item_type = convert_to_java_type(item_type)
            class_code += f'\tprivate List<{item_type}> {prop_name};\n'
        elif prop_type == 'object':
            ref_class = prop_name.capitalize()
            class_code += f'\tprivate {ref_class} {prop_name};\n'
        else:
            prop_type = convert_to_java_type(prop_type)
            class_code += f'\tprivate {prop_type} {prop_name};\n'

    class_code += '\n'

    for prop_name, _ in properties.items():
        prop_name = prop_name[0].upper() + prop_name[1:]
        prop_type = properties[prop_name.lower()]['type']
        prop_type = convert_to_java_type(prop_type)
        class_code += f'\tpublic {prop_type} get{prop_name}() {{\n'
        class_code += f'\t\treturn {prop_name};\n\t}}\n\n'
        class_code += f'\tpublic void set{prop_name}({prop_type} {prop_name}) {{\n'
        class_code += f'\t\tthis.{prop_name} = {prop_name};\n\t}}\n\n'

    class_code += '}'

    return class_code


def convert_to_java_type(prop_type):
    if prop_type == 'string':
        return 'String'
    elif prop_type == 'number':
        return 'double'
    elif prop_type == 'integer':
        return 'int'
    elif prop_type == 'boolean':
        return 'boolean'
    else:
        return 'Object'


def generate_pojo_classes(schema):
    classes = []

    class_name = schema['title']
    class_details = schema['properties']

    if class_name not in classes:
        classes.append(class_name)
        class_code = generate_pojo_class(class_name, class_details)
        classes.append(class_code)

    for prop_name, prop_details in class_details.items():
        if prop_details['type'] == 'object':
            obj_name = prop_name.capitalize()
            if obj_name not in classes:
                classes.append(obj_name)
                obj_code = generate_pojo_class(obj_name, prop_details['properties'])
                classes.append(obj_code)

    return classes


def main():
    json_schema = '''
    {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Company",
        "type": "object",
        "properties": {
            "employee": {
                "title": "Employee",
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                    "email": {"type": "string"}
                },
                "required": ["name", "age"]
            },
            "address": {
                "title": "Address",
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"},
                    "zip": {"type": "string"}
                },
                "required": ["street", "city"]
            }
        }
    }
    '''

    schema = json.loads(json_schema)

    pojo_classes = generate_pojo_classes(schema)

    for pojo_class in pojo_classes:
        print(pojo_class)
        print('\n')
        
        
        
        
        
        
        from jinja2 import Template
import json

# JSON schema as a string
json_schema_str = '''
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Company",
    "type": "object",
    "properties": {
        "employee": {
            "title": "Employee",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "email": {"type": "string"}
            },
            "required": ["name", "age"]
        },
        "address": {
            "title": "Address",
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "city": {"type": "string"},
                "zip": {"type": "string"}
            },
            "required": ["street", "city"]
        }
    }
}
'''

# Parse the JSON schema string into a dictionary
json_schema = json.loads(json_schema_str)

# Define the Jinja2 template for the Java POJO
template_str = """
public class {{ class_name }} {
    {% for obj_name, obj_schema in objects.items() %}
    public class {{ obj_name }} {
        {% for prop, prop_schema in obj_schema.get('properties', {}).items() %}
        private {{ prop_schema.type }} {{ prop }};
        {% endfor %}

        public {{ obj_name }}() {
        }

        public {{ obj_name }}({% for prop, prop_schema in obj_schema.get('properties', {}).items() %}{{ prop_schema.type }} {{ prop }}{% if not loop.last %}, {% endif %}{% endfor %}) {
            super();
            {% for prop, prop_schema in obj_schema.get('properties', {}).items() %}
            this.{{ prop }} = {{ prop }};
            {% endfor %}
        }

        {% for prop, prop_schema in obj_schema.get('properties', {}).items() %}
        public {{ prop_schema.type }} get{{ prop|capitalize }}() {
            return {{ prop }};
        }

        public void set{{ prop|capitalize }}({{ prop_schema.type }} {{ prop }}) {
            this.{{ prop }} = {{ prop }};
        }
        {% endfor %}

        @Override
        public String toString() {
            return "{{ obj_name }} ("
                    {% for prop, prop_schema in obj_schema.get('properties', {}).items() %}
                    + "{{ prop }}=" + {{ prop }} + ", "
                    {% endfor %}
                    + "]";
        }

        public void validate() throws IllegalArgumentException {
            {% for required_field in obj_schema.get('required', []) %}
            if ({{ required_field }} == null || {{ required_field }}.isEmpty()) {
                throw new IllegalArgumentException("{{ required_field }} must not be null or empty.");
            }
            {% endfor %}
        }
    }
    {% endfor %}

    public static void main(String[] args) {
        // Create instances of the objects
        {% for obj_name, obj_schema in objects.items() %}
        {{ obj_name }} {{ obj_name|lower }} = new {{ obj_name }}();
        {% endfor %}

        // Validate the objects
        {% for obj_name, obj_schema in objects.items() %}
        try {
            {{ obj_name|lower }}.validate();
            System.out.println("{{ obj_name }} is valid.");
        } catch (IllegalArgumentException e) {
            System.out.println("{{ obj_name }} is invalid: " + e.getMessage());
        }
        {% endfor %}
    }
}
"""

# Create a Jinja2 template object
template = Template(template_str)

# Extract the main class name from the JSON schema's title
class_name = json_schema.get("title", "NewGenPojoClass")

# Extract the objects and their properties from the JSON schema
objects = {obj_name: obj_schema for obj_name, obj_schema in json_schema.get("properties", {}).items() if obj_schema.get("type") == "object"}

# Render the template with the data from the JSON schema
rendered_code = template.render(class_name=class_name, objects=objects)

# Print the generated Java code
print(rendered_code)






from jinja2 import Template
import json

# JSON schema as a string
json_schema_str = '''
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Company",
    "type": "object",
    "properties": {
        "employee": {
            "title": "Employee",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "email": {"type": "string"}
            },
            "required": ["name", "age"]
        },
        "address": {
            "title": "Address",
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "city": {"type": "string"},
                "zip": {"type": "string"}
            },
            "required": ["street", "city"]
        }
    }
}
'''

# Parse the JSON schema string into a dictionary
json_schema = json.loads(json_schema_str)

# Define the Jinja2 template for the Java POJO
template_str = """
public class {{ class_name }} {
    {% for prop, prop_schema in properties.items() %}
    private {{ prop_schema.type }} {{ prop }};
    {% endfor %}

    public {{ class_name }}() {
    }

    public {{ class_name }}({% for prop, prop_schema in properties.items() %}{{ prop_schema.type }} {{ prop }}{% if not loop.last %}, {% endif %}{% endfor %}) {
        super();
        {% for prop, prop_schema in properties.items() %}
        this.{{ prop }} = {{ prop }};
        {% endfor %}
    }

    {% for prop, prop_schema in properties.items() %}
    public {{ prop_schema.type }} get{{ prop|capitalize }}() {
        return {{ prop }};
    }

    public void set{{ prop|capitalize }}({{ prop_schema.type }} {{ prop }}) {
        this.{{ prop }} = {{ prop }};
    }
    {% endfor %}

    @Override
    public String toString() {
        return "{{ class_name }} ("
                {% for prop, prop_schema in properties.items() %}
                + "{{ prop }}=" + {{ prop }} + ", "
                {% endfor %}
                + "]";
    }

    public void validate() throws IllegalArgumentException {
        {% for prop in required_fields %}
        if ({{ prop }} == null || {{ prop }}.isEmpty()) {
            throw new IllegalArgumentException("{{ prop }} must not be null or empty.");
        }
        {% endfor %}
    }
}
"""

# Create a Jinja2 template object
template = Template(template_str)

# Check if the schema has a top-level "definitions" object
if "definitions" in json_schema:
    # Iterate over each object in the "definitions" object and generate Java code
    for obj_name, obj_schema in json_schema["definitions"].items():
        class_name_parts = obj_schema.get("title", "").split()
        class_name = class_name_parts[0].capitalize()
        required_fields = obj_schema.get("required", [])

        # Render the template with the data from the JSON schema object
        rendered_code = template.render(class_name=class_name, properties=obj_schema.get("properties", {}), required_fields=required_fields)

        # Print the generated Java code for the object
        print(rendered_code)
        print('\n')
else:
    # Generate Java code for the root object in the schema
    class_name_parts = json_schema.get("title", "NewGenPojoClass").split()
    class_name = class_name_parts[0].capitalize()
    required_fields = json_schema.get("required", [])

    # Render the template with the data from the root JSON schema
    rendered_code = template.render(class_name=class_name, properties=json_schema.get("properties", {}), required_fields=required_fields)

    # Print the generated Java code for the root object
    print(rendered_code)
    print('\n')













####################################

from jinja2 import Template

# JSON schema as a dictionary
json_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Employee",
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "email": {"type": "string"}
    },
    "required": ["name", "age"]
}

# Define the Jinja2 template for the Java POJO
template_str = """
public class {{ class_name }} {
    {% for prop, prop_schema in properties.items() %}
    private {{ prop_schema.type }} {{ prop }};
    {% endfor %}

    public {{ class_name }}() {
    }

    public {{ class_name }}({% for prop, prop_schema in properties.items() %}{{ prop_schema.type }} {{ prop }}{% if not loop.last %}, {% endif %}{% endfor %}) {
        super();
        {% for prop, prop_schema in properties.items() %}
        this.{{ prop }} = {{ prop }};
        {% endfor %}
    }

    {% for prop, prop_schema in properties.items() %}
    public {{ prop_schema.type }} get{{ prop|capitalize }}() {
        return {{ prop }};
    }

    public void set{{ prop|capitalize }}({{ prop_schema.type }} {{ prop }}) {
        this.{{ prop }} = {{ prop }};
    }
    {% endfor %}

    @Override
    public String toString() {
        return "{{ class_name }} ("
                {% for prop, prop_schema in properties.items() %}
                + "{{ prop }}=" + {{ prop }} + ", "
                {% endfor %}
                + "]";
    }

    public void validate() throws IllegalArgumentException {
        {% for prop in required_fields %}
        if ({{ prop }} == null || {{ prop }}.isEmpty()) {
            throw new IllegalArgumentException("{{ prop }} must not be null or empty.");
        }
        {% endfor %}
    }
}
"""

# Create a Jinja2 template object
template = Template(template_str)

# Get the list of required fields
required_fields = json_schema.get("required", [])

# Render the template with the data from the JSON schema
rendered_code = template.render(class_name='Employee', properties=json_schema['properties'], required_fields=required_fields)

# Print the generated Java code
print(rendered_code)











import jsonschema2popo
from jinja2 import Template

# JSON schema as a dictionary
json_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Employee",
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "email": {"type": "string"}
    },
    "required": ["name", "age"]
}

# Define the Jinja2 template for the Java POJO
template_str = """
public class {{ class_name }} {
    {% for prop, prop_schema in properties.items() %}
    private {{ prop_schema.type }} {{ prop }};
    {% endfor %}

    public {{ class_name }}() {
    }

    public {{ class_name }}({% for prop, prop_schema in properties.items() %}{{ prop_schema.type }} {{ prop }}{% if not loop.last %}, {% endif %}{% endfor %}) {
        super();
        {% for prop, prop_schema in properties.items() %}
        this.{{ prop }} = {{ prop }};
        {% endfor %}
    }

    {% for prop, prop_schema in properties.items() %}
    public {{ prop_schema.type }} get{{ prop|capitalize }}() {
        return {{ prop }};
    }

    public void set{{ prop|capitalize }}({{ prop_schema.type }} {{ prop }}) {
        this.{{ prop }} = {{ prop }};
    }
    {% endfor %}

    @Override
    public String toString() {
        return "{{ class_name }} ("
                {% for prop, prop_schema in properties.items() %}
                + "{{ prop }}=" + {{ prop }} + ", "
                {% endfor %}
                + "]";
    }
}
"""

# Create a Jinja2 template object
template = Template(template_str)

# Render the template with the data from the JSON schema
rendered_code = template.render(class_name='Employee', properties=json_schema['properties'])

# Print the generated Java code
print(rendered_code)
