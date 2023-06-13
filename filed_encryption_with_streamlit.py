import json
import base64
from cryptography.fernet import Fernet
import streamlit as st

# Generate a local encryption key
encryption_key = Fernet.generate_key()
cipher_suite = Fernet(encryption_key)

def encrypt_field(plaintext):
    plaintext_bytes = bytes(json.dumps(plaintext), encoding="utf-8")
    encrypted_bytes = cipher_suite.encrypt(plaintext_bytes)
    return base64.b64encode(encrypted_bytes).decode("utf-8")

def decrypt_field(ciphertext):
    encrypted_bytes = base64.b64decode(ciphertext)
    decrypted_bytes = cipher_suite.decrypt(encrypted_bytes)
    decrypted_plaintext = decrypted_bytes.decode("utf-8")
    return json.loads(decrypted_plaintext)

# Streamlit app
st.title("JSON Data Encryption")

# Create a two-column layout
col1, col2 = st.columns(2)

# Input fields in the first column
with col1:
    json_schema_input = st.text_area("JSON Schema")

# Input fields in the second column
with col2:
    json_data_input = st.text_area("JSON Data")
# Submit button
if st.button("Submit"):
    try:
        # Parse JSON schema
        schema = json.loads(json_schema_input)

        # Parse JSON data
        data = json.loads(json_data_input)

        # Encrypt sensitive fields based on schema
        for field, field_schema in schema.get("properties", {}).items():
            if field_schema.get("encryption"):
                encrypted_value = encrypt_field(data.get(field))
                data[field] = encrypted_value

        # Print the encrypted JSON
        st.subheader("Encrypted JSON:")
        st.json(data)

        # Decrypt sensitive fields based on schema
        for field, field_schema in schema.get("properties", {}).items():
            if field_schema.get("encryption"):
                decrypted_value = decrypt_field(data.get(field))
                data[field] = decrypted_value

        # Print the decrypted JSON
        st.subheader("Decrypted JSON:")
        st.json(data)
    except json.JSONDecodeError as e:
        st.error("Invalid JSON input. Please provide valid JSON schema and data.")
