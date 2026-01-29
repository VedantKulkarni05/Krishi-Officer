# Krishi Officer - AI-Powered Agricultural Assistant

![Logo](/static/assets/Logo.png)

## Crop & Pest Help Module – AI System

### Purpose
Krishi Officer is a Flask-based web application that leverages **Gemini Vision AI** to help farmers analyze crops and pests. It supports image uploads, chat-style conversations, and persistent chat history, with recommendations tailored for Indian farming conditions.

---

## Features

- 🌾 **AI-Powered Crop Analysis** - Upload crop/pest images for intelligent analysis using Gemini Vision
- 💬 **Chat-based Conversations** - Persistent chat history with UUID-based sessions
- 📊 **Dashboard** - View and manage your analysis history
- 🔍 **Pest Detection** - Identify pests and diseases in crops
- 🌾 **Agricultural Guidance** - Get recommendations tailored for Indian farming conditions

---

## Prerequisites

Before running the project, ensure you have the following installed:

- **Python 3.8+**
- **PostgreSQL** (database)
- **pip** (Python package manager)
- **Gemini API Key** (from [Google AI Studio](https://ai.google.dev))

---

## Project Structure

```
krishi-officer/
├── app.py                     # Flask app entry point
├── routes/
│   ├── __init__.py
│   ├── session_routes.py      # Chat session CRUD (UUID-based)
│   ├── message_routes.py      # Chat messages CRUD
│   └── analyze_routes.py      # Image + Gemini orchestration
├── services/
│   └── gemini_service.py      # Gemini Vision API integration
├── database/
│   ├── db.py                  # PostgreSQL connection (psycopg2)
│   └── schema.sql             # PostgreSQL tables (UUID, SERIAL)
├── uploads/
│   └── crops/                 # Uploaded crop/soil images
├── static/
│   ├── css/
│   │   ├── style.css
│   │   ├── dashboard.css
│   │   └── pest_detection.css
│   ├── js/
│   │   ├── script.js
│   │   ├── dashboard.js
│   │   └── pest_detection.js
│   └── assets/
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   └── pest-detection.html
├── .env                       # Environment variables (ignored in git)
├── .gitignore
└── README.md
```

---

## Setup & Installation

### 1. Fork the Repository

1. Visit the [GitHub repository](https://github.com)
2. Click the **Fork** button in the top-right corner
3. This creates a copy of the repository under your GitHub account

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/krishi-officer.git
cd krishi-officer
```

Replace `YOUR_USERNAME` with your GitHub username.

### 3. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Set Up Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://username:password@localhost:5432/krishi_officer
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
```

**Getting a Gemini API Key:**
1. Go to [Google AI Studio](https://ai.google.dev)
2. Click "Get API Key"
3. Copy your API key and paste it in the `.env` file

### 6. Set Up the Database

```bash
# Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE krishi_officer;"

# Load schema
psql -U postgres -d krishi_officer -f database/schema.sql
```

### 7. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

---

## How to Use

1. **Home Page** - Access the dashboard at `/`
2. **Start a New Chat** - Create a new session for crop/pest analysis
3. **Upload Image** - Upload a crop or pest image for analysis
4. **Get Insights** - Receive AI-powered recommendations and guidance
5. **View History** - Check previous analyses in the dashboard

---

## Contributing

We welcome contributions! Here's how to get started:

### Step 1: Fork the Repository
- Click the **Fork** button on the GitHub repository page

### Step 2: Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names like:
- `feature/add-notification-system`
- `fix/image-upload-bug`
- `docs/improve-readme`

### Step 3: Make Your Changes

- Keep commits small and focused on one feature
- Write clear, descriptive commit messages:
  ```bash
  git commit -m "feat: add multilingual support for farmer guidance"
  ```

### Step 4: Push Your Changes

```bash
git push origin feature/your-feature-name
```

### Step 5: Create a Pull Request

1. Go to your forked repository on GitHub
2. Click **Compare & pull request**
3. Add a clear title and description of your changes
4. Link any related issues if applicable
5. Submit the pull request

