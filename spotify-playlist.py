import os, requests, json
from secrets import spotify_token, spotify_user_id

class SpotifyPlaylist:
    def __init__(self):
        # Dict to store the artist name and song title
        self.all_song_info = {}
    
    def get_songs(self, filename):
        '''Gets songs from txt file and adds them to all_song_info dictionary'''
        f = open(filename, "r")
        data = f.readlines()

        for x in data:
            artist = x.split(' - ')[0]
            track = x.split(' - ')[1].rstrip()
            self.all_song_info[artist] = track
        f.close()
    
    def create_playlist(self, playlist_name):
        # Look at https://developer.spotify.com/console/post-playlists/ for details on spotify API for creating playlists
        playlists = self.get_user_playlists()

        # Check if playlist already exists, if it does then return its id
        for playlist in playlists:
            if playlist["name"] == playlist_name:
                return playlist["id"]

        request_body = json.dumps({
            "name": playlist_name,
            "description": "Songs I have come accross and liked.",
            "public": False
        })

        query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)

        response = requests.post(
            query,
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()

        # Check out the example response at https://developer.spotify.com/documentation/web-api/reference/playlists/create-playlist/
        return response_json["id"]

    ''' Gets the uri of a specified track and returns it '''
    def get_uri(self, song_name, artist):
        query = "https://api.spotify.com/v1/search?query={}+{}&type=track&offset=0&limit=20".format(
            song_name,
            artist
        )

        response = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()
        songs = response_json["tracks"]["items"]

        uri = songs[0]["uri"]
        return uri

    ''' Gets the current users playlists and returns them '''
    def get_user_playlists(self):
        query = "https://api.spotify.com/v1/me/playlists"

        response = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )

        response_json = response.json()
        playlists = response_json["items"]
        return playlists

    def add_songs(self):
        # Check out the docs https://developer.spotify.com/documentation/web-api/reference/playlists/add-tracks-to-playlist/
        # NOTE: Spotify only lets you add 100 songs per request max

        # NOTE: We are hard coding in the playlist name but this can be changed later for better usability and customization for the user
        playlist_id = self.create_playlist("Discovered Songs")

        uris = []
        for key in self.all_song_info:
            uris.append(self.get_uri(key, self.all_song_info[key]))
        
        request_body = json.dumps({
            "uris": uris
        })
        
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id)

        response = requests.post(
            query,
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )

        response_json = response.json()
        print(response_json)



if __name__ == '__main__':
    p = SpotifyPlaylist()
    p.get_songs("songs.txt")
    p.add_songs()