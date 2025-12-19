from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# This allows all origins, which is necessary for a NodePort setup
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided", "status": "error"}), 400
        
        # Get the numbers and operation
        num1 = float(data.get('num1', 0))
        num2 = float(data.get('num2', 0))
        operation = data.get('operation', '')
        
        # Perform the calculation based on operation
        if operation == 'add':
            result = num1 + num2
            operation_text = f"{num1} + {num2}"
        elif operation == 'subtract':
            result = num1 - num2
            operation_text = f"{num1} - {num2}"
        elif operation == 'multiply':
            result = num1 * num2
            operation_text = f"{num1} × {num2}"
        elif operation == 'divide':
            if num2 == 0:
                return jsonify({
                    "error": "Cannot divide by zero", 
                    "status": "error"
                }), 400
            result = num1 / num2
            operation_text = f"{num1} ÷ {num2}"
        else:
            return jsonify({
                "error": "Invalid operation. Use: add, subtract, multiply, or divide", 
                "status": "error"
            }), 400
        
        return jsonify({
            "result": result, 
            "status": "success",
            "message": f"{operation_text} = {result}"
        }), 200
    except ValueError:
        return jsonify({"error": "Invalid number format", "status": "error"}), 400
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 400

# Keep the old /add endpoint for backward compatibility
@app.route('/add', methods=['POST'])
def add():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided", "status": "error"}), 400
        
        num1 = float(data.get('num1', 0))
        num2 = float(data.get('num2', 0))
        result = num1 + num2
        
        return jsonify({
            "result": result, 
            "status": "success",
            "message": f"Added {num1} and {num2}"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 400

if __name__ == '__main__':
    # host 0.0.0.0 is required for Kubernetes to route traffic to the container
    app.run(host='0.0.0.0', port=5000, debug=False)