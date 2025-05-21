from flask import Flask, request, send_file, jsonify, render_template, after_this_request
import yt_dlp
import os
import tempfile
import shutil

app = Flask(__name__)

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    media_type = data.get('type')  # 'audio' or 'video'

    # Validate input
    if not url or media_type not in ['audio', 'video']:
        return jsonify({'error': 'Invalid input'}), 400

    if "youtube.com" not in url and "youtu.be" not in url:
        return jsonify({'error': 'Only YouTube URLs are supported'}), 400

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set FFmpeg path (update this if needed)
            ffmpeg_path = os.getenv('FFMPEG_PATH', r'C:\ffmpeg\bin\ffmpeg.exe')
            print("Using FFmpeg path:", ffmpeg_path)

            ydl_opts = {
                'format': 'bestaudio/best' if media_type == 'audio' else 'bestvideo+bestaudio/best',
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'quiet': True,
                'socket_timeout': 30,
                'retries': 10,
                'cachedir': False,
                'ffmpeg_location': ffmpeg_path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }] if media_type == 'audio' else [],
            }

            print("⏬ Starting download...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                if media_type == 'audio':
                    file_path = os.path.splitext(file_path)[0] + '.mp3'

            print("✅ Download complete:", file_path)

            temp_ext = ".mp3" if media_type == 'audio' else ".mp4"
            temp_fp = tempfile.NamedTemporaryFile(delete=False, suffix=temp_ext)
            temp_fp.close()
            shutil.copy2(file_path, temp_fp.name)

            @after_this_request
            def remove_file(response):
                try:
                    os.remove(temp_fp.name)
                    print("🧹 Temp file deleted:", temp_fp.name)
                except Exception as e:
                    print("❌ Cleanup failed:", e)
                return response

            return send_file(
                temp_fp.name,
                as_attachment=True,
                download_name=os.path.basename(file_path),
                mimetype='audio/mpeg' if media_type == 'audio' else 'video/mp4'
            )

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
