from klasy_api_obsluga.APIClient import APIClient

class GoldPrices:
    def __init__(self, client: APIClient):
        self.client = client

    def get_current_price(self):
        """Aktualna cena złota w PLN/g"""
        url = f"{self.client.base_url}/cenyzlota/"
        data = self.client.get_json(url, {"format": "json"})
        if data and len(data) > 0:
            return data[0]["cena"]
        return None
    
    def update(self):
        """Aktualizuje aktualną cenę złota w self.gold_price"""
        url = f"{self.client.base_url}/cenyzlota/"
        data = self.client.get_json(url, {"format": "json"})
        if data and len(data) > 0:
            self.gold_price = data[0]["cena"]
        else:
            self.gold_price = None
        return self.gold_price