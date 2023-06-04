import json
import streamlit as st
from jsonschema import validate, exceptions

def validate_json_data(json_data, json_schema):
    try:
        # Load the JSON data and validate against the schema
        data = json.loads(json_data)
        validate(instance=data, schema=json_schema)
        st.success("JSON data is valid against the schema.")
    except exceptions.ValidationError as e:
        st.error("JSON data is not valid against the schema.")
        st.error(e)

# Streamlit app
def main():
    # Title and description
    st.title("JSON Data Validation")
    st.write("Enter JSON data and JSON schema to validate.")

    # JSON data input
    json_data = st.text_area("Enter JSON Data")

    # JSON schema input
    json_schema = st.text_area("Enter JSON Schema")

    # Validate button
    if st.button("Validate"):
        try:
            # Parse JSON schema
            schema = json.loads(json_schema)
            validate_json_data(json_data, schema)
        except json.JSONDecodeError:
            st.error("Invalid JSON schema.")

if __name__ == "__main__":
    main()
