from flask import Flask, render_template, request, jsonify
import openai
from llamaapi import LlamaAPI
import speech_recognition as sr
import pyaudio

app = Flask(__name__)

#initializes the OpenAI and LlamaAPI
API_TOKEN = 'LL-6qhAUZklQw8Dzf2WYrPw58wsnNTdSx7BUWKjx1JoAVNqdTI9CwjIR8xGpgDmBeve'
llama = LlamaAPI(API_TOKEN)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.form.get('user_message')
   
    #handles the llamaAPI request
    llama_response = llama.run({"messages": [{"role": "user", "content": user_message}]})

    #processes the response 
    bot_response_llama = llama_response["choices"][0]["message"]["content"]

    return jsonify({'response_llama': bot_response_llama})

@app.route('/record_speech', methods=['POST'])
def record_speech():
    recorded_speech = request.json.get('speech', '')
    # Handle the recorded speech on the server side
    # You may need to use Flask's request object to get the recorded speech
    # Perform speech recognition and interact with the chatbot
    # Return the bot's response to the client
    return jsonify({'resonse': 'Bot response for recorded speech'})

if __name__== '__main__':
    app.run(debug=True)