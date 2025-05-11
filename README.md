# AnimeDownloader 🍿📥

Lights, camera, ACTION! 🎬 Ready to embark on an anime-tastic adventure with AnimeDownloader? Grab your popcorn and get ready to download your favorite anime episodes with ease! 🍿✨

## What's the Deal? 🤔

AnimeDownloader is your trusty sidekick in the world of anime. It's your one-stop-shop for fetching those animated gems from the vast internet seas. It's like a Shinkansen (bullet train) for anime episodes, only without the rails! 🚄📺

## Features 🌟

- **Anime Hunt**: Search for your favorite anime like a ninja in the night. 🦸
- **Organized Chaos**: Downloaded episodes neatly organized into folders. No more messy downloads! 📁✨
- **Quality Control**: Choose your video resolution and quality, like a true anime connoisseur. 📐👀
- **No Language Barrier**: Select your preferred language for that authentic experience. 🗣️🌍

## How to Get Started 🚀

1. Clone the repository.
2. Install the required Python libraries using `pip install -r requirements.txt`.
3. Run the `main.py` script and let the anime magic begin! 🧙

### Windows Users
1. Navigate to the `Windows` folder in the script directory.
2. Install the required Python libraries using `pip install -r requirements.txt`.
3. Run the `main.py` script and let the anime magic begin! 🧙

## AnimePahe Magic ◕⩊◕

We've integrated AnimePahe's superpowers to fetch your episodes seamlessly. Say goodbye to buffering! 🧙‍♂️🎩

## Contribution 💪

We welcome fellow anime enthusiasts to join our crew! Pull requests are like Shuriken; they help us get things done faster! 👒⚔🏴‍☠️🌊

## License 📜

This project is licensed under the GNU License. It's as free as a Pikachu in the wild! ⚡🐭

## Disclaimer ⚠️

Remember to be a responsible anime pirate! Only download content you have the right to access. We don't want to anger the anime gods! 😇🙏

Get ready for an anime-tastic journey with AnimeDownloader! Let the downloading spree begin! 🌟📥

## Note: Updating the Base URL ⚠️

AnimePahe is known to change its base URL from time to time. If you encounter issues with the current base URL (https://animepahe.ru/), here's how you can update it to ensure that AnimeDownloader continues to work seamlessly:

1. Open the `pahe.py` file in your project directory.

2. Locate the `url` variable at the beginning of the file, which contains the current AnimePahe base URL:

   `url = "https://animepahe.ru/"`

   Update with the Current Url

---

# AnimePaheDownloader API

This is a Flask-based API that provides access to AnimePahe downloader functionality.

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the Flask application:
   ```
   python app.py
   ```

## Deployment

### Vercel Deployment

AnimePaheDownloader API can be easily deployed on Vercel's serverless platform:

1. Install the Vercel CLI:
   ```
   npm install -g vercel
   ```

2. Navigate to your project directory:
   ```
   cd path/to/AnimePaheDownloader
   ```

3. Deploy to Vercel:
   ```
   vercel
   ```

4. Follow the prompts to configure your project:
   - Set up a new Vercel project
   - Link to an existing project or create a new one
   - Confirm the project root directory

5. Once deployed, Vercel will give you a URL for your API.

### Alternative Deployment Method

You can also deploy directly from the Vercel dashboard:

1. Push your code to a GitHub repository
2. Log in to your Vercel account
3. Click "New Project"
4. Import your GitHub repository
5. Configure the project settings:
   - Framework preset: Other
   - Build command: None
   - Output directory: None
6. Click "Deploy"

## API Endpoints

### Search for Anime
```
GET /api/search?query=<search_term>
```

> **Note:** The actual response from the deployed Vercel API will have a slightly different format, with fields in a different order:
>
> ```json
> {
>   "results": [
>     {
>       "episodes": 26,
>       "score": 8.43,
>       "session_id": "8d0c8929-47e2-a116-8c83-5b83afec7b1e",
>       "status": "Finished Airing",
>       "title": "Demon Slayer: Kimetsu no Yaiba",
>       "type": "TV",
>       "year": 2019
>     },
>     {
>       "episodes": 11,
>       "score": 8.72,
>       "session_id": "e4413711-aba2-fa1c-6181-480031ad6c0c",
>       "status": "Finished Airing",
>       "title": "Demon Slayer: Kimetsu no Yaiba Entertainment District Arc",
>       "type": "TV",
>       "year": 2022
>     }
>   ]
> }
> ```

### Get Episode Information
```
GET /api/episodes?anime_id=<anime_id>&start_episode=<start>&end_episode=<end>
```

> **⚠️ Important Thread Issue Note:**
> 
> If you encounter an error like `{"error":"cannot switch to a different thread (which happens to have exited)"}` when querying the episodes endpoint on Vercel, this is due to Vercel's serverless function limitations with certain operations in the application.
>
> **Potential solutions:**
> 
> 1. **Modify the `api/index.py` file** to avoid using Selenium or other thread-heavy operations:
>    - Replace Selenium-based operations with pure requests
>    - Simplify the episode fetching logic to be more compatible with serverless environments
>
> 2. **Consider using a different hosting provider** that supports long-running processes, such as:
>    - Digital Ocean App Platform
>    - Heroku
>    - AWS EC2
>    - Google Cloud Run with increased timeout settings
>
> 3. **For quick testing**, you can use your local development environment to test episode retrieval, then use the deployed API for search and direct link generation.

**Expected Response when working properly:**
```json
{
  "episodes": {
    "1": {
      "jpn": {
        "720": ["https://pahe.win/DemonSlayer-01-720p"],
        "1080": ["https://pahe.win/DemonSlayer-01-1080p"]
      },
      "eng": {
        "720": ["https://pahe.win/DemonSlayer-01-720p-dub"]
      }
    },
    "2": {
      "jpn": {
        "720": ["https://pahe.win/DemonSlayer-02-720p"],
        "1080": ["https://pahe.win/DemonSlayer-02-1080p"]
      },
      "eng": {
        "720": ["https://pahe.win/DemonSlayer-02-720p-dub"]
      }
    },
    "3": {
      "jpn": {
        "720": ["https://pahe.win/DemonSlayer-03-720p"],
        "1080": ["https://pahe.win/DemonSlayer-03-1080p"]
      },
      "eng": {
        "720": ["https://pahe.win/DemonSlayer-03-720p-dub"]
      }
    }
  }
}
```

### Get Download Link
```
POST /api/download
Content-Type: application/json

{
  "anime_id": "session_id",
  "episode_num": 1,
  "lang": "eng",
  "quality": 720,
  "anime_title": "Title of Anime"
}
```

Response:
```json
{
  "message": "Download link generated",
  "download_link": "https://example.com/download/path/file.mp4",
  "quality": 720,
  "language": "eng",
  "episode": 1,
  "anime_title": "Title of Anime"
}
```

## ✅ Vercel Compatibility Update

The API has been optimized for Vercel's serverless environment:

1. **Selenium Removed**: We've replaced all Selenium-based operations with pure HTTP requests
2. **Thread-Safe Operations**: Episode fetching logic has been simplified to work within serverless constraints 
3. **Optimized Performance**: Batch processing has been improved to handle requests more efficiently

These changes ensure the API works reliably on Vercel, resolving the thread switching errors that were previously occurring.

## Example API Usage with "Demon Slayer"

### 1. Search for the Anime

**Request:**
```
GET /api/search?query=demon%20slayer
```

**Response:**
```json
{
  "results": [
    {
      "episodes": 26,
      "score": 8.43,
      "session_id": "8d0c8929-47e2-a116-8c83-5b83afec7b1e",
      "status": "Finished Airing",
      "title": "Demon Slayer: Kimetsu no Yaiba",
      "type": "TV",
      "year": 2019
    },
    {
      "episodes": 11,
      "score": 8.72,
      "session_id": "e4413711-aba2-fa1c-6181-480031ad6c0c",
      "status": "Finished Airing",
      "title": "Demon Slayer: Kimetsu no Yaiba Entertainment District Arc",
      "type": "TV",
      "year": 2022
    }
  ]
}
```

### 2. Get Episode Information for Season 1

**Request:**
```
GET /api/episodes?anime_id=8d0c8929-47e2-a116-8c83-5b83afec7b1e&start_episode=1&end_episode=3
```

**Response:**
```json
{
  "episodes": {
    "1": {
      "jpn": {
        "720": ["https://pahe.win/DemonSlayer-01-720p"],
        "1080": ["https://pahe.win/DemonSlayer-01-1080p"]
      },
      "eng": {
        "720": ["https://pahe.win/DemonSlayer-01-720p-dub"]
      }
    },
    "2": {
      "jpn": {
        "720": ["https://pahe.win/DemonSlayer-02-720p"],
        "1080": ["https://pahe.win/DemonSlayer-02-1080p"]
      },
      "eng": {
        "720": ["https://pahe.win/DemonSlayer-02-720p-dub"]
      }
    },
    "3": {
      "jpn": {
        "720": ["https://pahe.win/DemonSlayer-03-720p"],
        "1080": ["https://pahe.win/DemonSlayer-03-1080p"]
      },
      "eng": {
        "720": ["https://pahe.win/DemonSlayer-03-720p-dub"]
      }
    }
  }
}
```

### 3. Get Direct Download Link for Episode 1 (1080p, Japanese)

**Request:**
```
POST /api/download
Content-Type: application/json

{
  "anime_id": "8d0c8929-47e2-a116-8c83-5b83afec7b1e",
  "episode_num": 1,
  "lang": "jpn",
  "quality": 1080,
  "anime_title": "Demon Slayer: Kimetsu no Yaiba"
}
```

**Response:**
```json
{
  "message": "Download link generated",
  "download_link": "https://kwik.cx/f/AbCdEfGhIjKlMnOp/1080.mp4",
  "quality": 1080,
  "language": "jpn",
  "episode": 1,
  "anime_title": "Demon Slayer: Kimetsu no Yaiba"
}
```

### Android App Integration

In your Android app, you can use these APIs to create a complete anime downloading experience:

```kotlin
// Example using Retrofit in Kotlin
class DemonSlayerDownloader {
    private val apiService = RetrofitClient.animeService
    
    suspend fun downloadEpisode(context: Context) {
        // Step 1: Search for Demon Slayer
        val searchResponse = apiService.searchAnime("demon slayer")
        val demonSlayer = searchResponse.results.firstOrNull { it.title == "Demon Slayer: Kimetsu no Yaiba" }
        
        if (demonSlayer != null) {
            // Step 2: Get episodes info
            val episodesResponse = apiService.getEpisodes(
                demonSlayer.session_id, 
                startEp = 1, 
                endEp = 1
            )
            
            // Step 3: Get download link
            val downloadRequest = DownloadRequest(
                animeId = demonSlayer.session_id,
                episodeNum = 1,
                lang = "jpn",
                quality = 1080,
                animeTitle = demonSlayer.title
            )
            
            val downloadResponse = apiService.getDownloadLink(downloadRequest)
            
            // Step 4: Use Android's DownloadManager to download the file
            val downloadManager = context.getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
            val request = DownloadManager.Request(Uri.parse(downloadResponse.downloadLink))
                .setTitle("Downloading ${demonSlayer.title} - Episode 1")
                .setDescription("Downloading episode in 1080p")
                .setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                .setDestinationInExternalPublicDir(
                    Environment.DIRECTORY_DOWNLOADS,
                    "Anime/${demonSlayer.title}/Episode_1_1080p.mp4"
                )
            
            downloadManager.enqueue(request)
        }
    }
}
```
