# DocuMint

AI-powered README generator for GitHub repositories. Paste a GitHub link, get a beautiful README.

## Features

- Generate comprehensive READMEs from GitHub repositories
- Multiple tone options (professional, startup, meme)
- Analyze repository structure and extract key information
- Generate additional documentation (coming soon)

## Project Structure

```
documint/
├── frontend/               # Next.js frontend
│   └── src/                # Frontend source code
│
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI entry point
│   │   ├── api/            # API routes
│   │   ├── services/       # Business logic
│   │   ├── utils/          # Utilities
│   │   └── config.py       # Configuration
│   └── requirements.txt    # Python dependencies
│
├── scripts/                # Development scripts
└── docs/                   # Documentation
```

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the backend directory with:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   GITHUB_TEMP_DIR=./temp_repos
   ```

5. Run the FastAPI server:
   ```
   python -m app.main
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Run the development server:
   ```
   npm run dev
   ```

## API Endpoints

- `POST /api/generate` - Generate a README for a GitHub repository
- `GET /api/health` - Health check endpoint

## License

MIT
