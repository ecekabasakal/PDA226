import requests

class LastFmService:
    def __init__(self, api_key):
        self.api_key = api_key if api_key else ""
        self.base_url = "https://ws.audioscrobbler.com/2.0/"

    def fetch_tracks_by_tag(self, tag, limit=10):
        print(f"Fetching tracks for tag: {tag}")
        
        params = {
            "method": "tag.gettoptracks",
            "tag": tag,
            "limit": limit,
            "api_key": self.api_key,
            "format": "json"
        }
        headers = {"User-Agent": "AlbumCoverStudio/1.0"}
        
        try:
            response = requests.get(self.base_url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data.get("tracks", {}).get("track", [])
        except requests.exceptions.RequestException as error:
            print(f"Network error while fetching tag {tag}: {error}")
            raise Exception(f"Error while connecting to Last.fm servers: {error}")

    def generate_tracklist(self, tags, track_count):
        print(f"Generating tracklist for {track_count} tracks using tags: {tags}")
        
        final_tracklist = []
        seen_tracks = set()
        
        if not tags:
            print("No tags provided.")
            return {"error": "No tags provided."}
            
        try:
            target_count = int(track_count)
        except ValueError:
            print("Invalid track_count type.")
            return {"error": "Invalid track_count type."}
            
        fetch_limit_per_tag = max(10, (target_count // len(tags)) + 10)
        
        for tag in tags:
            if len(final_tracklist) >= target_count:
                break
                
            try:
                tracks = self.fetch_tracks_by_tag(tag, limit=fetch_limit_per_tag)
            except Exception as error:
                print(f"Skipping tag {tag} due to exception: {error}")
                continue
                
            for track in tracks:
                if len(final_tracklist) >= target_count:
                    break
                    
                track_name = track.get("name")
                artist_name = track.get("artist", {}).get("name")
                track_url = track.get("url")
                
                if not track_name or not artist_name:
                    continue
                    
                unique_id = f"{track_name.lower()}-{artist_name.lower()}"
                
                if unique_id not in seen_tracks:
                    seen_tracks.add(unique_id)
                    final_tracklist.append({
                        "title": track_name,
                        "artist": artist_name,
                        "url": track_url
                    })
                    
        if len(final_tracklist) < target_count:
            print("Warning: Could not fetch the exact requested number of tracks.")
            
        print(f"Successfully generated {len(final_tracklist)} tracks.")
        return final_tracklist