# Example Python code with various issues for testing

def calculate_average(numbers):
    total = 0
    for num in numbers:
        total = total + num
    return total / len(numbers)  # Bug: No check for empty list

class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
    
    def send_email(self, message):
        # Security issue: No input validation
        query = f"INSERT INTO messages VALUES ('{self.email}', '{message}')"
        # This is SQL injection vulnerable
        pass

def process_data(data):
    # Missing error handling
    result = data['key']  # KeyError if key doesn't exist
    return result

if __name__ == "__main__":
    nums = [1, 2, 3, 4, 5]
    avg = calculate_average(nums)
    print(f"Average: {avg}")
