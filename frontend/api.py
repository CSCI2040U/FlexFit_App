import requests

class ExerciseAPI:
    BASE_URL = "http://127.0.0.1:8000/exercises/"

    @classmethod
    def fetch_exercises(cls):
        try:
            response = requests.get(cls.BASE_URL)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ ERROR: {response.status_code}")
                return []
        except Exception as e:
            print(f"🚨 API Request Failed: {e}")
            return []
