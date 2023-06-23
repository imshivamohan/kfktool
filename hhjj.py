import json
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
    # Custom type mappings (JSON type to Java type)
    custom_type_mappings = {
        "integer": "int",
        "number": "double",
        "string": "String",
        "boolean": "boolean",
        # Add more custom type mappings as needed
    }

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

def generate_java_pojos(json_schema_url):
    """
    Generates Java POJOs based on a JSON schema fetched from the provided URL.
    Returns a dictionary of generated Java code snippets where the key is the class name.
    """
    json_schema = fetch_json_schema(json_schema_url)

    pojo_code_snippets = {}

    def generate_class_code(class_name, properties):
        template_str = """
        public class {{ class_name }} {
            {% for prop, prop_schema in properties.items() %}
            private {{ generate_java_type(prop_schema) }} {{ prop }};
            {% endfor %}

            // Getters and Setters
            {% for prop, prop_schema in properties.items() %}
            public {{ generate_java_type(prop_schema) }} get{{ prop|capitalize }}() {
                return {{ prop }};
            }

            public void set{{ prop|capitalize }}({{ generate_java_type(prop_schema) }} {{ prop }}) {
                this.{{ prop }} = {{ prop }};
            }
            {% endfor %}
        }
        """

        env = Environment()
        env.filters["generate_java_type"] = generate_java_type
        template = env.from_string(template_str)
        rendered_code = template.render(class_name=class_name, properties=properties)

        return rendered_code

    def traverse_schema(schema, class_name):
        if "type" in schema and schema["type"] == "object":
            properties = schema.get("properties", {})
            required_fields = schema.get("required", [])
            pojo_code_snippets[class_name] = generate_class_code(class_name, properties)

            for prop, prop_schema in properties.items():
                if "$ref" in prop_schema:
                    ref_class_name = prop_schema["$ref"].split("/")[-1]
                    traverse_schema(prop_schema, ref_class_name)
                elif "type" in prop_schema and prop_schema["type"] == "array":
                    items_schema = prop_schema.get("items", {})
                    if "$ref" in items_schema:
                        ref_class_name = items_schema["$ref"].split("/")[-1]
                        traverse_schema(items_schema, ref_class_name)

    # Traverse the JSON schema and generate Java POJOs
    class_name = json_schema.get("title", "NewGenPOJOClass")
    traverse_schema(json_schema, class_name)

    return pojo_code_snippets

# URL for fetching the JSON schema
json_schema_url = "https://example.com/json-schema"

# Generate Java POJOs based on the JSON schema
pojo_code_snippets = generate_java_pojos(json_schema_url)

# Print the generated Java code snippets
for class_name, code_snippet in pojo_code_snippets.items():
    print(f"Java POJO - {class_name}:")
    print(code_snippet)
    print("---------------------------------")
