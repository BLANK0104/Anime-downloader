from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import os
import kwik_token
import pahe
import threading
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'animepahedownloader_secret_key'  # Change this to a random secret key
app.config['DOWNLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Downloads')

# Ensure download directory exists
if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
    os.makedirs(app.config['DOWNLOAD_FOLDER'])

# Dictionary to store download progress
download_status = {}

# Function to replace special characters in a string
def replace_special_characters(input_string, replacement="_"):
    special_characters = "!@#$%^&*()_+{}[]|\\:;<>,.?/~` "
    for char in special_characters:
        input_string = input_string.replace(char, replacement)
    return input_string

# Function to extract anime titles and year to show in results
def get_titles_from_result(list_of_anime):
    return [f"{anime[0]} - {anime[4]} ({anime[1]})" for anime in list_of_anime]

# Download thread function
def download_episodes(anime_title, episodes, lang, quality):
    global download_status
    download_id = f"{anime_title}_{lang}_{quality}"
    download_status[download_id] = {
        'status': 'starting',
        'progress': 0,
        'total': len(episodes),
        'completed': 0,
        'current_episode': 0,
        'message': 'Preparing to download...'
    }
    
    title = replace_special_characters(anime_title)
    download_dir = os.path.join(app.config['DOWNLOAD_FOLDER'], title)
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    download_status[download_id]['status'] = 'downloading'
    
    for episode_num, url in episodes.items():
        try:
            download_status[download_id]['current_episode'] = episode_num
            download_status[download_id]['message'] = f"Getting download link for episode {episode_num}..."
            
            download_link = kwik_token.get_dl_link(url)
            destination = os.path.join(download_dir, f"{episode_num}_{lang}_{quality}.mp4")
            
            download_status[download_id]['message'] = f"Downloading episode {episode_num}..."
            pahe.download_file(url=download_link, destination=destination)
            
            download_status[download_id]['completed'] += 1
            download_status[download_id]['progress'] = int((download_status[download_id]['completed'] / download_status[download_id]['total']) * 100)
        except Exception as e:
            download_status[download_id]['message'] = f"Error downloading episode {episode_num}: {str(e)}"
            continue
    
    download_status[download_id]['status'] = 'completed'
    download_status[download_id]['message'] = 'Download completed!'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        if not query:
            flash('Please enter a search query', 'error')
            return redirect(url_for('index'))
            
        list_of_anime = pahe.search_apahe(query)
        
        if len(list_of_anime) == 0:
            flash('No anime found!', 'error')
            return redirect(url_for('index'))
        
        session['search_results'] = list_of_anime
        return redirect(url_for('results'))
    
    return redirect(url_for('index'))

@app.route('/results')
def results():
    if 'search_results' not in session:
        flash('Please search for anime first', 'error')
        return redirect(url_for('index'))
        
    list_of_anime = session['search_results']
    list_of_titles = get_titles_from_result(list_of_anime)
    return render_template('results.html', titles=list_of_titles, anime_list=list_of_anime)

@app.route('/anime/<int:anime_index>')
def anime_detail(anime_index):
    if 'search_results' not in session:
        flash('Please search for anime first', 'error')
        return redirect(url_for('index'))
    
    list_of_anime = session['search_results']
    if anime_index < 0 or anime_index >= len(list_of_anime):
        flash('Invalid anime selection', 'error')
        return redirect(url_for('results'))
    
    selected_anime = list_of_anime[anime_index]
    session['selected_anime'] = selected_anime
    
    return render_template('anime_detail.html', anime=selected_anime)

@app.route('/episodes', methods=['POST'])
def select_episodes():
    if 'selected_anime' not in session:
        flash('Please select an anime first', 'error')
        return redirect(url_for('results'))
    
    selected_anime = session['selected_anime']
    anime_id = selected_anime[6]
    total_episodes = selected_anime[2]
    
    episode_start = request.form.get('episode_start', '1')
    episode_end = request.form.get('episode_end', str(total_episodes))
    
    try:
        episode_start = int(episode_start)
        episode_end = int(episode_end)
        
        if episode_start < 1 or episode_start > total_episodes or episode_end > total_episodes:
            flash('Episode range exceeds total number of episodes', 'error')
            return redirect(url_for('anime_detail', anime_index=session['search_results'].index(selected_anime)))
    except ValueError:
        flash('Please enter valid episode numbers', 'error')
        return redirect(url_for('anime_detail', anime_index=session['search_results'].index(selected_anime)))
    
    episode_range = [episode_start, episode_end]
    session['episode_range'] = episode_range
    
    # Fetch episode IDs
    episode_ids = pahe.mid_apahe(session_id=anime_id, episode_range=episode_range)
    
    # Fetch episode download links
    episodes_data = pahe.dl_apahe1(anime_id=anime_id, episode_ids=episode_ids)
    
    # Organize episode data
    episodes = {}
    index = episode_range[0]
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
    
    session['episodes_data'] = episodes
    
    # Get available languages and qualities from first episode
    available_langs = list(episodes[episode_range[0]].keys())
    
    return render_template('quality_selection.html', 
                          languages=available_langs, 
                          anime_title=selected_anime[0])

@app.route('/download', methods=['POST'])
def download():
    if 'episodes_data' not in session or 'selected_anime' not in session:
        flash('Please select episodes first', 'error')
        return redirect(url_for('index'))
    
    selected_anime = session['selected_anime']
    episodes = session['episodes_data']
    episode_range = session['episode_range']
    
    # Get user selections
    lang = request.form.get('language')
    quality = request.form.get('quality')
    
    if not lang or not quality:
        flash('Please select language and quality', 'error')
        return redirect(url_for('episodes'))
    
    # Update episodes dictionary to contain selected download link
    final_episodes = {}
    for key, items in episodes.items():
        if lang not in items:
            flash(f'Language {lang} not available for episode {key}', 'warning')
            continue
            
        backup_quality = sorted(list(episodes[key][lang].keys()))[0]  # Use the first quality as backup
        
        try:
            # Convert quality to integer for proper comparison
            quality_int = int(quality)
            
            # Check if exact quality is available
            if quality_int in episodes[key][lang]:
                final_episodes[key] = episodes[key][lang][quality_int][0]
            else:
                # Find closest available quality if exact match not available
                available_qualities = sorted(list(episodes[key][lang].keys()), reverse=True)
                
                # Find closest lower quality
                closest_quality = None
                for q in available_qualities:
                    if q <= quality_int:
                        closest_quality = q
                        break
                
                # If no lower quality, take highest available
                if closest_quality is None:
                    closest_quality = available_qualities[0]
                
                final_episodes[key] = episodes[key][lang][closest_quality][0]
                flash(f"Selected quality {quality}p not available for episode {key}, using {closest_quality}p instead", 'info')
        except Exception as e:
            try:
                # Use backup quality as last resort
                final_episodes[key] = episodes[key][lang][backup_quality][0]
                flash(f"Using fallback quality for episode {key}", 'info')
            except:
                flash(f"Failed to find suitable quality for episode {key}", 'error')
                pass
    
    # Fetch video links
    kwik_episodes = {}
    for key, value in final_episodes.items():
        kwik_episodes[key] = pahe.dl_apahe2(value)
    
    # Start downloading in a separate thread
    download_thread = threading.Thread(
        target=download_episodes,
        args=(selected_anime[0], kwik_episodes, lang, quality)
    )
    download_thread.daemon = True
    download_thread.start()
    
    download_id = f"{selected_anime[0]}_{lang}_{quality}"
    session['download_id'] = download_id
    
    return redirect(url_for('download_status'))

@app.route('/download_status')
def download_status_page():
    download_id = session.get('download_id')
    if not download_id or download_id not in download_status:
        flash('No active download found', 'error')
        return redirect(url_for('index'))
        
    return render_template('download_status.html', download_id=download_id)

@app.route('/api/download_status/<download_id>', methods=['GET'])
def get_download_status(download_id):
    if download_id not in download_status:
        return jsonify({'error': 'Download not found'}), 404
    
    return jsonify(download_status[download_id])

if __name__ == '__main__':
    app.run(debug=True)
