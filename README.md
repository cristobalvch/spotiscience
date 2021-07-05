# SPOTISCIENCE

Spotiscience is a Python library for extracting and modelling music data of Spotify and Genius

### Recomended:  See completely guide to use the library

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install spotiscience.

```bash
pip install spotiscience
```

Use the git option 
```bash
git clone https://github.com/cristobalvch/spotiscience.git
```


## Usage

```python
import spotiscience

#create a dictionary with authorization keys
CREDENTIALS = {}
CREDENTIALS['client_id'] = "your_spotify_client_id"
CREDENTIALS['client_secret'] = "your_spotify_client_secret"
CREDENTIALS['redirect_url'] = "your_redirect_url"
CREDENTIALS['user_id'] = "your_spotify_user_id"
CREDENTIALS['genius_access_token'] = "your_genius_access_token"

# returns 'downloader class'
sd = spotiscience.SpotiScienceDownloader(credentials=CREDENTIALS)

# returns 'predicter class'
sp = spotiscience.SpotiSciencePredicter()

```
## Download Music Data

```python
# Returns song features

song_copy_link = "https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b?si=369f90167c9d48fb"
song = sd.get_song_features(song_id=song_copy_link)
song

[output]
{'id': '0VjIjW4GlUZAMYd2vXMi3b',
 'name': 'Blinding Lights',
 'artist': 'The Weeknd',
 'album': 'After Hours',
 'release_date': '2020-03-20',
 'popularity': 94,
 'length': 200040,
 'acousticness': 0.00146,
 'danceability': 0.514,
 'energy': 0.73,
 'instrumentalness': 9.54e-05,
 'liveness': 0.0897,
 'valence': 0.334,
 'loudness': -5.934,
 'speechiness': 0.0598,
 'tempo': 171.005,
 'key': 1,
 'time_signature': 4}

# Returns song lyric
song_lyric = sd.get_song_lyrics(songname=song['name'],artistname=song['artist'])
```

## Topic Modelling and Music Mood Prediction

```python
#predict the mood of the song
mood = sp.predict_song_mood(song=song)
mood

[output]
'energy'

#predict the topics of the song lyric
topics = sp.predict_topic_lyric(lyric=lyrics,model='lda',lang='english',n_grams=(1,1),n_topics=1,top_n=5)
topics

[output]
defaultdict(list,
            {'Topic 0:': [[('hey', 8.249863616778203),
               ('ooh', 6.627924700037221),
               ('touch', 5.011524363507339),
               ('light', 4.997437601882748),
               ('feel', 4.23125338314076)]]})

```

## Authors and acknowledgment
Cristóbal Veas - Data Scientist , feel free to contact me on [Linkedln](https://www.linkedin.com/in/cristobal-veas/)

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
