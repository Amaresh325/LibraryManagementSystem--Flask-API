from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import jwt
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Mock database
books = []
members = []

# Helper function to generate a token
def generate_token(username):
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

# Middleware for authentication
def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Extract token from the 'Authorization' header
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        # Check if the token starts with "Bearer "
        if token.startswith('Bearer '):
            token = token[7:]  # Strip the "Bearer " prefix
        else:
            return jsonify({'message': 'Token format is incorrect!'}), 401

        try:
            # Decode the token with the secret key and HS256 algorithm
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(*args, **kwargs)

    return wrapper


# Books CRUD
@app.route('/books', methods=['GET', 'POST'])
@token_required
def manage_books():
    if request.method == 'POST':
        data = request.json
        book = {
            'id': len(books) + 1,
            'title': data['title'],
            'author': data['author'],
            'year': data['year']
        }
        books.append(book)
        return jsonify({'message': 'Book added successfully!', 'book': book}), 201

    # GET request with optional search and pagination
    search_query = request.args.get('search')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    filtered_books = [book for book in books if
                      search_query.lower() in book['title'].lower() or
                      search_query.lower() in book['author'].lower()] if search_query else books

    start = (page - 1) * per_page
    end = start + per_page

    return jsonify({
        'books': filtered_books[start:end],
        'total': len(filtered_books),
        'page': page,
        'per_page': per_page
    })

@app.route('/books/<int:book_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def handle_book(book_id):
    book = next((book for book in books if book['id'] == book_id), None)
    if not book:
        return jsonify({'message': 'Book not found!'}), 404

    if request.method == 'GET':
        return jsonify(book)

    if request.method == 'PUT':
        data = request.json
        book.update(data)
        return jsonify({'message': 'Book updated successfully!', 'book': book})

    if request.method == 'DELETE':
        books.remove(book)
        return jsonify({'message': 'Book deleted successfully!'})

# Members CRUD
@app.route('/members', methods=['GET', 'POST'])
@token_required
def manage_members():
    if request.method == 'POST':
        data = request.json
        member = {
            'id': len(members) + 1,
            'name': data['name'],
            'email': data['email']
        }
        members.append(member)
        return jsonify({'message': 'Member added successfully!', 'member': member}), 201

    return jsonify({'members': members})

@app.route('/members/<int:member_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def handle_member(member_id):
    member = next((member for member in members if member['id'] == member_id), None)
    if not member:
        return jsonify({'message': 'Member not found!'}), 404

    if request.method == 'GET':
        return jsonify(member)

    if request.method == 'PUT':
        data = request.json
        member.update(data)
        return jsonify({'message': 'Member updated successfully!', 'member': member})

    if request.method == 'DELETE':
        members.remove(member)
        return jsonify({'message': 'Member deleted successfully!'})

# Authentication endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')  # In a real app, validate the password
    if username == 'admin' and password == 'password':
        token = generate_token(username)
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials!'}), 401

if __name__ == '__main__':
    app.run(debug=True)
