from flask import Flask, render_template, request, jsonify
from llamaapi import LlamaAPI
import speech_recognition as sr
import pyaudio

app = Flask(__name__)

#initializes the OpenAI and LlamaAPI
API_TOKEN = 'LL-6qhAUZklQw8Dzf2WYrPw58wsnNTdSx7BUWKjx1JoAVNqdTI9CwjIR8xGpgDmBeve'
llama = LlamaAPI(API_TOKEN)

#initialize PyAudio
p = pyaudio.PyAudio()

#initialize speech recognizer 
recognizer = sr.Recognizer()

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

@app.route('/record_speech', methods=['POST'])
def record_speech():
    #setting the parameters for recording 
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    fs = 44100

    # Record audio
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []

    # Record for 5 seconds
    for i in range(0, int(fs / chunk * 5)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Convert recorded audio to text
    r = sr.Recognizer()
    audio_data = b''.join(frames)
    try:
        recorded_speech = r.recognize_google(audio_data)
    except sr.UnknownValueError:
        recorded_speech = "Speech Recognition could not understand audio"
    except sr.RequestError as e:
        recorded_speech = "Could not request results from Google Speech Recognition service; {0}".format(e)

    #send recorded speech to LlamaAPI for processing 
    llama_response = llama.run({"messages": [{"role": "user", "content": recorded_speech}]})
    bot_response_llama = llama_response["choices"][0]["messages"]["content"]
    
    return jsonify({'resonse_llama':bot_response_llama})

if __name__== '__main__':
    app.run(debug=True)