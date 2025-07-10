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

4. Create a `.env` file in the backend directory by copying the example:
   ```
   copy env.example .env  # On Unix: cp env.example .env
   ```

5. Edit the `.env` file to add your OpenAI API key.

6. Run the FastAPI server:
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

## Development Notes

### Environment Variables

The project uses environment variables for configuration. These are stored in `.env` files which are not committed to the repository for security reasons.

- Backend: Copy `backend/env.example` to `backend/.env` and fill in your API keys
- Frontend: Create a `.env.local` file in the frontend directory if needed

### Git Ignore

The `.gitignore` file is set up to exclude:
- Environment files (`.env`, `.env.local`, etc.)
- Python cache and virtual environments
- Node.js modules and build artifacts
- Temporary repository storage
- IDE files and logs

## License

MIT
