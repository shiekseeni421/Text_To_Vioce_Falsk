## Packages installed
# pip3 install -U pip
# pip install flask
# pip install flask-cors
# pip install gTTS

import logging
import os
import ffmpeg
from gtts import gTTS, gTTSError
from gtts.lang import tts_langs
from flask import Flask, request, jsonify
from flask_cors import CORS



logging.basicConfig(filename="services_info.log", level=logging.INFO)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route('/generate-speech', methods=['POST'])
def generate_speech():
    logging.info("------------------------------------------- AUDIO ------------------------------------------------------------")

    # Requesting values from the POSTed form data
    pageId = request.form.get("pid", "")
    logging.info("pageId --> %s", pageId)

    # Default to English if lang not provided
    lang = request.form.get("lang", "en")
    logging.info("lang --> %s", lang)

    text = request.form.get("text", "")
    # logging.info("text --> %s", text)
    logging.info("text.len --> %d", len(text))

    # Concatenate pageId and lang for a unique file_name
    file_name = f"speech_{pageId}_{lang}.mp3"
    logging.info("file_name --> %s", file_name)

    # Creating file_path for saving audio files
    file_path = f"/var/www/html/mediastorage/audio/{file_name}"
    logging.info("file_path --> ", file_path)
    
    compress_file_name=f"audio_{pageId}_{lang}.mp3"
    compress_file_path=f"/var/www/html/mediastorage/audio/{compress_file_name}"
    logging.info("compress_file_path --> ", compress_file_path)
    
    

    try:
        logging.info("INSIDE TRY BLOCK OF GENERATE_SPEECH FUNCTION")

        # Checking if file already exists or not
        if os.path.exists(compress_file_path):
            logging.info(
                "FILE ALREADY EXISTS. Sending file_path --> %s", compress_file_path)
            return jsonify({"speechUrl": compress_file_path})
        else:
            logging.info(
                "FILE DOES NOT EXIST. Generating new file_path --> %s", file_path)

            # Grant full permissions to the audio directory
            logging.info("Allowing 'audio' directory permissions...")
            os.chmod("/var/www/html/mediastorage/audio/", 0o777)
            logging.info("DIRECTORY PERMISSIONS ALLOWED SUCCESSFULLY")

            # Gnerating speech using gTTS
            logging.info("Generating speech using gTTS...")
            speech = gTTS(text=text, lang=lang, slow=False, lang_check=True)
            logging.info("speech  --> %s", speech)

            if speech:  # Check if speech is not None
                speech.save(file_path)
                logging.info(
                    "AUDIO SAVED SUCCESSFULLY AT PATH ---> %s", file_path)

                # Grant full permissions to the file
                logging.info("Allowing file permissions...")
                os.chmod(file_path, 0o777)
                logging.info("FILE PERMISSIONS ALLOWED SUCCESSFULLY")
                
                logging.info("Compression OF Audio Will start ..... ")
                reduced_audio_path = reduce_audio_size(file_path,compress_file_path)
                
                if reduced_audio_path:
                    os.remove(file_path)
                    logging.info("compression sucess hence, Original File is Deleted")
                    return jsonify({'speechUrl':  reduced_audio_path}), 200
                else:
                    logging.info("Compression Failure, so return original file")
                    return jsonify({'speechUrl':  file_path}), 200
            else:
                # Handle the case where gTTS did not generate audio
                logging.error("gTTS Error speech NOT Generated")
                return jsonify({"error": "Oops! No audio generated at this moment."}), 500

    except gTTSError as e:
        logging.info("INSIDE EXCEPT BLOCK OF (gTTSError) FUNCTION")
        logging.info(
            "file_name in Exception Block (gTTSError) --> %s", file_name)
        logging.info(
            "file_path in Exception Block (gTTSError) --> %s", file_path)
        logging.error('gTTS Error --> %s', e)
        logging.exception("An error occurred in (gTTSError) FUNCTION")

        # Delete the audio file if it was created
        if os.path.exists(file_path):
            logging.info(
                "removing the existing file if (gTTSError) Exception Occurred --> %s", file_path)
            # os.remove(file_path)

        return jsonify({"error": "Failed to generate audio at the moment."}), 500

    except Exception as e:
        logging.info("INSIDE EXCEPT BLOCK OF GENERATE_SPEECH FUNCTION")
        logging.info("file_name in Exception Block --> %s", file_name)
        logging.info("file_path in Exception Block --> %s", file_path)
        logging.error("Exception Block ---> %s", e)

        # Delete the audio file if it was created
        if os.path.exists(file_path):
            logging.info(
                "removing the existing file if Exception Occurred --> %s", file_path)
            os.remove(file_path)

        return jsonify({"error": "Oops! No audio generated at this moment. Please try again!."}), 500

def reduce_audio_size(input_path,compress_file_path,target_size_kb=20,):
    logging.info("--------------------COMPRESS FUNCTION----------------")
    logging.info("input path iss ->%s",input_path)
    logging.info("compress_file_path iss ->%s",compress_file_path)
    # logging.info("Allow compress file path permissins")
    # os.chmod(compress_file_path, 0o777)
    # logging.info("permissins sucess for compress path")
    
    
   
    try:
        # Use ffmpeg to compress the audio file
        ffmpeg.input(input_path).output(compress_file_path, ar=22050, ac=1, ab=f'{target_size_kb}k', loglevel='error').run(overwrite_output=True)
        os.chmod(compress_file_path, 0o777)
        return compress_file_path

    except Exception as e:
        print(f"Error reducing audio size: {e}")
        return None
      
@app.route("/delete_file", methods=["POST"])
def delete_file():
    logging.info(
        "-------------------------------------- DELETE AUDIO ------------------------------------------------------------"
    )

    file_name = request.data.decode("utf-8")
    logging.info("file_name to delete --> %s", file_name)

    # locating file_path where audio files were saved
    file_path = f"/var/www/html/mediastorage/audio/{file_name}"
    logging.info("file_path to delete --> %s", file_path)

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            logging.info("File deleted successfully")
            return jsonify({"status": "File deleted successfully"}), 200
        except Exception as e:
            logging.error("Error deleting file --> %s", e)
            logging.exception("An error occurred in delete_file function")
            return jsonify({"error": "Error deleting audio file"}), 500
    else:
        logging.info("File does not exist")
        return jsonify({"status": "File does not exist"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)