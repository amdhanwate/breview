from flask import Flask, request, jsonify, render_template
import psycopg2
import bcrypt 
from database import get_db_connection
from flask_jwt_extended import create_access_token, create_refresh_token, JWTManager, jwt_required
from brewery import getBreweriesBy, getBreweryByID, addNewReview
from datetime import datetime, timedelta

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Change this to a strong, secret key
app.config["JWT_COOKIE_SECURE"] = False
# app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this in your code!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)


# User registration route
@app.route('/api/v1/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    password_confirmation = data.get('password_confirmation')
    full_name = data.get('full_name')

    conn = get_db_connection()
    curr = conn.cursor()

    # Validate data
    if not (username and password and password_confirmation and full_name):
        return jsonify({'error': 'All fields are required'}), 400

    if password != password_confirmation:
        return jsonify({'error': 'Passwords do not match'}), 400

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    hashed_password = hashed_password.decode('utf-8')

    try:
        curr.execute(
            "INSERT INTO users (username, password, full_name) VALUES (%s, %s, %s)",
            (username, hashed_password, full_name),
        )
        conn.commit()     

        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)
        
        return jsonify({
            'status': 'ok',
            'message': 'Registration successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'username': username
        }), 201
    except psycopg2.errors.UniqueViolation as e:
        return jsonify({
            "status": "error",
            "error": 'Username already exists'
        }), 422
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': 'Registration failed'
        }), 500
    finally:
        curr.close()
        conn.close()

@app.route('/api/v1/login', methods=['POST'])
def login():
    conn = get_db_connection()
    curr = conn.cursor()
    
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Fetch user data from the database
        curr.execute("SELECT username, password FROM users WHERE username = %s", (username,))
        user_data = curr.fetchone()

        if user_data:
            saved_password = user_data[1]

            # Verify the hashed password
            if bcrypt.checkpw(password.encode('utf-8'), saved_password.encode('utf-8')):
                # Create access and refresh tokens
                access_token = create_access_token(identity=username)
                refresh_token = create_refresh_token(identity=username)

                return jsonify({
                    'status': 'ok',
                    'access_token': access_token, 
                    'refresh_token': refresh_token,
                    'username': user_data[0]
                }), 200
            else:
                return jsonify({'error': 'Invalid username or password'}), 401
        else:
            return jsonify({'error': 'User not found'}), 404
        
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500
    finally:
        curr.close()
        conn.close()

@jwt_required()
@app.get("/api/v1/breweries")
def searchBreweriesBy():
    params = request.args

    by_type = params.get("by_type")
    by_city = params.get("by_city")
    by_name = params.get("by_name")
    per_page = params.get("per_page") or 5

    result = None
    if by_type:
        result = result = getBreweriesBy("type", by_type, per_page)
    elif by_city:
        result = getBreweriesBy("city", by_city, per_page)
    elif by_name:
        result = getBreweriesBy("name", by_name, per_page)

    if result is not None:
        return jsonify({
            "status": "ok",
            "data": result
        }), 200
        
    else:
        return jsonify({
            "status": "error",
            "error": "Could not fetch breweries"
        }), 500

@jwt_required()
@app.get("/api/v1/breweries/<id>")
def searchBreweryById(id):
    brewery = getBreweryByID(id)

    if brewery is not None:
        return jsonify({
            "status": "ok",
            "data": brewery
        }), 200

    return jsonify({
        "status": "error",
        "message": "Could not find brewery with given id"
    })

@jwt_required()
@app.post("/api/v1/breweries/<id>/review")
def addBreweryReview(id):
    data = request.json
    review_status = addNewReview(id, data["username"], data["review"], data["rating"])

    if review_status is True:
        return jsonify({
            "status": "ok"
        }), 200

    return jsonify({
        "status": "error",
        "message": "Could not add review"
    })

# Views
@app.get("/auth")
def getAuthPageView():
    return render_template("auth.html")

@app.get("/")
def getHomePageView():
    return render_template("home.html")

@app.get("/brewery/<id>")
def getBreweryView(id):
    brewery = getBreweryByID(id)
    return render_template("brewery.html", brewery=brewery)

if __name__ == '__main__':
    app.run(debug=False)
