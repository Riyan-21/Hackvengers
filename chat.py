import google.generativeai as genai
import json
import sys

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

def process_chat():
    """Process text chat with Gemini"""
    print("Chat system initialized and ready to receive messages...", file=sys.stderr)
    sys.stderr.flush()
    
    while True:
        try:
            # Read input from stdin
            user_input = sys.stdin.readline().strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["exit", "quit", "stop"]:
                print("Chat system shutting down...", file=sys.stderr)
                break
                
            # Generate response from the model
            response = chat_session.send_message(user_input)
            response_text = response.text
            
            # Save conversation
            conversation_entry = f"**You  :** {user_input}\n\n**Gemini:** {response_text}\n\n"
            save_to_markdown(conversation_entry)
            write_conversation_to_json("chat_response.json", user_input, response_text)
            
            # Print response to stdout for the server to read
            print(response_text)
            sys.stdout.flush()
            
        except KeyboardInterrupt:
            print("\nChat system ended by user.", file=sys.stderr)
            break
        except Exception as e:
            print(f"An error occurred: {e}", file=sys.stderr)
            print("Error processing message. Please try again.")
            sys.stdout.flush()
            continue

if __name__ == "__main__":
    try:
        process_chat()
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
    finally:
        print("Cleaning up...", file=sys.stderr)


