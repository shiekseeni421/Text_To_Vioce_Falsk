
# sudo apt update
# sudo apt install ffmpeg

from flask import Flask, render_template, request,send_file,jsonify
from gtts import gTTS
import os
import ffmpeg

app = Flask(__name__)
def reduce_audio_size(input_path, target_size_kb=20):
    """Reduce the file size of the audio file using ffmpeg."""
    file_path = '/var/www/html/mediastorage/audio/uplodaudio'
  
    try:
        output_path = os.path.join(file_path, 'compress_output.mp3')
        # Use ffmpeg to compress the audio file
        ffmpeg.input(input_path).output(output_path, ar=22050, ac=1, ab=f'{target_size_kb}k', loglevel='error').run(overwrite_output=True)
        return output_path
    
    except Exception as e:
        print(f"Error reducing audio size: {e}")
        return None
    
# def decompress_audio(input_path):
#     """Decompress the compressed audio file back to its original format."""
#     file_path = '/var/www/html/mediastorage/audio/decompressaudio'
#     try:
#         output_path = os.path.join(file_path, os.path.basename(input_path))

#         # Use ffmpeg to convert the compressed audio file back to original format
#         ffmpeg.input(input_path).output(output_path, loglevel='error').run(overwrite_output=True)
#         return output_path
    
#     except Exception as e:
#         print(f"Error decompressing audio: {e}")
#         return None

# @app.route('/')
# def index():
#     return render_template('index.html')

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    text = request.form['text']
    language = request.form['language']

    # Specify language for gTTS
    ConverTextSpeech = gTTS(text, lang=language, lang_check=True)
    
    # Specify path to storge 
    file_path = '/var/www/html/mediastorage/audio/uplodaudio'
    file_name='output.mp3'
    
    #join the path and file name
    audio_path = os.path.join(file_path, file_name)
    
    # Save the generated speech to a file
    ConverTextSpeech.save(audio_path)
    print(ConverTextSpeech)
    
    # Reduce the file size of the uploaded audio
    reduced_audio_path = reduce_audio_size(audio_path)
    # os.rename(reduced_audio_path,audio_path)
    
    if reduced_audio_path:
        os.remove(audio_path)        
        # return send_file(reduced_audio_path)
        return jsonify({'message': f'File path received: {reduced_audio_path}'}), 200
        
    else:
        return 'File reduction failed', 500
    
    
    
# @app.route('/compress', methods=['POST'])
# def compress():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']

    if file.filename == '':
        return 'No selected file', 400
    
    file_path = '/var/www/html/mediastorage/audio/uplodaudio'
    upload_path = os.path.join(file_path, file.filename)
    file.save(upload_path)
    
    # Reduce the file size of the uploaded audio
    reduced_audio_path = reduce_audio_size(upload_path)
    
    if reduced_audio_path:
        # # Decompress the compressed audio file back to original format
        # decompressed_audio_path = decompress_audio(reduced_audio_path)
        # if decompressed_audio_path:
        #     # Return a download link for the decompressed audio file
        #     return f'<a href="/download/{os.path.basename(decompressed_audio_path)}">Download Decompressed Audio</a>'
        # else:
        #     return 'Audio decompression failed', 500
        # Return a download link for the reduced file
        return f'<a href="/download/{os.path.basename(reduced_audio_path)}">Download Reduced Audio</a>'
    else:
        return 'File reduction failed', 500

 

@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    file_path = '/var/www/html/mediastorage/audio/decompressaudio'
    """Serve a file for download."""
    return send_file(os.path.join(file_path, filename), as_attachment=True)
   

if __name__ == '__main__':
    app.run(debug=True)
