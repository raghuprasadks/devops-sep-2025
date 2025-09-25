from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World!"

@app.route('/welcome')
def welcome():
    return "Welcome. I am learning flask"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
#docker build -t flaskapp .
#docker run -d -p 5000:5000 --name flaskapp1 flaskapp
#docker run -d -p 8000:5000 --name flaskapp2 flaskapp