from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
import os
import pahe
import kwik_token
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'animepahe_downloader'
app.config['DOWNLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Downloads')

# Create download directory if it doesn't exist
if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
    os.makedirs(app.config['DOWNLOAD_FOLDER'])

# Dictionary to store active downloads and their progress
active_downloads = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query', '')
    if not query:
        return redirect(url_for('index'))
    
    search_results = pahe.search_apahe(query)
    return render_template('search_results.html', results=search_results, query=query)

@app.route('/anime/<anime_id>')
def anime_details(anime_id):
    # Get anime details from query parameters
    title = request.args.get('title', 'Unknown Anime')
    anime_type = request.args.get('type', 'Unknown')
    episodes = request.args.get('episodes', 0)
    status = request.args.get('status', 'Unknown')
    year = request.args.get('year', 'Unknown')
    score = request.args.get('score', 'Unknown')
    
    return render_template('anime_details.html', 
                          anime_id=anime_id,
                          title=title,
                          type=anime_type,
                          episodes=episodes,
                          status=status,
                          year=year,
                          score=score)

@app.route('/prepare_download', methods=['POST'])
def prepare_download():
    anime_id = request.form.get('anime_id')
    episode_start = int(request.form.get('episode_start', 1))
    episode_end = int(request.form.get('episode_end', 1))
    
    # Fetch episode IDs
    episode_ids = pahe.mid_apahe(session_id=anime_id, episode_range=[episode_start, episode_end])
    
    # Fetch episode download links
    episodes_data = pahe.dl_apahe1(anime_id=anime_id, episode_ids=episode_ids)
    
    # Organize episode data
    episodes = {}
    index = episode_start
    
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
    
    # Get available languages and qualities
    try:
        available_langs = list(episodes[episode_start].keys())
        first_lang = available_langs[0]
        available_quality = list(episodes[episode_start][first_lang].keys())
        available_quality.sort(reverse=True)
    except:
        return "Error processing episodes. Please try again.", 500
    
    # Store episode data for the download step
    session_key = f"{anime_id}_{int(time.time())}"
    app.config[f'episodes_{session_key}'] = episodes
    app.config[f'title_{session_key}'] = request.form.get('title', 'Unknown Anime')
    
    return render_template('download_options.html', 
                          session_key=session_key,
                          available_langs=available_langs,
                          available_quality=available_quality)

def download_episode_task(episode_num, download_link, destination, session_key, episode_count):
    try:
        # Get actual download link from kwik
        final_link = kwik_token.get_dl_link(download_link)
        
        # Start download with progress tracking
        active_downloads[session_key]['episodes'][episode_num] = {
            'status': 'downloading',
            'progress': 0,
            'size': 0,
            'downloaded': 0
        }
        
        # Custom download function that updates progress
        headers = {}
        if os.path.exists(destination):
            file_size = os.path.getsize(destination)
            headers = {'Range': f'bytes={file_size}-'} 
        else:
            file_size = 0
            
        response = pahe.session.get(final_link, headers=headers, stream=True)
        total_size = int(response.headers.get('content-length', 0)) + file_size
        
        active_downloads[session_key]['episodes'][episode_num]['size'] = total_size
        
        with open(destination, 'ab') as file:
            downloaded = file_size
            for data in response.iter_content(chunk_size=1024*1024):  # 1MB chunks
                if not active_downloads.get(session_key):  # Check if download was cancelled
                    break
                file.write(data)
                downloaded += len(data)
                active_downloads[session_key]['episodes'][episode_num]['downloaded'] = downloaded
                active_downloads[session_key]['episodes'][episode_num]['progress'] = int((downloaded / total_size) * 100)
        
        # Update overall progress
        active_downloads[session_key]['completed'] += 1
        active_downloads[session_key]['progress'] = int((active_downloads[session_key]['completed'] / episode_count) * 100)
        active_downloads[session_key]['episodes'][episode_num]['status'] = 'completed'
        
    except Exception as e:
        active_downloads[session_key]['episodes'][episode_num]['status'] = 'error'
        active_downloads[session_key]['episodes'][episode_num]['error'] = str(e)

@app.route('/start_download', methods=['POST'])
def start_download():
    session_key = request.form.get('session_key')
    selected_lang = request.form.get('language')
    selected_quality = request.form.get('quality')
    
    if not session_key or f'episodes_{session_key}' not in app.config:
        return "Invalid session", 400
    
    episodes = app.config[f'episodes_{session_key}']
    title = app.config[f'title_{session_key}']
    
    # Clean title for filesystem
    clean_title = ''.join(char if char.isalnum() or char in ' -_()[]' else '_' for char in title)
    
    # Create directory for anime
    anime_dir = os.path.join(app.config['DOWNLOAD_FOLDER'], clean_title)
    if not os.path.exists(anime_dir):
        os.makedirs(anime_dir)
    
    # Update episodes to contain only selected download link
    download_links = {}
    for episode_num, episode_data in episodes.items():
        try:
            quality_int = int(selected_quality)
            if selected_lang in episode_data:
                lang_data = episode_data[selected_lang]
                
                # Find best matching quality
                if quality_int in lang_data:
                    download_links[episode_num] = episode_data[selected_lang][quality_int][0]
                else:
                    available_qualities = list(lang_data.keys())
                    available_qualities.sort(reverse=True)
                    
                    # Find closest lower quality
                    closest_quality = None
                    for q in available_qualities:
                        if q <= quality_int:
                            closest_quality = q
                            break
                    
                    # If no lower quality, take highest available
                    if closest_quality is None:
                        closest_quality = available_qualities[0]
                    
                    download_links[episode_num] = episode_data[selected_lang][closest_quality][0]
        except Exception as e:
            print(f"Error processing episode {episode_num}: {str(e)}")
    
    # Set up download tracking
    active_downloads[session_key] = {
        'title': title,
        'progress': 0,
        'completed': 0,
        'total': len(download_links),
        'episodes': {}
    }
    
    # Start download threads
    for episode_num, link in download_links.items():
        destination = os.path.join(anime_dir, f"{episode_num}_{selected_lang}_{selected_quality}.mp4")
        active_downloads[session_key]['episodes'][episode_num] = {
            'status': 'pending',
            'progress': 0
        }
        
        thread = threading.Thread(
            target=download_episode_task,
            args=(episode_num, link, destination, session_key, len(download_links))
        )
        thread.daemon = True
        thread.start()
    
    return redirect(url_for('download_status', session_key=session_key))

@app.route('/download_status/<session_key>')
def download_status(session_key):
    if session_key not in active_downloads:
        return "Download session not found", 404
    
    return render_template('download_status.html', 
                          session_key=session_key,
                          title=active_downloads[session_key]['title'])

@app.route('/download_progress/<session_key>')
def download_progress(session_key):
    if session_key not in active_downloads:
        return jsonify({'error': 'Download session not found'}), 404
    
    return jsonify(active_downloads[session_key])

@app.route('/cancel_download/<session_key>')
def cancel_download(session_key):
    if session_key in active_downloads:
        del active_downloads[session_key]
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
