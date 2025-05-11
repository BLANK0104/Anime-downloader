import json
from time import sleep
import grequests
import requests
import re
import os
from tqdm import tqdm

session = requests.session()

# Base URL for animepahe.ru
url = "https://animepahe.ru/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "X-Requested-With": "XMLHttpRequest",
    "Cookie": "__ddgid_=7lWyc52yRS7YgOpW; __ddgmark_=wfZpnxacF2nXdVTE; __ddg2_=qtEE5nKN3PCJ7c2Z; __ddg1_=5Qh2v4L5z7LpVnQx; __ddg3_=fHwWwZbYpI3fHcQx"
}

def get_json_response(url, retries=3, delay=1):
    """
    Get JSON response from a URL using pure requests.
    Retries on failure and includes a delay between attempts.
    
    Parameters:
        url (str): The URL to fetch
        retries (int): Number of retry attempts
        delay (int): Delay between retries in seconds
    
    Returns:
        dict: JSON response data
    """
    for attempt in range(retries):
        try:
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            return response.json()
        except Exception as e:
            if attempt < retries - 1:
                print(f"Request failed, retrying ({attempt+1}/{retries}): {e}")
                sleep(delay)
            else:
                print(f"Failed to get response after {retries} attempts: {e}")
                raise

def search_apahe(query: str) -> list:
    """
    Search animepahe.ru for anime matching the given query.
    
    Parameters:
        query (str): The search query.
    
    Returns:
        A list of lists, where each inner list contains the following information
        about a search result:
            - Title
            - Type (e.g. TV, movie)
            - Number of episodes
            - Status (e.g. completed, airing)
            - Year
            - Score
            - Session ID
    """
    global url
    search_url = url + "api?m=search&q=" + query

    try:
        data = get_json_response(search_url)
    except Exception as e:
        print(f"Search failed: {e}")
        return []

    # if data is empty, return an empty list. i.e. no anime found
    if "data" not in data:
        return []

    clean_data = []
    for i in data["data"]:
        hmm = []
        hmm.append(i['title'])
        hmm.append(i['type'])
        hmm.append(i['episodes'])
        hmm.append(i['status'])
        hmm.append(i['year'])
        hmm.append(i['score'])
        hmm.append(i['session'])
        clean_data.append(hmm)
    return clean_data

def mid_apahe(session_id: str, episode_range: list) -> list:
    """
    Retrieve a list of episode IDs for the specified session ID within a given range.
    
    Parameters:
        session_id (str): The unique session ID.
        episode_range (list): A list containing the start and end episode IDs within the range.
    
    Returns:
        list: A list of episode IDs.
    """
    start_ep, end_ep = episode_range[0], episode_range[1]
    
    # Calculate pages more efficiently
    # Each page has 30 episodes
    start_page = (start_ep - 1) // 30 + 1
    end_page = (end_ep - 1) // 30 + 1
    
    global url
    episode_ids = []
    
    # Batch requests for all required pages
    page_urls = [
        f"{url}api?m=release&id={session_id}&sort=episode_asc&page={page}" 
        for page in range(start_page, end_page + 1)
    ]
    
    responses = []
    for page_url in page_urls:
        try:
            response = get_json_response(page_url)
            responses.append(response)
        except Exception as e:
            print(f"Failed to get page {page_url}: {e}")
            # Return empty list on error
            return []
    
    # Process all responses
    all_episodes = []
    for response in responses:
        if 'data' in response:
            all_episodes.extend(response['data'])
    
    # Calculate start and end indices in the combined episode list
    start_idx_in_first_page = (start_ep - 1) % 30
    total_episodes = len(all_episodes)
    
    # Extract only the requested episode range
    # First, calculate how many episodes we need from the start_ep to end_ep
    needed_episodes = end_ep - start_ep + 1
    
    # Then, get only those episodes from all_episodes
    relevant_episodes = all_episodes[start_idx_in_first_page:start_idx_in_first_page + needed_episodes]
    
    # Extract session IDs
    for episode in relevant_episodes:
        if 'session' in episode:
            episode_ids.append(episode['session'])
    
    return episode_ids

def dl_apahe1(anime_id: str, episode_ids: list) -> dict:
    """
    Get a list of download links for the given episode IDs.
    Uses individual requests instead of grequests for better compatibility.
    
    Parameters:
        anime_id (str): The anime ID.
        episode_ids (list): List of episode IDs.
    
    Returns:
        A dictionary where keys are episode indices and values are lists of download link information.
    """
    global url
    data_dict = {}
    
    # Process each episode sequentially for better stability
    for index, episode_id in enumerate(episode_ids):
        episode_url = f'{url}play/{anime_id}/{episode_id}'
        try:
            response = session.get(url=episode_url, headers=headers, timeout=10)
            if response.status_code == 200:
                text = response.text
                data = re.findall(r'href="(?:([^\"]+)" target="_blank" class="dropdown-item">(?:[^\&]+)&middot; ([^\<]+))(?:<span class="badge badge-primary">(?:[^\&]+)</span> <span class="badge badge-warning text-capitalize">([^\<]+))?', text)
                data_dict[index] = data
            else:
                print(f"Episode {episode_id} returned status code {response.status_code}")
                data_dict[index] = []
        except Exception as e:
            print(f"Error fetching episode {episode_id}: {e}")
            data_dict[index] = []
            
    return data_dict

def dl_apahe2(url: str) -> str:
    """
    Follow a redirect link to get the final download link.
    
    Parameters:
        url (str): The redirect link.
    
    Returns:
        The final download link.
    """
    try:
        r = requests.get(url, timeout=10)
        redirect_links = re.findall(r'(https://kwik\.[a-z]+/[^"]+)', r.text)
        if redirect_links:
            return redirect_links[0]
        else:
            print("No kwik link found in response")
            return ""
    except Exception as e:
        print(f"Error getting kwik link: {e}")
        return ""

def download_file(url, destination):
    if os.path.exists(destination):
        file_size = os.path.getsize(destination)
    else:
        file_size = 0

    headers = {'Range': f'bytes={file_size}-'} if file_size else None
    response = requests.get(url, headers=headers, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    if response.status_code == 206:
        print("Downloading resumed successfully.")
    elif response.status_code == 200:
        print("Downloading")

    with open(destination, 'ab') as file, tqdm(
        desc=destination,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=69420):
            bar.update(len(data))
            file.write(data)