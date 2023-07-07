import json
import re

class_template = """
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonTypeName;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@ToString
@JsonTypeName("{class_name}")
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

def generate_java_code(schema, class_name, definitions):
    properties = ""

    for property_name, property_info in schema.items():
        # Convert property name to valid Java identifier
        java_property_name = convert_to_valid_identifier(property_name)

        if "$ref" in property_info:
            ref = property_info["$ref"]
            ref_id = ref.split("/")[-1]
            ref_class_name = convert_to_valid_identifier(ref_id.capitalize())
            properties += f"  @JsonProperty(\"{property_name}\")\n"
            properties += f"  private {ref_class_name} {java_property_name};\n\n"
            nested_class_code = generate_java_code(definitions[ref_id]["properties"], ref_class_name, definitions)
            properties += nested_class_code
        elif "oneOf" in property_info:
            oneof_classes = []
            for oneof_property in property_info["oneOf"]:
                ref = oneof_property["$ref"]
                ref_id = ref.split("/")[-1]
                ref_class_name = convert_to_valid_identifier(ref_id.capitalize())
                oneof_class_code = generate_java_code(definitions[ref_id]["properties"], ref_class_name, definitions)
                oneof_classes.append(ref_class_name)
                properties += oneof_class_code
            properties += f"  @JsonProperty(\"{property_name}\")\n"
            properties += f"  private OneOf<{', '.join(oneof_classes)}> {java_property_name};\n\n"
        else:
            property_type = property_info.get("type", "Object")
            required = property_name in schema.get("required", [])
            properties += f"  @JsonProperty(value = \"{property_name}\", required = {str(required).lower()})\n"
            properties += f"  private {property_type} {java_property_name};\n\n"

    return class_template.format(class_name=class_name, properties=properties)


def generate_java_pojos(json_schema):
    schema = json.loads(json_schema)
    definitions = schema.get("definitions", {})
    java_code = generate_java_code(definitions["Header"]["properties"], "Header", definitions)
    java_code += generate_java_code(definitions["Payload"]["properties"], "Payload", definitions)
    for definition_name, definition_properties in definitions.items():
        if definition_name.startswith("ApplicationInitiatedType"):
            java_code += generate_java_code(definition_properties["properties"], definition_name, definitions)
    with open("Header.java", "w") as file:
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
