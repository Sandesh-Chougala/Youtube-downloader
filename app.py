from flask import Flask, render_template, request, redirect, flash, send_file
import yt_dlp
import os

print("Starting Flask app...")


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

DOWNLOAD_DIR = os.path.abspath('./downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_url = request.form.get('url')
        if not video_url:
            flash('Please enter a YouTube URL.', 'danger')
            return redirect('/')

        ydl_opts = {
    'format': 'bestaudio/best',
    'ffmpeg_location': r'C:\ffmpeg\bin',  # 👈 Add this line
    'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
                return send_file(filename, as_attachment=True)
        except Exception as e:
            flash(f"Error: {e}", 'danger')
            return redirect('/')

    return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=True)
