# LibraryManagementSystem--Flask-API

firstly we need to run the login path using
  curl -X POST http://127.0.0.1:5000/login  -H "Content-Type: application/json" -d '{"username": "admin", "password": "password"}'
Now we get a token

then we can run other paths to add book, members
