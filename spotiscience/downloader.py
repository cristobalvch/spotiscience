"""
This module implements the main functionality of Spotify's and Genius's data extraction
Author: Cristóbal Veas
Linkedln: https://www.linkedin.com/in/cristobal-veas/
"""

__author__ = "Cristóbal Veas"
__email__ = "cristobal.veas.ch@gmail.com"
__status__ = "planning"

from collections import defaultdict
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import lyricsgenius
import re
import numpy as np 

class SpotiScienceDownloader():
    """
    Class for downloading data.
    Attributes
    ----------
    credentials: dictionary
          {
              'client_id': str - spotify client id for developers,
              'client_secret : str - spotify client secret for developers.
              'redirect_url : str - spotify url for redirection (localhost is the common use),
              'user_id: str - spotify user_id  personal account,
              'genius_access_token: str - genius access token for developers
          }

    scope_playlist: str - authorization scope  defined by Spotify to use certain API methods for playlist downloading
    scope_user: str - authorization scope  defined by Spotify to use certain API methos for music downloading
    scope_user_modify: str - authorization scope  defined by Spotify to use certain API methos for app interaction

    more information of Spotify API scopes: https://developer.spotify.com/documentation/general/guides/scopes/
    """
    def __init__(self,credentials):

        self.client_id = credentials['client_id']
        self.client_secret = credentials['client_secret']
        self.redirect_url = credentials['redirect_url'] 
        self.user_id = credentials['user_id']
        self.genius_acess_token = credentials['genius_access_token']

        self.scope_playlist = 'playlist-modify-public'
        self.scope_user = 'user-library-read'
        self.scope_user_modify = 'user-library-modify' 

    def __inner__clean_spotify_id(self,id):
        """
        Search and return a string object id from the spotify copy object link 
        Attributes
        ----------
        id: str - the spotify copy song or playlist or album or artist link given by spotify  desktop application
        """
        pattern = re.compile('((?<=playlist/)|(?<=artist/)|(?<=track/)|(?<=album/))(.*)(?=\?si)')
        id = re.search(pattern,id).group()
        return id

    def __inner__auth_spotify_music(self):
        """
        Return the object api authorization for downloading  spotify global music data
        """
        manager = SpotifyClientCredentials(self.client_id,self.client_secret)
        sp = spotipy.Spotify(client_credentials_manager=manager)
        return sp

    def __inner__auth_spotify_user_music(self,scope):
        """
        Return the  object api authorization for downloading  spotify music related by the user account 
        Attributes
        ----------
        scope: str - the spotify API authorization scope
        """
        auth_manager = SpotifyOAuth(scope=scope,client_id=self.client_id,client_secret=self.client_secret,username=self.user_id, redirect_uri=self.redirect_url)
        sp = spotipy.Spotify(auth_manager=auth_manager)
        return sp 

    def __inner__get_albums_id(self,artist_id):
        """
        Return a list with Spotify album ids given a Spotify artist id
        Attributes
        ----------
        artist_id: str - the spotify id of the artist
        """
        album_ids = []
        sp = self.__inner__auth_spotify_music()
        results = sp.artist_albums(artist_id)
        for album in results['items']:
            album_ids.append(album['id'])
        return album_ids

    def __inner__get_album_songs_id(self,album_id):
        """
        Return  a list with Spotify song ids given a Spotify album id
        Attributes
        ----------
        album_id: str - the spotify id of the album
        """
        song_ids = []
        sp = self.__inner__auth_spotify_music()
        results = sp.album_tracks(album_id,offset=0)
        for songs in results['items']:
            song_ids.append(songs['id'])
        return song_ids

    def get_song_features(self,song_id):
        """
        Return a dictionary with the  song features given a spotify song id
        Attributes
        ----------
        song_id: str - the spotify id  or the spotify copy link of the song
        
        example:
        copy song link: https://open.spotify.com/track/4MRJvEFvgob7I20cj5WEbE?si=10700e68342840f6
        song id : 4MRJvEFvgob7I20cj5WEbE
        """

        if "https" in song_id:
            song_id = self.__inner__clean_spotify_id(song_id)

        FEATURES = {}

        sp = self.__inner__auth_spotify_music()
        meta = sp.track(song_id)
        feature = sp.audio_features(song_id)
        # metadata
        name = meta['name']
        album = meta['album']['name']
        artist = meta['album']['artists'][0]['name']
        release_date = meta['album']['release_date']
        length = meta['duration_ms']
        popularity = meta['popularity']
        ids =  meta['id']
        # features
        acousticness = feature[0]['acousticness']
        danceability = feature[0]['danceability']
        energy = feature[0]['energy']
        instrumentalness = feature[0]['instrumentalness']
        liveness = feature[0]['liveness']
        valence = feature[0]['valence']
        loudness = feature[0]['loudness']
        speechiness = feature[0]['speechiness']
        tempo = feature[0]['tempo']
        key = feature[0]['key']
        time_signature = feature[0]['time_signature']

        FEATURES['id']= ids
        FEATURES['name']= name
        FEATURES['artist']= artist
        FEATURES['album']= album
        FEATURES['release_date']= release_date
        FEATURES['popularity']= popularity
        FEATURES['length']= length
        FEATURES['acousticness']= acousticness
        FEATURES['danceability']= danceability
        FEATURES['energy']= energy
        FEATURES['instrumentalness']= instrumentalness
        FEATURES['liveness']= liveness
        FEATURES['valence']= valence
        FEATURES['loudness']= loudness
        FEATURES['speechiness']= speechiness
        FEATURES['tempo']= tempo
        FEATURES['key']= key
        FEATURES['time_signature']= time_signature

        return FEATURES 

    def get_playlist_information(self,playlist_id):
        """
        Return a dictionary with main playlist information
        Attributes
        ----------
        playlist_id: str - the spotify id  or the spotify copy link of the playlist
        """
        if "https" in playlist_id:
            playlist_id = self.__inner__clean_spotify_id(playlist_id)
       
        sp = self.__inner__auth_spotify_user_music(self.scope_playlist)

        playlist_info = sp.playlist_tracks(playlist_id)
        return playlist_info
        
    def get_albums_song_features(self,id,is_artist=False):
        """
        Return a dictionary of lists were the dict keys are the name of the album and the lists contains all the songs and its features
        Attributes
        ----------
        id: str [str,str,...] - the copy link or id of the albums (it could be a single string or list of strings)
        is_artist: boolean - If False, the id attributes should be  album ids or copy link (available as singe string and list of strings)
                             If True, the id attribute should be the artist id (available as single string)
        """
        print("Downloading Albums...")

        ALBUMS = defaultdict(list)

        if type(id) == str:
            album_ids = [id]
            album_ids = [self.__inner__clean_spotify_id(ids) if "https" in ids else ids for ids in album_ids]
        
        if is_artist:
            try:
                artist_id = self.__inner__clean_spotify_id(id)
            except:
                artist_id = id
            album_ids = self.__inner__get_albums_id(artist_id)

        if type(id) == list:
            album_ids = id
            album_ids = [self.__inner__clean_spotify_id(ids) if "https" in ids else ids for ids in album_ids]

        for i,album in enumerate(album_ids):

            song_ids = self.__inner__get_album_songs_id(album)
            time.sleep(.6)

            for song in song_ids:

                song_features = self.get_song_features(song)
                ALBUMS[song_features['album']].append(song_features)

            print(f"Album {song_features['album']} downloaded!")

        return ALBUMS 

    def get_playlist_song_features(self,playlist_id,n_songs=100):
        """
        Return a dictionary of lists were the dict keys are the name of the playlist and the lists contains all the songs and its features
        Attributes
        ----------
        playlist_id: str - the copy link or id of the playlist 
        n_songs: boolean - number of playlist songs (default is 100)
        """
        print("Downloading Playlist...")
        PLAYLISTS = defaultdict(list)
        songs_ids = []

        if "https" in playlist_id:
            playlist_id = self.__inner__clean_spotify_id(playlist_id)

        sp = self.__inner__auth_spotify_user_music(self.scope_playlist)

        playlist_info = sp.playlist(playlist_id)

        if n_songs < 100:
            playlist = sp.playlist_tracks(playlist_id,limit=n_songs)
            for songs in playlist['items']:
                songs_ids.append(songs['track']['id'])

        if n_songs >= 100:
            for i in range(0,n_songs,100):
                playlist = sp.playlist_tracks(playlist_id,limit=100,offset=i)
                for songs in playlist['items']:
                    songs_ids.append(songs['track']['id'])

        for song in songs_ids:
            time.sleep(.6)
            song_features = self.get_song_features(song)
            PLAYLISTS[playlist_info['name']].append(song_features)

        print(f"Playlist {playlist_info['name']} downloaded!")
            
        return PLAYLISTS

    def get_song_music_genre(self,song_id):
        """
        Return a list with all the genres of the song from spotify
        Attributes
        ----------
        song_id: str - the copy link or id of the song 
        """
        if "https" in song_id:
            song_id = self.__inner__clean_spotify_id(song_id)
        
        sp = self.__inner__auth_spotify_music()

        song = sp.track(song_id)
        album = sp.album(song['album']['id'])
        artist = sp.artist(song['artists'][0]['id'])

        if len(album['genres'])<1:
            genre = artist['genres']
        else:
            genre = album['genres']
        return genre

    def get_song_lyrics(self,songname,artistname):
        """
        Return a string with the lyrics  of the song from genius
        Attributes
        ----------
        songname: str - the name of the song
        artistname: str - the name of the artist's song
        """
        genius = lyricsgenius.Genius(self.genius_acess_token)
        genius.remove_section_headers = True
        song = genius.search_song(songname,artistname)
        return song.lyrics

    
    def get_artist_information(self,artist):
        """
        Return a string with the information of the artist
        Attributes
        ----------
        artist: str - the name of the artist
        """
        sp = self.__inner__auth_spotify_user_music(self.scope_user_modify)
        artist = sp.search(q=artist,type='artist',limit=1)
        return artist


    



                    
    
    