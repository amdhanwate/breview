from flask import Flask, request, jsonify, render_template
import psycopg2
import bcrypt 
from database import get_db_connection
from flask_jwt_extended import create_access_token, create_refresh_token, JWTManager, jwt_required


app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Change this to a strong, secret key
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



# Views
@app.get("/auth")
def getAuthPageView():
    return render_template("auth.html")

if __name__ == '__main__':
    app.run(port=3838, debug=True)
