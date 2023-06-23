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
