from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pahe
import kwik_token

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "online",
        "message": "AnimePaheDownloader API is running",
        "endpoints": [
            "/api/search?query=<search_term>",
            "/api/episodes?anime_id=<anime_id>&start_episode=<start>&end_episode=<end>",
            "/api/download (POST)"
        ]
    })

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
        
        # Limit the range to avoid timeouts in serverless environment
        if end_ep - start_ep > 10:
            end_ep = start_ep + 10
            
        episode_ids = pahe.mid_apahe(session_id=anime_id, episode_range=[start_ep, end_ep])
        
        if not episode_ids:
            return jsonify({"error": "Failed to fetch episode IDs or no episodes found"}), 404
            
        # Get download links for these episodes
        episodes_data = pahe.dl_apahe1(anime_id=anime_id, episode_ids=episode_ids)
        
        # Organize episode data
        episodes = {}
        index = start_ep
        for key, value in episodes_data.items():
            sorted_links = {}
            for link_info in value:
                if len(link_info) >= 2:  # Make sure we have at least link and size
                    link, size = link_info[0], link_info[1]
                    lang = link_info[2] if len(link_info) > 2 else ''
                    
                    if size and "p" in size:
                        size = int(size.split('p')[0])
                    else:
                        continue  # Skip if size format is unexpected
                        
                    if lang == '':
                        lang = 'jpn'
                    if lang not in sorted_links:
                        sorted_links[lang] = {}
                    if size not in sorted_links[lang]:
                        sorted_links[lang][size] = []
                    sorted_links[lang][size].append(link)
            
            if sorted_links:  # Only add if we found links
                episodes[index] = sorted_links
            index += 1
            
        return jsonify({"episodes": episodes})
    except Exception as e:
        import traceback
        traceback.print_exc()
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
        
        if not episodes_data or 0 not in episodes_data or not episodes_data[0]:
            return jsonify({"error": "Failed to get episode data"}), 500
        
        # Process available qualities and languages
        episode_links = episodes_data[0]
        
        # Check if language is available
        available_langs = []
        for link_info in episode_links:
            if len(link_info) > 2:
                _, _, link_lang = link_info
                if link_lang == '':
                    link_lang = 'jpn'
                if link_lang not in available_langs:
                    available_langs.append(link_lang)
        
        if not available_langs:
            available_langs = ['jpn']  # Default if no languages found
            
        if lang not in available_langs:
            lang = available_langs[0]  # Default to first available language
        
        # Organize links by quality for the selected language
        quality_links = {}
        for link_info in episode_links:
            if len(link_info) > 2:
                link, size, link_lang = link_info
                if link_lang == '' and lang == 'jpn':
                    link_lang = 'jpn'
                
                if link_lang == lang and 'p' in size:
                    size_int = int(size.split('p')[0])
                    if size_int not in quality_links:
                        quality_links[size_int] = []
                    quality_links[size_int].append(link)
        
        # Find closest quality
        available_qualities = list(quality_links.keys())
        if not available_qualities:
            return jsonify({"error": f"No qualities available for language {lang}"}), 500
            
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
        if not redirect_link:
            return jsonify({"error": "Failed to get redirect link"}), 500
            
        # Get the final download link
        try:
            download_link = kwik_token.get_dl_link(redirect_link)
            if not download_link:
                return jsonify({"error": "Failed to get download link"}), 500
        except Exception as e:
            return jsonify({"error": f"Error extracting download link: {str(e)}"}), 500
        
        # For serverless environment, return the direct download link
        return jsonify({
            "message": "Download link generated",
            "download_link": download_link,
            "quality": selected_quality,
            "language": lang,
            "episode": episode_num,
            "anime_title": anime_title
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Serverless entry point
app.debug = False
app = app.wsgi_app

# For local testing only
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
