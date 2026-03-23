def calculator():
    print("Simple Calculator")
    print("Available operations: +, -, *, /")
    print("Type 'quit' to exit")
    
    while True:
        try:
            user_input = input("\nEnter expression (e.g., 5 + 3): ").strip()
            
            if user_input.lower() == 'quit':
                print("Goodbye!")
                break
            
            # Split the input into parts
            parts = user_input.split()
            if len(parts) != 3:
                print("Invalid format. Use: number operator number")
                continue
            
            num1, operator, num2 = parts
            
            # Convert to float
            num1 = float(num1)
            num2 = float(num2)
            
            # Perform calculation
            if operator == '+':
                result = num1 + num2
            elif operator == '-':
                result = num1 - num2
            elif operator == '*':
                result = num1 * num2
            elif operator == '/':
                if num2 == 0:
                    print("Error: Division by zero!")
                    continue
                result = num1 / num2
            else:
                print("Invalid operator. Use +, -, *, /")
                continue
            
            # Display result
            if result.is_integer():
                print(f"Result: {int(result)}")
            else:
                print(f"Result: {result}")
                
        except ValueError:
            print("Invalid input. Please enter valid numbers.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    calculator()