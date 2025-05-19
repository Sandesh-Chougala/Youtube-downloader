from flask import Flask, request, send_file, jsonify, render_template
import yt_dlp
import os
import uuid

app = Flask(__name__)

# Directory to store downloaded MP3 files
DOWNLOAD_DIR = os.path.abspath('./downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    video_url = data.get('url')

    if not video_url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        # Generate a unique filename
        filename = str(uuid.uuid4()) + '.mp3'
        filepath = os.path.join(DOWNLOAD_DIR, filename)

        # yt_dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'ffmpeg_location': r'C:\ffmpeg\bin\ffmpeg.exe',  # Update if your path differs
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            downloaded_filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'

        # Return file for download
        return send_file(
            downloaded_filename,
            as_attachment=True,
            download_name=os.path.basename(downloaded_filename),
            mimetype='audio/mpeg'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
