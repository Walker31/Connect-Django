# Connect-Django

Connect-Django is a backend service built with Django and Django REST Framework, designed to provide user authentication, profile management, and social features. The app supports user registration (including bulk signup), login with JWT authentication, and profile updates, making it suitable for social or matchmaking platforms.

## Features

- User registration with profile creation
- Bulk user signup for onboarding multiple users at once
- JWT-based authentication (using SimpleJWT)
- User login with phone number and password
- Profile update functionality
- Modular structure for easy extension (matches, messaging, posts, etc.)

## Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- (Optional) Docker & Docker Compose

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Connect-Django.git
cd Connect-Django
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py migrate
```

### 5. Run the Development Server

```bash
python manage.py runserver
```

### 6. (Optional) Run with Docker

```bash
docker-compose up --build
```

## API Endpoints

### User Endpoints

All endpoints are prefixed as per your Django URL configuration (e.g., `/user/`).

#### 1. Signup

- **URL:** `/user/signup/`
- **Method:** `POST`
- **Body:**
  ```json
  {
    "name": "John Doe",
    "password": "yourpassword",
    "phone_no": "1234567890",
    "age": 25,
    "latitude": 12.34,
    "longitude": 56.78
  }
  ```
- **Response:** Success message or error details.

#### 2. Login

- **URL:** `/user/login/`
- **Method:** `POST`
- **Body:**
  ```json
  {
    "phone_no": "1234567890",
    "password": "yourpassword"
  }
  ```
- **Response:** JWT tokens, profile data, or error.

#### 3. Update Account

- **URL:** `/user/update/`
- **Method:** `PUT`
- **Body:** (Include at least `phone_no`, plus any fields to update)
  ```json
  {
    "phone_no": "1234567890",
    "name": "New Name",
    "age": 26,
    "location": "New Location"
  }
  ```
- **Response:** Success message or error.

#### 4. Bulk Signup

- **URL:** `/user/bulk-signup/`
- **Method:** `POST`
- **Body:** List of user objects
  ```json
  [
    {
      "username": "Alice",
      "password": "alicepass",
      "gender": "F",
      "phone_no": "1111111111",
      "age": 22,
      "latitude": 10.0,
      "longitude": 20.0,
      "interests": ["music", "sports"]
    }
    // ... more users
  ]
  ```
- **Response:** List of created users and errors.

## Project Structure

- `azureservice/` - Azure-related integrations
- `connect_django/` - Main Django project settings and URLs
- `matches/` - Matchmaking features
- `messaging/` - Messaging and chat features
- `post/` - User posts and feeds
- `spotify/` - Spotify integration
- `user/` - User authentication and profile management

## Environment Variables

You may need to set up environment variables for database, secret keys, and third-party integrations. Refer to Django's documentation for best practices.

## License

[MIT](LICENSE) (or your chosen license)
