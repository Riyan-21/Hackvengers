from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import json
import threading
import queue
import subprocess
import os
import sys
import argparse
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Gemini
genai.configure(api_key="AIzaSyDaSi3WwHk3NagJv7ay6ERwEW5SZuKz1Aw")

# Create the model
generation_config = {
    "temperature": 0.5,
    "top_p": 0.5,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction="You are a helpful and friendly wellness assistant."
)

chat_session = model.start_chat(history=[])
chat_queue = queue.Queue()
chat_process = None

def start_chat_process():
    global chat_process
    if chat_process is None or chat_process.poll() is not None:
        try:
            chat_process = subprocess.Popen(
                ['python', 'chat.py'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            # Wait for initialization message
            time.sleep(1)
            # Read and discard the initialization message
            while chat_process.stderr.readable():
                line = chat_process.stderr.readline()
                if "initialized" in line.lower():
                    break
            print("Chat process started successfully", file=sys.stderr)
        except Exception as e:
            print(f"Error starting chat process: {e}", file=sys.stderr)
            chat_process = None

def write_conversation_to_json(filepath, user_input, model_output):
    """Writes a user input and model output to a JSON file."""
    new_data = [
        {"role": "user", "parts": [user_input]},
        {"role": "model", "parts": [model_output]},
    ]

    try:
        with open(filepath, "r+") as f:
            if f.read(1):  # Check if file is not empty
                f.seek(0)
                existing_data = json.load(f)
            else:
                existing_data = []

            existing_data.extend(new_data)
            f.seek(0)
            json.dump(existing_data, f, indent=4)
    except FileNotFoundError:
        with open(filepath, "w") as f:
            json.dump(new_data, f, indent=4)

def save_to_markdown(content):
    with open("chat_response.md", "a") as f:
        f.write(content + "\n\n")

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_input = data.get('message')
        
        if not user_input:
            return jsonify({'error': 'No message provided'}), 400

        # Start chat process if not running
        start_chat_process()
        
        if chat_process is None:
            return jsonify({'error': 'Failed to start chat process'}), 500

        try:
            # Send message to chat.py
            chat_process.stdin.write(user_input + '\n')
            chat_process.stdin.flush()

            # Read response from chat.py
            response_text = chat_process.stdout.readline().strip()
            
            if not response_text:
                # If no response, try reading stderr for error
                error = chat_process.stderr.readline().strip()
                if error:
                    print(f"Chat process error: {error}", file=sys.stderr)
                    return jsonify({'error': 'Error getting response from chat process'}), 500
                else:
                    return jsonify({'error': 'No response from chat process'}), 500

            # Save conversation
            conversation_entry = f"**You  :** {user_input}\n\n**Gemini:** {response_text}\n\n"
            save_to_markdown(conversation_entry)
            write_conversation_to_json("chat_response.json", user_input, response_text)

            return jsonify({'response': response_text})

        except Exception as e:
            print(f"Error communicating with chat process: {e}", file=sys.stderr)
            # Try to restart the chat process
            start_chat_process()
            return jsonify({'error': 'Error communicating with chat process'}), 500

    except Exception as e:
        print(f"Error in chat endpoint: {e}", file=sys.stderr)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start the ZenZone web server')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    args = parser.parse_args()
    
    print(f"Starting server on port {args.port}...")
    app.run(debug=True, port=args.port) 