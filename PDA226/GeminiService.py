import json
import time
from google import genai


class GeminiService:
    def __init__(self, api_key):
        self.api_key = api_key if api_key else ""
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "gemini-1.5-flash"

    def _create_prompt(self, journal_text, genre, era, track_count):
        prompt = f"""
        Task: Act as a music curator and analyze the user's journal entry.

        Inputs:
        - Journal: "{journal_text}"
        - Music Genre: {genre}
        - Era: {era}
        - Track Count: {track_count}

        Desired Output:
        Return ONLY a valid JSON object strictly matching the following schema. Do not include any markdown formatting or extra text:
        {{
          "album_name": "Album name",
          "artist_name": "Artist name",
          "year": "A year from the {era}",
          "label": "Fictional record label",
          "mood_description": "Short mood summary",
          "cover_prompt": "Detailed visual prompt for Pollinations.ai in {genre} style",
          "lastfm_tags": ["4-6 lowercase last.fm compatible tags"]
        }}
        """
        return prompt

    def _parse_json_response(self, text):
        try:
            json_str = text.strip()
            if json_str.startswith("```"):
                json_str = json_str.replace("```json", "").replace("```", "").strip()
            parsed_data = json.loads(json_str)
            return parsed_data
        except Exception as e:
            print(f"JSON Parsing Error: {e}")
            return None

    def generate_album_metadata(self, journal_text, genre, era, track_count):
        prompt = self._create_prompt(journal_text, genre, era, track_count)

        for attempt in range(3):
            try:
                print(f"Connecting to Gemini API... (Attempt {attempt + 1}/3)")
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=prompt
                )

                if not response or not response.text:
                    continue

                album_data = self._parse_json_response(response.text)

                if album_data:
                    print("Success! Album metadata generated.")
                    return album_data

            except Exception as e:
                print(f"API Error (Attempt {attempt + 1}): {e}")
                time.sleep(1)

        print("Could not get a valid response from Gemini API after 3 attempts.")
        return None



