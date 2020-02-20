import os, requests, json
from secrets import spotify_token, spotify_user_id

# TODO: Add function that checks if the user already has a playist of specified name before attempting to create a new playlist as otherwise it will create duplicates
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
    
    def create_playlist(self):
        # Look at https://developer.spotify.com/console/post-playlists/ for details on spotify API for creating playlists
        request_body = json.dumps({
            "name": "Discovered Songs",
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

    def add_songs(self):
        # Check out the docs https://developer.spotify.com/documentation/web-api/reference/playlists/add-tracks-to-playlist/
        # NOTE: Spotify only lets you add 100 songs per request max
        playlist_id = self.create_playlist()

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