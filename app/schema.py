def individual_serial(todo) -> dict: 
    return {
        'id': str(todo['_id']),
        'name': todo['name'],
        'description': todo['description'],
        'isCompleted': todo['isCompleted']
    }
    
def list_serial(todos) -> list:
    return [individual_serial(todo) for todo in todos]

def individual_serial_user(user) -> dict:
    return {
        'email': user['email'],
        'fullName': user['fullName']
    }