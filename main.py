from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

@app.route('/metrics')
def metrics():
    return '', 200

@app.route('/')
def hello():
    return 'Hello world!'

if __name__ == '__main__':
    port = int(os.getenv('PORT', '8000'))
    print(f'Starting HTTP server on port {port}')
    try:
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        print(f'Server failed to start: {e}')
        exit(1)
