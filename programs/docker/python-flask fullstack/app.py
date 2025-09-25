from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
import time
import sys
import mysql.connector

app = Flask(__name__)

# Database connection with a retry loop
db = None
retries = 20
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

# Route for GET requests to serve the HTML page with data from the database
@app.route('/', methods=['GET'])
def get_items_html():
    cursor.execute("SELECT * FROM items")
    result = cursor.fetchall()
    items_list = [{"id": item[0], "content": item[1]} for item in result]
    return render_template('index.html', items=items_list)

# Route for POST requests to add a new item from the form
@app.route('/items', methods=['POST'])
def add_item():
    content = request.form.get('content')
    if not content:
        return "Content not provided", 400
    
    sql = "INSERT INTO items (content) VALUES (%s)"
    cursor.execute(sql, (content,))
    db.commit()
    return redirect(url_for('get_items_html'))

# Route for deleting an item
@app.route('/items/<int:item_id>/delete', methods=['POST'])
def delete_item(item_id):
    sql = "DELETE FROM items WHERE id = %s"
    cursor.execute(sql, (item_id,))
    db.commit()
    return redirect(url_for('get_items_html'))

# Route for handling updates (a new page with a pre-filled form)
@app.route('/items/<int:item_id>/update', methods=['GET'])
def update_item_form(item_id):
    sql = "SELECT * FROM items WHERE id = %s"
    cursor.execute(sql, (item_id,))
    item = cursor.fetchone()
    if item:
        return render_template('update.html', item={"id": item[0], "content": item[1]})
    return "Item not found", 404

# Route for handling the POST request to update the item in the database
@app.route('/items/<int:item_id>/update', methods=['POST'])
def update_item(item_id):
    content = request.form.get('content')
    if not content:
        return "Content not provided", 400
    
    sql = "UPDATE items SET content = %s WHERE id = %s"
    cursor.execute(sql, (content, item_id))
    db.commit()
    return redirect(url_for('get_items_html'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)