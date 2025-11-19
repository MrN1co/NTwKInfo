import requests

class APIClient:
    def __init__(self, base_url="https://api.nbp.pl/api"):
        self.base_url = base_url

    def get_json(self, url, params=None):
        """Wysyła zapytanie GET i zwraca dane JSON"""
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Błąd: {e}")
            return None