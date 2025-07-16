# DocuMint

AI-powered README generator for GitHub repositories. Paste a GitHub link, get a beautiful README.

## Features

- Generate comprehensive READMEs from GitHub repositories
- Multiple tone options (professional, startup, meme)
- Analyze repository structure and extract key information
- Handle large repositories with advanced chunking system
- User authentication and API key management
- Token usage tracking per user
- Generate additional documentation (coming soon)

## Project Structure

```
documint/
├── frontend/               # Next.js frontend
│   └── src/                # Frontend source code
│       ├── app/            # Next.js App Router
│       │   ├── api-keys/   # API key management
│       │   ├── login/      # Authentication pages
│       │   └── register/   # User registration
│
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI entry point
│   │   ├── api/            # API routes
│   │   ├── services/       # Business logic
│   │   │   ├── auth.py     # Authentication service
│   │   │   └── generate.py # README generation
│   │   ├── routers/        # API routers
│   │   │   └── auth.py     # Auth endpoints
│   │   ├── models/         # Data models
│   │   │   ├── user.py     # User models
│   │   │   └── api_key.py  # API key models
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

5. Edit the `.env` file to add your OpenAI API key and Supabase credentials.

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

3. Create a `.env.local` file with the following variables:
   ```
   BACKEND_URL=http://localhost:8000
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url_here
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here
   NEXTAUTH_SECRET=your_nextauth_secret_here
   NEXTAUTH_URL=http://localhost:3000
   ```

4. Run the development server:
   ```
   npm run dev
   ```

### Supabase Setup

1. Create a Supabase account at [supabase.com](https://supabase.com)

2. Create a new project

3. Set up the following tables in Supabase:

   - **users**:
     ```sql
     CREATE TABLE users (
       id UUID PRIMARY KEY,
       email TEXT UNIQUE NOT NULL,
       username TEXT NOT NULL,
       hashed_password TEXT NOT NULL,
       is_active BOOLEAN DEFAULT TRUE,
       is_superuser BOOLEAN DEFAULT FALSE,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
       updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
     );
     ```

   - **api_keys**:
     ```sql
     CREATE TABLE api_keys (
       id UUID PRIMARY KEY,
       user_id UUID REFERENCES users(id) NOT NULL,
       name TEXT NOT NULL,
       key TEXT UNIQUE NOT NULL,
       is_active BOOLEAN DEFAULT TRUE,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
       last_used_at TIMESTAMP WITH TIME ZONE,
       expires_at TIMESTAMP WITH TIME ZONE
     );
     ```

   - **token_usage**:
     ```sql
     CREATE TABLE token_usage (
       user_id UUID REFERENCES users(id) PRIMARY KEY,
       prompt_tokens BIGINT DEFAULT 0,
       completion_tokens BIGINT DEFAULT 0,
       total_tokens BIGINT DEFAULT 0,
       last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
     );
     ```

4. Enable Google OAuth or other authentication providers in Supabase Auth settings

5. Get your Supabase URL and anon key from the project settings to use in your environment variables

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/token` - Get an access token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/api-keys` - Create a new API key
- `GET /api/auth/api-keys` - List API keys
- `DELETE /api/auth/api-keys/{id}` - Delete an API key

### Generation
- `POST /api/generate` - Generate a README for a GitHub repository
- `POST /api/advanced-generate` - Generate a README using advanced strategies
- `POST /api/stream-generate` - Generate a README with streaming output
- `GET /api/models` - Get available LLM models
- `GET /api/modes` - Get available generation modes
- `GET /api/health` - Health check endpoint

## Authentication

DocuMint uses JWT-based authentication with Supabase. There are two ways to authenticate:

1. **User Authentication**: Users can sign up and log in via the web interface using email/password or OAuth providers like Google and GitHub.

2. **API Keys**: Users can generate API keys to use the API programmatically. API keys can be managed in the API Keys section of the dashboard.

Example API request with an API key:

```http
POST /api/generate
Content-Type: application/json
x-api-key: documint_live_xxxxxxxxxxxxxxxxxxxxxxxxxxx

{
  "repo_url": "https://github.com/username/repo",
  "tone": "professional",
  "model": "gpt-4"
}
```

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

### User Isolation

DocuMint implements user isolation for:
- Token usage tracking per user
- API key management
- Generation history (coming soon)
- User preferences (coming soon)

## Development Notes

### Environment Variables

The project uses environment variables for configuration. These are stored in `.env` files which are not committed to the repository for security reasons.

- Backend: Copy `backend/env.example` to `backend/.env` and fill in your API keys and Supabase credentials
- Frontend: Create a `.env.local` file in the frontend directory with your Supabase and backend URLs

### Git Ignore

The `.gitignore` file is set up to exclude:
- Environment files (`.env`, `.env.local`, etc.)
- Python cache and virtual environments
- Node.js modules and build artifacts
- Temporary repository storage
- IDE files and logs

## License

MIT
