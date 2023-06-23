import json
import re

def generate_java_pojos(json_schema):
    java_code = ''

    # Parse the JSON schema
    schema = json.loads(json_schema)
    title = schema.get('title', 'Unknown')
    properties = schema.get('properties', {})
    required_fields = schema.get('required', [])

    # Generate the Java class definition
    java_code += f"public class {title} {{\n"

    # Generate the private member variables
    for prop, prop_schema in properties.items():
        prop_type = prop_schema.get('type', 'Unknown')
        java_code += f"    private {prop_type} {prop};\n"

    # Generate the default constructor
    java_code += f"\n    public {title}() {{\n    }}\n"

    # Generate the parameterized constructor
    java_code += f"\n    public {title}("
    constructor_args = []
    for prop, prop_schema in properties.items():
        prop_type = prop_schema.get('type', 'Unknown')
        constructor_args.append(f"{prop_type} {prop}")
    java_code += ', '.join(constructor_args)
    java_code += f") {{\n        super();\n"

    # Generate the constructor assignments and validation for required fields
    for prop in properties.keys():
        if prop in required_fields:
            prop_type = properties[prop].get('type', 'Unknown')
            java_code += f"        if ({prop} == null"
            if prop_type == 'string':
                java_code += f" || {prop}.isEmpty()"
            java_code += f") {{\n"
            java_code += f"            throw new IllegalArgumentException(\"'{prop}' cannot be null or empty\");\n"
            java_code += f"        }}\n"
        java_code += f"        this.{prop} = {prop};\n"
    java_code += f"    }}\n"

    # Generate the getter and setter methods
    for prop, prop_schema in properties.items():
        prop_type = prop_schema.get('type', 'Unknown')

        # Getter method
        java_code += f"\n    public {prop_type} get{capitalize_first_letter(prop)}() {{\n"
        java_code += f"        return {prop};\n    }}\n"

        # Setter method
        java_code += f"\n    public void set{capitalize_first_letter(prop)}({prop_type} {prop}) {{\n"
        if prop in required_fields:
            java_code += f"        if ({prop} == null"
            if prop_type == 'string':
                java_code += f" || {prop}.isEmpty()"
            java_code += f") {{\n"
            java_code += f"            throw new IllegalArgumentException(\"'{prop}' cannot be null or empty\");\n"
            java_code += f"        }}\n"
        java_code += f"        this.{prop} = {prop};\n    }}\n"

    # Generate the toString() method
    java_code += f"\n    @Override\n"
    java_code += f"    public String toString() {{\n"
    java_code += f"        return \"{title} (\"\n"
    for prop in properties.keys():
        java_code += f"                + \"{prop}=\" + {prop} + \", \"\n"
    java_code += f"                + \"]\";\n    }}\n"

    java_code += f"}}"

    return java_code

def capitalize_first_letter(string):
    return re.sub(r"(^|_)([a-z])", lambda match: match.group(2).upper(), string)

# Example usage
json_schema = '''
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Employee",
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "age": {
            "type": "integer"
        },
        "email": {
            "type": "string"
        }
    },
    "required": ["name", "age"]
}
'''

generated_code = generate_java_pojos(json_schema)
print(generated_code)
