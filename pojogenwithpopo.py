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