import inspect

def generate_serializer(class_obj):
    class_name = class_obj.__name__

    # Generate the serializer function definition
    serializer_def = f'def serialize_{class_name}(obj, serialization_context):\n'

    # Generate the function body
    serializer_body = '    if hasattr(obj, "to_dict") and callable(obj.to_dict):\n'
    serializer_body += '        return obj.to_dict()\n'
    serializer_body += '    else:\n'
    serializer_body += '        return {}\n'

    # Generate the full serializer function
    serializer_func = serializer_def + serializer_body

    return serializer_func

# Sample class definition
class FoodDeliveryOrder(object):
    orderId = None
    customerName = None
    customerAddress = None
    items = None
    totalPrice = None
    deliveryInstructions = None
    paymentMethod = None

    def __init__(self, orderId, customerName, customerAddress, items, totalPrice, deliveryInstructions, paymentMethod):
        self.orderId = orderId
        self.customerName = customerName
        self.customerAddress = customerAddress
        self.items = items
        self.totalPrice = totalPrice
        self.deliveryInstructions = deliveryInstructions
        self.paymentMethod = paymentMethod

    def to_dict(self):
        return {
            "orderId": self.orderId,
            "customerName": self.customerName,
            "customerAddress": self.customerAddress,
            "items": self.items,
            "totalPrice": self.totalPrice,
            "deliveryInstructions": self.deliveryInstructions,
            "paymentMethod": self.paymentMethod,
        }





"""class Employee(object):
    name = None
    age = None

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def to_dict(self):
        return {
            "name": self.name,
            "age": self.age,
        }
        """
# Generate the serializer function for the Employee class
serializer_func = generate_serializer(FoodDeliveryOrder)

# Execute the generated serializer function dynamically
namespace = {}
exec(serializer_func, namespace)
serializer = namespace[f'serialize_{FoodDeliveryOrder.__name__}']




# Test the serializer function
employee = Employee("John Doe", 30)
serialized_data = serializer(employee, {})
print(serialized_data)
