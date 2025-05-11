from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import pahe
import kwik_token
import json
import threading
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Dictionary to track download status
downloads = {}

# Set the working directory
script_directory = os.path.dirname(os.path.realpath(__file__))
DOWNLOAD_FOLDER = os.path.join(script_directory, "Downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Helper function to replace special characters
def replace_special_characters(input_string, replacement="_"):
    special_characters = "!@#$%^&*()_+{}[]|\\:;<>,.?/~` "
    for char in special_characters:
        input_string = input_string.replace(char, replacement)
    return input_string

@app.route('/api/search', methods=['GET'])
def search_anime():
    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    try:
        results = pahe.search_apahe(query)
        formatted_results = []
        
        for anime in results:
            formatted_results.append({
                "title": anime[0],
                "type": anime[1],
                "episodes": anime[2],
                "status": anime[3],
                "year": anime[4],
                "score": anime[5],
                "session_id": anime[6]
            })
        
        return jsonify({"results": formatted_results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/episodes', methods=['GET'])
def get_episodes():
    anime_id = request.args.get('anime_id', '')
    start_ep = request.args.get('start_episode', 1)
    end_ep = request.args.get('end_episode', 1)
    
    if not anime_id:
        return jsonify({"error": "anime_id parameter is required"}), 400
    
    try:
        start_ep = int(start_ep)
        end_ep = int(end_ep)
        episode_ids = pahe.mid_apahe(session_id=anime_id, episode_range=[start_ep, end_ep])
        
        # Get download links for these episodes
        episodes_data = pahe.dl_apahe1(anime_id=anime_id, episode_ids=episode_ids)
        
        # Organize episode data
        episodes = {}
        index = start_ep
        for key, value in episodes_data.items():
            sorted_links = {}
            for link_info in value:
                link, size, lang = link_info
                size = int(size.split('p')[0])
                if lang == '':
                    lang = 'jpn'
                if lang not in sorted_links:
                    sorted_links[lang] = {}
                if size not in sorted_links[lang]:
                    sorted_links[lang][size] = []
                sorted_links[lang][size].append(link)
            episodes[index] = sorted_links
            index += 1
            
        return jsonify({"episodes": episodes})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/download', methods=['POST'])
def download_episode():
    data = request.json
    
    # Required parameters
    anime_id = data.get('anime_id')
    episode_num = data.get('episode_num')
    lang = data.get('lang', 'jpn')
    quality = data.get('quality')
    anime_title = data.get('anime_title')
    
    if not all([anime_id, episode_num, quality, anime_title]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    try:
        # Convert parameters to appropriate types
        episode_num = int(episode_num)
        quality = int(quality)
        
        # Get episode ID
        episode_ids = pahe.mid_apahe(session_id=anime_id, episode_range=[episode_num, episode_num])
        if not episode_ids:
            return jsonify({"error": "Episode not found"}), 404
        
        # Get download link
        episodes_data = pahe.dl_apahe1(anime_id=anime_id, episode_ids=episode_ids)
        
        if not episodes_data or 0 not in episodes_data:
            return jsonify({"error": "Failed to get episode data"}), 500
        
        # Process available qualities and languages
        episode_links = episodes_data[0]
        
        # Check if language is available
        available_langs = []
        for link_info in episode_links:
            _, _, link_lang = link_info
            if link_lang == '':
                link_lang = 'jpn'
            if link_lang not in available_langs:
                available_langs.append(link_lang)
        
        if lang not in available_langs:
            lang = available_langs[0]  # Default to first available language
        
        # Organize links by quality for the selected language
        quality_links = {}
        for link_info in episode_links:
            link, size, link_lang = link_info
            if link_lang == '' and lang == 'jpn':
                link_lang = 'jpn'
            
            if link_lang == lang:
                size_int = int(size.split('p')[0])
                if size_int not in quality_links:
                    quality_links[size_int] = []
                quality_links[size_int].append(link)
        
        # Find closest quality
        available_qualities = list(quality_links.keys())
        available_qualities.sort(reverse=True)
        
        selected_quality = None
        for q in available_qualities:
            if q <= quality:
                selected_quality = q
                break
        
        if selected_quality is None and available_qualities:
            selected_quality = available_qualities[0]
        
        if not selected_quality:
            return jsonify({"error": "No suitable quality found"}), 500
        
        # Get the redirect link
        redirect_link = pahe.dl_apahe2(quality_links[selected_quality][0])
        
        # Get the final download link
        download_link = kwik_token.get_dl_link(redirect_link)
        
        # Create download directory
        title = replace_special_characters(anime_title)
        download_dir = os.path.join(DOWNLOAD_FOLDER, title)
        os.makedirs(download_dir, exist_ok=True)
        
        # Set download destination
        destination = os.path.join(download_dir, f"{episode_num}_{lang}_{selected_quality}p.mp4")
        
        # Generate a unique download ID
        download_id = f"{title}_{episode_num}_{int(time.time())}"
        
        # Start download in a separate thread
        downloads[download_id] = {
            "status": "queued",
            "progress": 0,
            "file_path": destination,
            "anime_title": title,
            "episode": episode_num,
            "quality": selected_quality
        }
        
        # Start download thread
        thread = threading.Thread(
            target=download_file_thread,
            args=(download_link, destination, download_id)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "message": "Download started",
            "download_id": download_id,
            "file_name": os.path.basename(destination),
            "quality": selected_quality,
            "language": lang
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def download_file_thread(url, destination, download_id):
    try:
        downloads[download_id]["status"] = "downloading"
        
        # Custom progress tracking class
        class ProgressTracker:
            def __init__(self, download_id):
                self.download_id = download_id
                self.total = 0
                
            def update(self, value):
                if self.total > 0:
                    progress = min(int((value / self.total) * 100), 100)
                    downloads[self.download_id]["progress"] = progress
        
        tracker = ProgressTracker(download_id)
        
        # Check if file exists already for resuming
        if os.path.exists(destination):
            file_size = os.path.getsize(destination)
        else:
            file_size = 0

        headers = {'Range': f'bytes={file_size}-'} if file_size else None
        response = requests.get(url, headers=headers, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        tracker.total = total_size + file_size
        
        with open(destination, 'ab') as file:
            for data in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                if data:
                    file.write(data)
                    tracker.update(file.tell())
        
        downloads[download_id]["status"] = "completed"
        
    except Exception as e:
        downloads[download_id]["status"] = "failed"
        downloads[download_id]["error"] = str(e)

@app.route('/api/download/status/<download_id>', methods=['GET'])
def get_download_status(download_id):
    if download_id not in downloads:
        return jsonify({"error": "Download ID not found"}), 404
    
    return jsonify(downloads[download_id])

@app.route('/api/download/list', methods=['GET'])
def list_downloads():
    return jsonify({"downloads": downloads})

@app.route('/api/download/file/<download_id>', methods=['GET'])
def download_file(download_id):
    if download_id not in downloads:
        return jsonify({"error": "Download ID not found"}), 404
    
    download_info = downloads[download_id]
    if download_info["status"] != "completed":
        return jsonify({"error": "Download not completed yet"}), 400
    
    file_path = download_info["file_path"]
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    
    try:
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Make sure the download folder exists
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
