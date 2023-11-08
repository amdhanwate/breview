import requests
from database import get_db_connection

# Replace this with the URL of the 3rd party API you want to access
api_url = "https://example.com/api/data"

def fetch_brewery_rating(id: str):
    conn = get_db_connection()
    curr = conn.cursor()

    curr.execute("SELECT avg_rating FROM rating WHERE brewery_id = %s", (id,))
    rating_data = curr.fetchone()

    if rating_data:
        return rating_data[0]
    return None

def getBreweriesBy(by, city, per_page=5):
    arg1 = None
    if by == "city":
        arg1 = "by_city"
    elif by == "type":
        arg1 = "by_type"
    else:
        arg1 = "by_name"

    API = "https://api.openbrewerydb.org/v1/breweries?{0}={1}&per_page={2}".format(arg1, city, per_page)

    try:
        response = requests.get(API)

        result = []

        if response.status_code == 200:
            data = response.json()

            for brewery in data:
                result.append({
                    "id": brewery["id"],
                    "name": brewery["name"],
                    "address": ', '.join(filter(None, (brewery["address_1"], brewery["address_2"],  brewery["address_3"]))),
                    "phone": brewery["phone"],
                    "website": brewery["website_url"],
                    "city": brewery["city"],
                    "state": brewery["state"],
                    "rating": fetch_brewery_rating(brewery["id"])
                })

            return result
        else:
            print(f"Request failed with status code {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None