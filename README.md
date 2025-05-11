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

### Get Episode Information
```
GET /api/episodes?anime_id=<anime_id>&start_episode=<start>&end_episode=<end>
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

## Android App Integration

To use this API in your Android app:

1. Make HTTP requests to the deployed API endpoints using a library like Retrofit or OkHttp.
2. For downloading episodes, the API returns a direct download link that your app can use to download the file.

Example Retrofit interface:

```java
public interface AnimeService {
    @GET("api/search")
    Call<SearchResponse> searchAnime(@Query("query") String query);
    
    @GET("api/episodes")
    Call<EpisodesResponse> getEpisodes(
        @Query("anime_id") String animeId,
        @Query("start_episode") int startEp,
        @Query("end_episode") int endEp
    );
    
    @POST("api/download")
    Call<DownloadResponse> getDownloadLink(@Body DownloadRequest request);
}
```

3. When you receive the download link, use Android's DownloadManager or a library like OkHttp to download the file.
