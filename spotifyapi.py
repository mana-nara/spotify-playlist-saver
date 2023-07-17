
# Import libraries
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import numpy as np
import time
import os

from flask import Flask, request, url_for,session, redirect

# Spotify API credentials
app = Flask(__name__) # create instance of Flask class
app.config['SESSION_COOKIE_NAME'] = 'spotify-cookie'# set the cookie name here
app.secret_key = os.urandom(24)# set the secret key here as a string
TOKEN_INFO = 'token_info'

@app.route('/')
def login():
    auth_url = CreateSpotifyOAuth().get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirectPage():
    session.clear()
    code = request.args.get('code') # get the code from the url
    token_info = CreateSpotifyOAuth().get_access_token(code) # get token info from the code
    session[TOKEN_INFO] = token_info # save token info in a session
    return redirect(url_for('saveDiscoverWeeklyPlaylist',_external=True)) # redirect to the saveDiscoverWeeklyPlaylist function

def getToken():
    token_info = session.get(TOKEN_INFO, None) # get token info from the session
    if not token_info:
        return redirect(url_for('login', _external=True)) # redirect to the login function
    now = int(time.time()) # get current time
    is_expired = token_info['expires_at'] - now < 60 # check if token is expired
    if is_expired:
        # refresh token
        sp_oauth = CreateSpotifyOAuth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info['access_token'] # return the access token


@app.route('/saveDiscoverWeeklyPlaylist')
def saveDiscoverWeeklyPlaylist():
    try:
        token_info = getToken() # get the access token
    except:
        print("User not logged in")
        return redirect('/')

    #return("Successfully logged in")#For testing purposes
    sp = spotipy.Spotify(auth=token_info['access_token']) # create a spotify object
    UserID = sp.current_user()['id'] # get the current user's ID
    savedDiscoverWeeklyID = None

    currentPlaylists = sp.current_user_playlists()['items'] # get the current user's playlists
    for playlist in currentPlaylists:
        if playlist['name'] == 'Discover Weekly':
            discoverWeeklyID = playlist['id']
        if playlist['name'] == 'Saved Discover Weekly':
            savedDiscoverWeeklyID = playlist['id']

    if not discoverWeeklyID:
        return("Discover Weekly playlist not found")
    if not savedDiscoverWeeklyID:
        sp.user_playlist_create(UserID, 'My Saved Discover Weekly',True)
        savedDiscoverWeeklyID = new_playlist['id']

    discoverWeeklyPlaylist = sp.playlist(discoverWeeklyID) # get the discover weekly playlist
    songs = [] # list to store the songs
    for song in discoverWeeklyPlaylist['items']:
        songURI = song['track']['uri']
        songs.append(songURI)# add the song to the list

    sp.user_playlist_add_tracks(UserID, savedDiscoverWeeklyID, songs) # add the songs to the saved discover weekly playlist
    return "Successfully added songs to the playlist"






def CreateSpotifyOAuth():
    return SpotifyOAuth(
        client_id = "your client id",
        client_secret = "your client secret",
        redirect_uri = url_for('redirectPage', _external=True),
        scope = 'user-library-read playlist-modify-public playlist-modify-private'
    )

app.run(debug=True)
