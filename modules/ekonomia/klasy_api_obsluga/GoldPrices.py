from modules.ekonomia.klasy_api_obsluga.APIClient import APIClient

class GoldPrices:
    def __init__(self, client: APIClient):
        self.client = client

    def get_current_price(self):
        """Get current gold price in PLN/oz (troy ounce)"""
        url = f"{self.client.base_url}/cenyzlota/"
        data = self.client.get_json(url, {"format": "json"})
        if data and len(data) > 0:
            # NBP returns price per gram, convert to troy ounce (1 oz = 31.1035 g)
            return round(data[0]["cena"] * 31.1035, 2)
        return None
    
    def update(self):
        """Updates gold price in PLN/oz (troy ounce)"""
        url = f"{self.client.base_url}/cenyzlota/"
        data = self.client.get_json(url, {"format": "json"})
        if data and len(data) > 0:
            # NBP returns price per gram, convert to troy ounce (1 oz = 31.1035 g)
            self.gold_price = round(data[0]["cena"] * 31.1035, 2)
        else:
            self.gold_price = None
        return self.gold_price