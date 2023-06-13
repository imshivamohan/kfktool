import json
import base64
from cryptography.fernet import Fernet

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

# JSON data
json_data = {
    "name": "Modi",
    "age": 66,
    "salary": 50000,
    "total_income": 100000
}

# JSON schema
json_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "salary": {"type": "integer", "encryption": True},
        "total_income": {"type": "integer", "encryption": True}
    },
    "required": ["name", "age", "salary", "total_income"]
}

# Encrypt the sensitive fields based on schema
encrypted_json = json_data.copy()

for field, value in json_data.items():
    if json_schema["properties"].get(field, {}).get("encryption"):
        encrypted_json[field] = encrypt_field(value)

# Serialize the encrypted JSON
serialized_json = json.dumps(encrypted_json)

# Store the encrypted JSON in a file
with open("encrypted_data.json", "w") as file:
    file.write(serialized_json)

# Retrieve the encrypted JSON from the file
with open("encrypted_data.json", "r") as file:
    retrieved_json = file.read()

# Deserialize the retrieved JSON string
deserialized_json = json.loads(retrieved_json)

# Decrypt the sensitive fields based on schema
decrypted_json = deserialized_json.copy()

for field, value in deserialized_json.items():
    if json_schema["properties"].get(field, {}).get("encryption"):
        decrypted_json[field] = decrypt_field(value)

# Print the original JSON
print("Original JSON:")
print(json_data)

# Print the encrypted JSON
print("\nEncrypted JSON:")
print(retrieved_json)

# Print the decrypted JSON
print("\nDecrypted JSON:")
print(decrypted_json)
