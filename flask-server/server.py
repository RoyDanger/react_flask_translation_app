from flask import Flask, request, jsonify, send_file
import openai
from flask_uploads import UploadSet, configure_uploads, DATA
import os
import json

app = Flask(__name__)

# Configure Flask-Uploads
uploads = UploadSet("uploads", DATA, default_dest=lambda app: 'uploads')

# Set allowed file extensions directly on the UploadSet
uploads.allowed_extensions = {'xlsx', 'pptx'}

# Configure uploads without specifying ALLOWED_EXTENSIONS separately
configure_uploads(app, uploads)

# Load configuration from config.json
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path) as config_file:
    config = json.load(config_file)

# Set your OpenAI API key
openai.api_key = 'your_openai_api_key'  # Replace with your actual API key

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        filename = uploads.save(file)
        file_path = f"uploads/{filename}"

        content = ""
        with open(file_path, 'r', encoding='utf-8') as file_content:
            content = file_content.read()

        target_language = request.form.get('target_language', 'fr')

        try:
            translation = openai.Completion.create(
                engine="text-davinci-002",
                prompt=content,
                max_tokens=150,
                temperature=0.7,
                stop=None,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            )

            translated_content = translation['choices'][0]['text']
        except Exception as e:
            return jsonify({'error': f'Error translating with OpenAI API: {str(e)}'})

        translated_filename = f"translated_{filename}"
        translated_file_path = f"uploads/{translated_filename}"

        with open(translated_file_path, 'w', encoding='utf-8') as translated_file:
            translated_file.write(translated_content)

        return jsonify({
            'message': 'File uploaded and translated successfully',
            'filename': translated_filename,
            'translated_content': translated_content
        })

@app.route('/download/<filename>')
def download_file(filename):
    translated_file_path = f"uploads/{filename}"
    return send_file(translated_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
