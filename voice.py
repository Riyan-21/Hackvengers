import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import json
import time
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
    with open("voice_response.md", "a") as f:
        f.write(content + "\n\n")

def get_voice_input():
    """Get voice input from the user's microphone"""
    recognizer = sr.Recognizer()
    
    # List available microphones
    try:
        print("Available microphones:")
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"{index}: {name}")
    except Exception as e:
        print(f"Error listing microphones: {e}")
        return None

    try:
        # Try to use the default microphone
        with sr.Microphone() as source:
            print("\nInitializing microphone...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Microphone initialized. Listening...")
            
            # Set timeout and phrase time limit
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("Processing speech...")
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
            
    except sr.WaitTimeoutError:
        print("No speech detected within the timeout period.")
        return None
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand what you said.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None
    except Exception as e:
        print(f"Error accessing microphone: {e}")
        return None

def text_to_speech(text):
    """Convert text to speech"""
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 140)
        voices = engine.getProperty("voices")
        engine.setProperty("voice", voices[1].id)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in text-to-speech: {e}")

def process_voice_chat():
    """Process voice chat with Gemini"""
    print("\nVoice chat initialized. Speak into your microphone.")
    print("Say 'exit', 'quit', or 'stop' to end the conversation.")
    
    while True:
        print("\nListening for your voice input...")
        user_input = get_voice_input()
        
        if user_input is None:
            print("Please try speaking again.")
            continue
            
        if user_input.lower() in ["exit", "quit", "stop"]:
            print("Ending voice chat. Goodbye!")
            break
            
        print("Processing your request...")
        # Generate response from the model
        response = chat_session.send_message(user_input)
        response_text = response.text
        
        # Save conversation
        conversation_entry = f"**You  :** {user_input}\n\n**Gemini:** {response_text}\n\n"
        save_to_markdown(conversation_entry)
        write_conversation_to_json("voice_response.json", user_input, response_text)
        
        print("Speaking response...")
        # Convert response to speech
        text_to_speech(response_text)

if __name__ == "__main__":
    try:
        process_voice_chat()
    except KeyboardInterrupt:
        print("\nVoice chat ended by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Cleaning up...")
        sys.exit(0)


