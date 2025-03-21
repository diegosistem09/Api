from flask import Flask, request, jsonify, send_file
from gtts import gTTS
import os
import speech_recognition as sr


app = Flask(__name__)

# @app.before_first_request
# def log_routes():
#     print("Rutas cargadas:")
#     for rule in app.url_map.iter_rules():
#         print(f"{rule.methods} -> {rule}")


# Ruta para convertir audio en texto
@app.route('/audio-to-text', methods=['POST'])
def convert_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No se envioo ninguun archivo de audio"}), 400

    audio_file = request.files['audio']
    file_path = "temp_audio.wav"
    audio_file.save(file_path)  # Guardar el archivo temporalmente

    # Convertir el audio a texto
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
        try:
            # Usar el reconocimiento de Google (por defecto)
            text = recognizer.recognize_google(audio_data, language="es-ES")
        except sr.UnknownValueError:
            text = "No se pudo entender el audio"
        except sr.RequestError:
            text = "Error en la solicitud de reconocimiento"

    os.remove(file_path)  # Eliminar el archivo temporal
    return jsonify({"texto": text})


# # Ruta para convertir texto en audio
@app.route('/text-to-audio', methods=['POST'])
def convert_text_to_audio():
    # Log de la solicitud recibida
    print("Solicitud recibida:", request.get_json())

    # Validación de la solicitud
    if not request.is_json:
        return jsonify({"error": "La solicitud debe tener formato JSON"}), 400

    data = request.json
    if not data or 'texto' not in data:
        return jsonify({"error": "No se envió ningún texto"}), 400

    text = data['texto']
    if not text.strip():
        return jsonify({"error": "El texto está vacío"}), 400

    # Generar el archivo de audio
    tts = gTTS(text=text, lang='es')
    output_file = "temp_audio.mp3"
    tts.save(output_file)

    # Enviar el archivo como respuesta
    return send_file(output_file, as_attachment=True, download_name="audio.mp3")




# Ruta principal para comprobar el estado del servidor
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "API funcionando correctamente"}), 200

# Corrección para habilitar CORS (Cross-Origin Resource Sharing)
from flask_cors import CORS
CORS(app)

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=4848,debug=True)


#diegosistem09.pythonanywhere.com
#app = Flask(__name__)







# Iniciar la aplicación
if __name__ == '__main__':
    # Corrección para asegurarte de que Flask escuche en todas las interfaces
    app.run(host='0.0.0.0', port=4848,debug=True)
