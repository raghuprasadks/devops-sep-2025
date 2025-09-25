from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory data store for demonstration
items = {1: "item1", 2: "item2"}
next_id = 3

@app.route('/items', methods=['GET'])
def get_items():
    return jsonify(items)

@app.route('/items', methods=['POST'])
def add_item():
    global next_id
    content = request.json.get('content')
    if content:
        items[next_id] = content
        next_id += 1
        return jsonify({"message": "Item added successfully", "id": next_id - 1}), 201
    return jsonify({"error": "Content not provided"}), 400

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = items.get(item_id)
    if item:
        return jsonify({item_id: item})
    return jsonify({"error": "Item not found"}), 404

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    content = request.json.get('content')
    if item_id in items and content:
        items[item_id] = content
        return jsonify({"message": "Item updated successfully"})
    return jsonify({"error": "Item not found or content not provided"}), 404

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    if item_id in items:
        del items[item_id]
        return jsonify({"message": "Item deleted successfully"})
    return jsonify({"error": "Item not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)