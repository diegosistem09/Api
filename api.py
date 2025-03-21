from flask import Flask, request, jsonify, send_file
import os
import speech_recognition as sr
from gtts import gTTS
import joblib
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Habilitar CORS para permitir peticiones de Unity

# Cargar el modelo y el vectorizador para predicciones
with open('modelo_multiclase.pkl', 'rb') as model_file:
    modelo = joblib.load(model_file)

with open('vectorizer.pkl', 'rb') as vectorizer_file:
    vectorizer = joblib.load(vectorizer_file)

# -------------------------- AUDIO A TEXTO -------------------------- #
@app.route('/audio-to-text', methods=['POST'])
def convert_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No se envió ningún archivo de audio"}), 400

    audio_file = request.files['audio']
    file_path = "temp_audio.wav"
    audio_file.save(file_path)  # Guardar el archivo temporalmente

    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language="es-ES")
        except sr.UnknownValueError:
            text = "No se pudo entender el audio"
        except sr.RequestError:
            text = "Error en la solicitud de reconocimiento"

    os.remove(file_path)  # Eliminar el archivo temporal
    return jsonify({"texto": text})

# -------------------------- TEXTO A AUDIO -------------------------- #
@app.route('/text-to-audio', methods=['POST'])
def convert_text_to_audio():
    if not request.is_json:
        return jsonify({"error": "La solicitud debe tener formato JSON"}), 400

    data = request.json
    if 'texto' not in data or not data['texto'].strip():
        return jsonify({"error": "El texto está vacío o no fue enviado"}), 400

    text = data['texto']
    tts = gTTS(text=text, lang='es')
    output_file = "temp_audio.mp3"
    tts.save(output_file)

    return send_file(output_file, as_attachment=True, download_name="audio.mp3")

# -------------------------- PREDICCIÓN DE TEXTO -------------------------- #
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    
    if 'text' not in data or not data['text'].strip():
        return jsonify({"error": "No se proporcionó texto para la predicción"}), 400

    texto = data['text']
    vectorizado = vectorizer.transform([texto])
    prediccion = modelo.predict(vectorizado)

    return jsonify({'prediccion': str(prediccion[0])}), 200, {'Content-Type': 'application/json; charset=utf-8'}

# -------------------------- RUTA DE PRUEBA -------------------------- #
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "API funcionando correctamente"}), 200

# -------------------------- INICIO DEL SERVIDOR -------------------------- #
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4848, debug=True)
