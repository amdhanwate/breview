import requests
from database import get_db_connection

# Replace this with the URL of the 3rd party API you want to access
api_url = "https://example.com/api/data"

def fetch_rating_data(brewery_id):
    conn = get_db_connection()
    curr = conn.cursor()

    curr.execute("SELECT avg_rating, review_count FROM rating WHERE brewery_id = %s", (brewery_id,))
    rating_data = curr.fetchone()

    if rating_data:
        return rating_data[0], rating_data[1]
    return None

def fetch_brewery_rating(id: str):
    conn = get_db_connection()
    curr = conn.cursor()

    curr.execute("SELECT avg_rating FROM rating WHERE brewery_id = %s", (id,))
    rating_data = curr.fetchone()

    if rating_data:
        return rating_data[0]
    return None

def fetch_brewery_reviews(id: str):
    conn = get_db_connection()
    curr = conn.cursor()

    curr.execute("SELECT * FROM reviews WHERE brewery_id = %s", (id,))
    reviews_data = curr.fetchall()

    if reviews_data:
        sum = 0
        for review in reviews_data:
            sum += int(review[4])

        return reviews_data
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
                fetch_rating_response = fetch_rating_data(brewery["id"])
                result.append({
                    "id": brewery["id"],
                    "name": brewery["name"],
                    "address": ', '.join(filter(None, (brewery["address_1"], brewery["address_2"],  brewery["address_3"]))),
                    "phone": brewery["phone"] or "Not Available",
                    "website": brewery["website_url"] or "Not Available",
                    "city": brewery["city"],
                    "state": brewery["state"],
                    "rating": fetch_rating_response[0] if fetch_rating_response else None,
                    "review_count": fetch_rating_response[1] if fetch_rating_response else 0
                })

            return result
        else:
            print(f"Request failed with status code {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def getBreweryByID(id):
    API = "https://api.openbrewerydb.org/v1/breweries/" + str(id)
    response = requests.get(API)
    result = None

    if response.status_code == 200:
        data = response.json()
        fetch_review_response = fetch_brewery_reviews(data["id"])
        fetch_rating_response = fetch_rating_data(data["id"])
        result = {
            "id": data["id"],
            "name": data["name"],
            "address": ', '.join(filter(None, (data["address_1"], data["address_2"],  data["address_3"]))),
            "phone": data["phone"] or "Not Available",
            "website": data["website_url"] or "Not Available",
            "city": data["city"],
            "state": data["state_province"],
            "rating": fetch_brewery_rating(data["id"]),
            "brewery_type": data["brewery_type"],
            "postal_code": data["postal_code"],
            "country": data["country"],
            "longitude": data["longitude"],
            "latitude": data["latitude"],
            "reviews": fetch_review_response if fetch_review_response else [],
            "avg_rating": fetch_rating_response[0] if fetch_rating_response else 0,
            "review_count": fetch_rating_response[1] if fetch_rating_response else 0,
        }

        return result

    return None

def addNewReview(brewery_id, username, review, rating):
    conn = get_db_connection()
    curr = conn.cursor()

    updateAvgRating(conn, curr, brewery_id, rating)

    curr.execute("INSERT INTO reviews (brewery_id, username, description, rating) VALUES (%s, %s, %s, %s)", (brewery_id, username, review, rating))
    conn.commit()

    return True

def updateAvgRating(conn, curr, brewery_id, new_rating):
    conn = get_db_connection()
    curr = conn.cursor()

    # check if brewery_id exists
    curr.execute("SELECT avg_rating, review_count FROM rating WHERE brewery_id = %s", (brewery_id,))
    rating_data = curr.fetchone()

    if rating_data:
        old_rating = rating_data[0]
        new_review_count = rating_data[1] + 1
        new_rating = str((float(new_rating) + float(old_rating) * rating_data[1]) / new_review_count)

        curr.execute("UPDATE rating SET avg_rating = %s, review_count = %s  WHERE brewery_id = %s", (new_rating, new_review_count, brewery_id))
    else:
        curr.execute("INSERT INTO rating (brewery_id, avg_rating, review_count) VALUES (%s, %s, %s)", (brewery_id, new_rating, 1))
    conn.commit()

    return True

