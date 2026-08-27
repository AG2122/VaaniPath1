# VaniPath Backend

AI-assisted real-time translation and curriculum-generation platform for mother-tongue-based primary education.

**Smart India Hackathon Problem Statement:** SIH26042  
**Target:** Hindi-speaking teachers teaching primary-school students who speak Santhali  
**Translation Pair:** Hindi ↔ Santhali (the only pair in this prototype)

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy environment file
cp .env.example .env

# 3. Seed the database
python -m app.database.seed

# 4. Start the server
uvicorn app.main:app --reload
```

**API Docs:** http://localhost:8000/docs  
**ReDoc:** http://localhost:8000/redoc

## Demo Credentials

| Role      | Email                   | Password    |
|-----------|-------------------------|-------------|
| Teacher   | teacher@vanipath.in     | teacher123  |
| Validator | validator@vanipath.in   | validator123|
| Admin     | admin@vanipath.in       | admin123    |

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Translation
- `POST /api/translation/text` - Translate text (Hindi ↔ Santhali)

### Speech
- `POST /api/speech/translate` - Voice translation (STT → Translate → TTS)
- `POST /api/speech/stt` - Speech to text
- `POST /api/speech/tts` - Text to speech

### Classroom
- `POST /api/classroom/teacher-to-student` - Hindi → Santhali
- `POST /api/classroom/student-to-teacher` - Santhali → Hindi
- `GET /api/classroom/phrases` - Common phrases
- `GET /api/classroom/{session_id}/history` - Session history

### AI Teacher Copilot
- `POST /api/copilot/lesson` - Generate bilingual lesson plan

### Worksheets
- `POST /api/worksheets/generate` - Generate bilingual worksheet
- `GET /api/worksheets/{id}` - Get worksheet

### Flashcards
- `POST /api/flashcards/generate` - Generate flashcards
- `GET /api/flashcards/categories` - Get categories

### Assessment
- `POST /api/assessment/generate` - Generate adaptive assessment
- `POST /api/assessment/submit` - Submit answers
- `GET /api/assessment/{id}` - Get assessment

### Students
- `POST /api/students/` - Create student
- `GET /api/students/` - List students
- `GET /api/students/{id}/progress` - Student progress
- `GET /api/students/{id}/recommendations` - Recommendations

### Validation
- `GET /api/validation/pending` - Pending validations
- `POST /api/validation/submit` - Submit for validation
- `POST /api/validation/{id}/approve` - Approve
- `POST /api/validation/{id}/reject` - Reject

### Language Learning
- `GET /api/language-learning/phrases` - Learning phrases
- `POST /api/language-learning/practice` - Practice
- `GET /api/language-learning/progress` - Progress

### Offline
- `GET /api/offline/sync-manifest` - Sync manifest
- `GET /api/offline/language-pack` - Download language pack
- `GET /api/offline/content-pack` - Download content
- `POST /api/offline/sync` - Synchronize data

### Dashboard
- `GET /api/dashboard/teacher` - Teacher dashboard

## Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── api/                 # API routes (13 modules)
│   ├── models/              # SQLAlchemy models (10 tables)
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic (9 services)
│   ├── ai/                  # Translation engine & NLP
│   ├── database/            # DB setup & seed
│   └── utils/               # Security, cache, audio
├── data/                    # Language data & curriculum
│   ├── languages/santhali/  # Vocabulary, phrases, FLN terms
│   └── curriculum/          # Grade 1 & 2 curriculum
├── tests/                   # Integration tests
├── requirements.txt
├── Dockerfile
└── .env.example
```

## Translation Pipeline

```
INPUT → Language validation → Text normalization
→ Educational context detection → FLN terminology lookup
→ Santhali vocabulary lookup → Translation
→ Context correction → Validation correction lookup
→ Confidence calculation → OUTPUT
```

## Key Features

1. **Hindi ↔ Santhali Translation** - Dictionary-based with FLN terminology
2. **Voice Translation** - STT → Translation → TTS pipeline
3. **AI Teacher Copilot** - Culturally relevant lesson generation
4. **Bilingual Worksheets** - Multiple question types
5. **Flashcards** - 7 categories, bilingual with pronunciation
6. **Adaptive Assessment** - TEACH → PRACTICE → ASSESS → ADAPT cycle
7. **Community Validation** - Human-in-the-loop quality control
8. **Offline-First** - Language packs for no-internet schools
9. **Confidence Scoring** - Every translation scored (HIGH/MEDIUM/LOW)

## Offline Support

The backend generates downloadable language packs containing:
- Santhali vocabulary (100+ words)
- FLN terminology
- Classroom phrases (20+ common phrases)
- Cached translations
- Curriculum content
- Worksheets and flashcards

## Database

SQLite for prototype. PostgreSQL-compatible schema for production.

Tables: users, students, translations, translation_feedback, classroom_sessions, classroom_messages, lessons, worksheets, worksheet_questions, flashcards, assessments, assessment_questions, student_progress, recommendations, validation_queue, santhali_vocabulary, santhali_phrases, language_packs, content_packs, offline_sync, audio_cache

## Docker

```bash
docker build -t vanipath-backend .
docker run -p 8000:8000 vanipath-backend
```
