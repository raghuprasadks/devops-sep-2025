from flask import Flask, request, jsonify
import os
import time
import sys
import mysql.connector

app = Flask(__name__)

# Wait for the database to be ready
db = None
retries = 5
while not db and retries > 0:
    try:
        db = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DB')
        )
        print("Database connection successful!")
    except mysql.connector.errors.DatabaseError as e:
        print(f"Database is unavailable. Retrying in 5 seconds... ({retries} attempts left)")
        print(f"Error: {e}")
        retries -= 1
        time.sleep(5)

if not db:
    print("Failed to connect to the database after multiple retries. Exiting.")
    sys.exit(1)

cursor = db.cursor()

# Create the 'items' table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content VARCHAR(255) NOT NULL
)
""")
db.commit()

# All your API routes go here...

@app.route('/items', methods=['GET'])
def get_items():
    cursor.execute("SELECT * FROM items")
    result = cursor.fetchall()
    items = [{"id": item[0], "content": item[1]} for item in result]
    return jsonify(items)

@app.route('/items', methods=['POST'])
def add_item():
    content = request.json.get('content')
    if not content:
        return jsonify({"error": "Content not provided"}), 400
    
    sql = "INSERT INTO items (content) VALUES (%s)"
    cursor.execute(sql, (content,))
    db.commit()
    return jsonify({"message": "Item added successfully", "id": cursor.lastrowid}), 201

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    sql = "SELECT * FROM items WHERE id = %s"
    cursor.execute(sql, (item_id,))
    item = cursor.fetchone()
    if item:
        return jsonify({"id": item[0], "content": item[1]})
    return jsonify({"error": "Item not found"}), 404

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    content = request.json.get('content')
    if not content:
        return jsonify({"error": "Content not provided"}), 400
    
    sql = "UPDATE items SET content = %s WHERE id = %s"
    cursor.execute(sql, (content, item_id))
    db.commit()
    if cursor.rowcount > 0:
        return jsonify({"message": "Item updated successfully"})
    return jsonify({"error": "Item not found"}), 404

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    sql = "DELETE FROM items WHERE id = %s"
    cursor.execute(sql, (item_id,))
    db.commit()
    if cursor.rowcount > 0:
        return jsonify({"message": "Item deleted successfully"})
    return jsonify({"error": "Item not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)