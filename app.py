from flask import Flask, render_template, request, jsonify
from llamaapi import LlamaAPI
from gtts import gTTS
import speech_recognition as sr
import pyaudio
import os

app = Flask(__name__, static_url_path='/static')

#initializes the OpenAI and LlamaAPI
API_TOKEN = 'LL-6qhAUZklQw8Dzf2WYrPw58wsnNTdSx7BUWKjx1JoAVNqdTI9CwjIR8xGpgDmBeve'
llama = LlamaAPI(API_TOKEN)

#initialize PyAudio
p = pyaudio.PyAudio()

#initialize speech recognizer 
recognizer = sr.Recognizer()

#defines the microphone instance
mic = sr.Microphone()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.form.get('user_message')
    selected_language = request.form.get('language')
   
    #handles the llamaAPI request with included language
    llama_response = llama.run({"messages": [{"role": "user", "content": user_message}], "language": selected_language})

    try:
        # Attempt to access the response data
        bot_response_llama = llama_response.json()["choices"][0]["message"]["content"]
        return jsonify({'response_llama': bot_response_llama})
    except Exception as e:
        # If accessing the response data fails, print the error and return an error response
        print("Error accessing llama_response:", e)
        return jsonify({'error': 'Failed to process the response from LlamaAPI'}), 500

@app.route('/record_and_process', methods=['POST'])
def record_and_process():
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            audio_data = recognizer.listen(source, timeout=5)

        user_message = recognizer.recognize_google(audio_data)

        # Process the user's message with LlamaAPI
        llama_response = llama.run({"messages": [{"role": "user", "content": user_message}]})
        bot_response_text = extract_response(llama_response)
        bot_response_voice = text_to_speech(bot_response_text)

        return jsonify({'user_message': user_message, 'bot_response_text': bot_response_text, 'bot_response_voice': bot_response_voice})

    except sr.UnknownValueError:
        return jsonify({'error': 'Speech Recognition unable to understand prompt. Please try again.'}), 400
    except sr.RequestError as e:
        return jsonify({'error': f'Error connecting to speech recognition API. Wifi Problem?: {e}'}), 500

# Helper function to extract the bot's response from the LlamaAPI response
def extract_response(llama_response):
    try:
        # Check if 'message' is directly accessible
        if 'message' in llama_response and 'content' in llama_response['message']:
            return llama_response['message']['content']
        elif 'choices' in llama_response and isinstance(llama_response['choices'], list):
            # If there are choices, check the first one for 'message' and 'content'
            first_choice = llama_response['choices'][0]
            if 'message' in first_choice and 'content' in first_choice['message']:
                return first_choice['message']['content']
    except (KeyError, TypeError):
        pass  # Ignore errors and return None if extraction fails
    return "Error extracting response from LlamaAPI"

# Helper function to convert text to speech using gTTS
def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='en')
        tts.save("response.mp3")
        os.system("start response.mp3")  # This command opens the file with the default system audio player
        return "Speech synthesized successfully"
    except Exception as e:
        print("Error in text_to_speech:", e)
        return "Error synthesizing speech"

if __name__== '__main__':
    app.run(debug=True)