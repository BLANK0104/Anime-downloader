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

## API Endpoints

### Search for Anime
```
GET /api/search?query=<search_term>
```

### Get Episode Information
```
GET /api/episodes?anime_id=<anime_id>&start_episode=<start>&end_episode=<end>
```

### Start Download
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

### Get Download Status
```
GET /api/download/status/<download_id>
```

### List All Downloads
```
GET /api/download/list
```

### Download File
```
GET /api/download/file/<download_id>
```

## Deployment

The application includes a Procfile for deploying to Heroku or similar platforms.
```
heroku create
git push heroku main
```

You can also deploy to other platforms that support Python web applications.

## Android App Integration

To use this API in your Android app, make HTTP requests to the deployed API endpoints using a library like Retrofit or OkHttp.
