from flask import Flask, render_template, request, jsonify
import os
from my_agent import SearchAgent

app = Flask(__name__)

# Initialize the search agent
agent = SearchAgent()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    message = request.form.get('message', '')
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    # Get response from agent
    response = agent.ask(message)
    
    # Return HTML for the message bubble
    return render_template('_message.html', message=message, response=response)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
