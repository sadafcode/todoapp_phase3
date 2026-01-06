# TaskMaster - Todo App (Hackathon Phase 2)

A modern, full-stack task management application built with Next.js 14 and FastAPI.

## 🚀 Features

### Phase 3 - AI-Powered Chatbot Interface ✅

- **Natural Language Task Management**: Users can manage tasks using conversational language
- **MCP Server Integration**: Model Context Protocol for standardized AI tool interactions
- **OpenAI Agents SDK**: Advanced AI processing with MCP tool integration
- **Stateless Chat Architecture**: Database-persisted conversation state with scalable design
- **Seamless Integration**: Maintains all Phase II features with enhanced AI capabilities

### Phase 2 - Enhanced Auth Flow & UI Improvements ✅

- **Beautiful Landing Page**: Welcoming homepage with clear navigation to signup/login
- **Auto-Login After Signup**: Users are automatically logged in after successful registration
- **Smart Redirects**: Authenticated users are automatically redirected to tasks from auth pages
- **Enhanced Error Messages**: Clear, actionable error feedback from the backend
- **Improved UI Readability**: Dark text inputs with helpful placeholders
- **Seamless User Experience**: Intuitive flow from landing → signup → tasks

### Core Features (Phase 1)

- **User Authentication**: Secure JWT-based auth with bcrypt password hashing
- **Task Management**: Full CRUD operations for tasks
- **Task Filtering**: Filter by status (all, pending, completed)
- **Task Sorting**: Sort by creation date, title, or update date
- **User Data Isolation**: Users only see their own tasks
- **Responsive Design**: Mobile-friendly interface with Tailwind CSS

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Context API
- **HTTP Client**: Fetch API with custom error handling

### Backend
- **Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: PostgreSQL (Neon)
- **Authentication**: JWT with python-jose
- **Password Hashing**: bcrypt

## 📁 Project Structure

```
todo_phase2/
├── frontend/temp_next_app/
│   └── src/
│       ├── app/                    # Next.js pages
│       │   ├── page.tsx           # Landing page
│       │   ├── login/             # Login page
│       │   ├── signup/            # Signup page
│       │   ├── tasks/             # Tasks page
│       │   └── components/        # UI components
│       ├── context/               # React Context
│       │   └── AuthContext.tsx    # Auth state management
│       └── lib/                   # Utilities
│           ├── api.ts             # API client
│           └── auth.ts            # Token management
├── backend/
│   ├── main.py                    # FastAPI app entry
│   ├── models.py                  # Database models
│   ├── db.py                      # Database connection
│   ├── auth.py                    # JWT verification
│   └── routes/
│       ├── auth.py                # Auth endpoints
│       └── tasks.py               # Task endpoints
└── specs/                         # Project specifications
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL database (or use Neon)

### Backend Setup

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --port 8000
```

Backend runs on: **http://localhost:8000**

### Frontend Setup

```bash
# Navigate to frontend
cd frontend/temp_next_app

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs on: **http://localhost:3000**

### Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=your_postgresql_connection_string
BETTER_AUTH_SECRET=your_secret_key_here
```

## 📝 API Endpoints

### Authentication
- `POST /auth/signup` - Create new user account
- `POST /auth/login` - Login with credentials
- `GET /auth/me` - Get current user info

### Tasks (Authenticated)
- `GET /api/{user_id}/tasks` - List all tasks (with filters)
- `POST /api/{user_id}/tasks` - Create new task
- `GET /api/{user_id}/tasks/{id}` - Get specific task
- `PUT /api/{user_id}/tasks/{id}` - Update task
- `DELETE /api/{user_id}/tasks/{id}` - Delete task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle completion

## 🎯 User Flow

1. **New User**:
   - Lands on homepage
   - Clicks "Get Started"
   - Signs up with email/password (min 8 chars)
   - Automatically logged in
   - Redirected to tasks dashboard

2. **Returning User**:
   - Lands on homepage
   - Clicks "Sign In"
   - Logs in with credentials
   - Redirected to tasks dashboard

3. **Authenticated User**:
   - Visiting `/`, `/login`, or `/signup` automatically redirects to `/tasks`

## 🔒 Security Features

- JWT-based authentication with 7-day expiry
- Bcrypt password hashing (cost factor 12)
- User data isolation at API level
- CORS protection
- Input validation (frontend + backend)

## ✨ Phase 2 Highlights

### Before Phase 2
- ❌ Users had to manually type `/login` or `/signup` in URL
- ❌ Generic Next.js template on homepage
- ❌ Light colored input text (hard to read)
- ❌ Generic error messages

### After Phase 2
- ✅ Beautiful landing page with clear CTAs
- ✅ Auto-login after signup
- ✅ Smart authenticated user redirects
- ✅ Dark, readable input text with placeholders
- ✅ Specific, helpful error messages from backend
- ✅ Improved user experience throughout

## 🧪 Testing

Create a test user:
```
Email: test@example.com
Password: password123
Name: Test User
```

## 📄 License

This project was created for a hackathon submission.

## 👨‍💻 Developer

Built with ❤️ for Hackathon Phase 2

---

**Note**: This is a hackathon project demonstrating full-stack development with modern web technologies.
