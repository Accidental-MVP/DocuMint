# DocuMint

AI-powered README generator for GitHub repositories. Paste a GitHub link, get a beautiful README.

## Features

- Generate comprehensive READMEs from GitHub repositories
- Multiple tone options (professional, startup, meme)
- Analyze repository structure and extract key information
- Handle large repositories with advanced chunking system
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
│   │   │   ├── chunker.py  # File chunking system
│   │   │   ├── reader.py   # Context-aware code reader
│   │   │   ├── parser.py   # Repository parser
│   │   │   └── llm.py      # LLM interface
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

3. Create a `.env.local` file in the frontend directory with the following content:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   ```

   This configures the frontend to connect to the backend API. Adjust the URL if your backend is running on a different host or port.

4. Run the development server:
   ```
   npm run dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser to view the application.

## API Endpoints

- `POST /api/generate` - Generate a README for a GitHub repository
- `GET /api/models` - Get available LLM models
- `GET /api/modes` - Get available generation modes
- `GET /api/health` - Health check endpoint

## Advanced Features

### Chunking System

DocuMint uses an advanced chunking system to handle repositories of any size:

1. **File Chunking**: Large files are broken into smaller chunks with overlap for context
2. **Context-Aware Reading**: Each chunk is processed while maintaining context from previous chunks
3. **Repository Understanding**: File summaries are combined to create a comprehensive understanding
4. **Intelligent README Generation**: The final README is generated based on the repository understanding

This approach allows DocuMint to:
- Handle repositories of any size without token limit issues
- Maintain context and understanding across large files
- Generate more accurate and comprehensive READMEs

## Development Notes

### Environment Variables

The project uses environment variables for configuration. These are stored in `.env` files which are not committed to the repository for security reasons.

- Backend: Copy `backend/env.example` to `backend/.env` and fill in your API keys
- Frontend: Create a `.env.local` file in the frontend directory with the API URL as shown above

### Connecting Frontend to Backend

The frontend and backend are designed to work together:

1. The backend should be running on http://localhost:8000 by default
2. The frontend connects to the backend API at the URL specified in NEXT_PUBLIC_API_URL
3. API health checks are performed when the frontend loads to ensure connectivity
4. If the backend is not available, appropriate error messages will be displayed

### Git Ignore

The `.gitignore` file is set up to exclude:
- Environment files (`.env`, `.env.local`, etc.)
- Python cache and virtual environments
- Node.js modules and build artifacts
- Temporary repository storage
- IDE files and logs

## License

MIT
