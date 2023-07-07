import json

def generate_class_definition(class_name, properties):
    class_template = '''
import com.fasterxml.jackson.annotation.JsonProperty;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@ToString
public class {class_name} {{
{properties}
}}
'''
    property_template = '    @JsonProperty(value = "{property_name}"{required_annotation})\n    private {property_type} {property_name};\n\n'
    properties_str = ''
    for property_name, property_info in properties.items():
        required_annotation = ', required = true' if property_info.get('required', False) else ''
        property_type = property_info.get('type')
        if not property_type:
            ref = property_info.get('$ref')
            if ref:
                property_type = ref.split('/')[-1]
        if property_type == 'array':
            items = property_info.get('items')
            ref = items.get('$ref')
            if ref:
                ref_class_name = ref.split('/')[-1]
                property_type = f'List<{ref_class_name}>'
        properties_str += property_template.format(property_name=property_name, required_annotation=required_annotation, property_type=property_type)
    
    return class_template.format(class_name=class_name, properties=properties_str)

def process_required_properties(json_schema):
    definitions = json_schema.get('definitions', {})
    for class_info in definitions.values():
        properties = class_info.get('properties', {})
        required = class_info.get('required', [])
        for prop in required:
            if prop in properties:
                properties[prop]['required'] = True

def generate_java_classes(json_schema):
    classes = {}
    definitions = json_schema.get('definitions', {})
    for class_name, class_info in definitions.items():
        properties = class_info.get('properties', {})
        classes[class_name] = generate_class_definition(class_name, properties)
    
    return classes

# Example usage:
json_schema = {
   "type":"object",
   "properties":{
      "header":{
         "type":"object",
         "properties":{
            "publishername":{
               "type":"string",
               "enum":[
                  "John Doe",
                  "Jane Smith",
                  "Alice Johnson"
               ]
            },
            "eventname":{
               "type":"string",
               "enum":[
                  "Event A",
                  "Event B",
                  "Event C"
               ]
            },
            "timestamp":{
               "type":"string",
               "format":"date-time"
            }
         },
         "required":[
            "publishername",
            "eventname",
            "timestamp"
         ]
      },
      "payload":{
         "type":"object",
         "properties":{
            "applicationinitiated":{
               "oneOf":[
                  {
                     "type":"object",
                     "properties":{
                        "property1":{
                           "type":"string",
                           "enum":[
                              "value1",
                              "value2",
                              "value3"
                           ]
                        },
                        "nestedobj":{
                           "$ref":"#/definitions/NestedObject"
                        },
                        "flag":{
                           "type":"boolean"
                        }
                     }
                  },
                  {
                     "type":"object",
                     "properties":{
                        "property2":{
                           "type":"string",
                           "enum":[
                              "value4",
                              "value5",
                              "value6"
                           ]
                        },
                        "count":{
                           "type":"integer",
                           "minimum":0
                        }
                     },
                     "required":[
                        "count"
                     ]
                  },
                  {
                     "type":"object",
                     "properties":{
                        "property3":{
                           "type":"string",
                           "enum":[
                              "value7",
                              "value8",
                              "value9"
                           ]
                        },
                        "options":{
                           "type":"array",
                           "items":{
                              "type":"string"
                           }
                        }
                     }
                  }
               ]
            }
         }
      }
   },
   "definitions":{
      "Header":{
         "type":"object",
         "properties":{
            "publishername":{
               "type":"string"
            },
            "eventname":{
               "type":"string"
            },
            "timestamp":{
               "type":"string",
               "format":"date-time"
            }
         },
         "required":[
            "publishername",
            "eventname",
            "timestamp"
         ]
      },
      "Payload":{
         "type":"object",
         "properties":{
            "applicationinitiated":{
               "oneOf":[
                  {
                     "$ref":"#/definitions/ApplicationInitiatedType1"
                  },
                  {
                     "$ref":"#/definitions/ApplicationInitiatedType2"
                  },
                  {
                     "$ref":"#/definitions/ApplicationInitiatedType3"
                  }
               ]
            }
         }
      },
      "ApplicationInitiatedType1":{
         "type":"object",
         "properties":{
            "property1":{
               "type":"string",
               "enum":[
                  "value1",
                  "value2",
                  "value3"
               ]
            },
            "nestedobj":{
               "$ref":"#/definitions/NestedObject"
            },
            "flag":{
               "type":"boolean"
            }
         }
      },
      "ApplicationInitiatedType2":{
         "type":"object",
         "properties":{
            "property2":{
               "type":"string",
               "enum":[
                  "value4",
                  "value5",
                  "value6"
               ]
            },
            "count":{
               "type":"integer",
               "minimum":0
            }
         },
         "required":[
            "count"
         ]
      },
      "ApplicationInitiatedType3":{
         "type":"object",
         "properties":{
            "property3":{
               "type":"string",
               "enum":[
                  "value7",
                  "value8",
                  "value9"
               ]
            },
            "options":{
               "type":"array",
               "items":{
                  "type":"string"
               }
            }
         }
      },
      "NestedObject":{
         "type":"object",
         "properties":{
            "nestedproperty":{
               "type":"string"
            },
            "priority":{
               "type":"integer",
               "minimum":1,
               "maximum":10
            }
         }
      }
   }
}

process_required_properties(json_schema)
java_classes = generate_java_classes(json_schema)

# Print the generated classes
for class_name, class_definition in java_classes.items():
    print(class_name + ".java\n")
    print(class_definition)
    print('\n' + '=' * 50 + '\n')
