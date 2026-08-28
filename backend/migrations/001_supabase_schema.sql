-- ============================================================================
-- VaniPath - Supabase PostgreSQL Schema Migration
-- ============================================================================
-- Run this in: Supabase Dashboard > SQL Editor > New Query
-- Creates all 23 tables for VaniPath Hindi<->Santhali translation platform.
-- ============================================================================

-- Enable UUID generation (Supabase has this by default via extensions)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. USERS
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id          TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    mobile      VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    role        VARCHAR(20) NOT NULL DEFAULT 'teacher'
                CHECK (role IN ('teacher','student','admin','validator')),
    school      VARCHAR(200),
    preferred_language VARCHAR(5) DEFAULT 'hi',
    target_language    VARCHAR(5) DEFAULT 'sat',
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role  ON users(role);

-- ============================================================================
-- 2. STUDENTS
-- ============================================================================
CREATE TABLE IF NOT EXISTS students (
    id          TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    name        VARCHAR(100) NOT NULL,
    grade       INTEGER NOT NULL DEFAULT 1,
    school      VARCHAR(200),
    preferred_language VARCHAR(5) DEFAULT 'sat',
    target_language    VARCHAR(5) DEFAULT 'hi',
    teacher_id  TEXT REFERENCES users(id) ON DELETE SET NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_students_teacher ON students(teacher_id);
CREATE INDEX IF NOT EXISTS idx_students_grade   ON students(grade);

-- ============================================================================
-- 3. TRANSLATIONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations (
    id              TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    source_text     TEXT NOT NULL,
    translated_text TEXT NOT NULL,
    source_language VARCHAR(5) NOT NULL,
    target_language VARCHAR(5) NOT NULL,
    confidence      DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    context_subject VARCHAR(100),
    context_grade   INTEGER,
    context_topic   VARCHAR(200),
    processing_time_ms INTEGER DEFAULT 0,
    requires_validation BOOLEAN DEFAULT FALSE,
    is_validated    BOOLEAN DEFAULT FALSE,
    user_id         TEXT REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_translations_langs ON translations(source_language, target_language);
CREATE INDEX IF NOT EXISTS idx_translations_user   ON translations(user_id);

-- ============================================================================
-- 4. TRANSLATION FEEDBACK
-- ============================================================================
CREATE TABLE IF NOT EXISTS translation_feedback (
    id              TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    translation_id  TEXT NOT NULL REFERENCES translations(id) ON DELETE CASCADE,
    user_id         TEXT REFERENCES users(id) ON DELETE SET NULL,
    is_correct      BOOLEAN,
    corrected_text  TEXT,
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_tf_translation ON translation_feedback(translation_id);

-- ============================================================================
-- 5. CLASSROOM SESSIONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS classroom_sessions (
    id          TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    teacher_id  TEXT REFERENCES users(id) ON DELETE SET NULL,
    grade       INTEGER,
    subject     VARCHAR(100),
    is_active   BOOLEAN DEFAULT TRUE,
    started_at  TIMESTAMPTZ DEFAULT NOW(),
    ended_at    TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_cs_teacher ON classroom_sessions(teacher_id);

-- ============================================================================
-- 6. CLASSROOM MESSAGES
-- ============================================================================
CREATE TABLE IF NOT EXISTS classroom_messages (
    id              TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    session_id      TEXT NOT NULL REFERENCES classroom_sessions(id) ON DELETE CASCADE,
    speaker         VARCHAR(50) NOT NULL,
    source_language VARCHAR(5) NOT NULL,
    target_language VARCHAR(5) NOT NULL,
    source_text     TEXT NOT NULL,
    translated_text TEXT NOT NULL,
    confidence      DOUBLE PRECISION DEFAULT 0.0,
    audio_path      VARCHAR(500),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_cm_session ON classroom_messages(session_id);

-- ============================================================================
-- 7. LESSONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS lessons (
    id               TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    title            VARCHAR(200) NOT NULL,
    description      TEXT,
    grade            INTEGER NOT NULL,
    subject          VARCHAR(100) NOT NULL,
    topic            VARCHAR(200) NOT NULL,
    learning_outcome TEXT,
    content          TEXT,  -- JSON string
    language         VARCHAR(5) DEFAULT 'sat',
    teacher_id       TEXT REFERENCES users(id) ON DELETE SET NULL,
    is_published     BOOLEAN DEFAULT FALSE,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_lessons_teacher ON lessons(teacher_id);
CREATE INDEX IF NOT EXISTS idx_lessons_grade   ON lessons(grade);

-- ============================================================================
-- 8. WORKSHEETS
-- ============================================================================
CREATE TABLE IF NOT EXISTS worksheets (
    id              TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    title           VARCHAR(200),
    grade           INTEGER NOT NULL,
    subject         VARCHAR(100) NOT NULL,
    topic           VARCHAR(200) NOT NULL,
    question_count  INTEGER DEFAULT 10,
    language        VARCHAR(5) DEFAULT 'sat',
    teacher_id      TEXT REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_ws_teacher ON worksheets(teacher_id);

-- ============================================================================
-- 9. WORKSHEET QUESTIONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS worksheet_questions (
    id              TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    worksheet_id    TEXT NOT NULL REFERENCES worksheets(id) ON DELETE CASCADE,
    question_number INTEGER NOT NULL,
    question_type   VARCHAR(50) DEFAULT 'mcq',
    hindi_text      TEXT NOT NULL,
    santhali_text   TEXT NOT NULL,
    options         JSONB,
    correct_answer  TEXT NOT NULL,
    image_url       VARCHAR(500),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_wq_worksheet ON worksheet_questions(worksheet_id);

-- ============================================================================
-- 10. FLASHCARDS
-- ============================================================================
CREATE TABLE IF NOT EXISTS flashcards (
    id              TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    category        VARCHAR(50) NOT NULL,
    hindi           VARCHAR(200) NOT NULL,
    santhali        VARCHAR(200) NOT NULL,
    pronunciation   VARCHAR(300),
    image_url       VARCHAR(500),
    audio_url       VARCHAR(500),
    grade           INTEGER DEFAULT 1,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_fc_category ON flashcards(category);

-- ============================================================================
-- 11. ASSESSMENTS
-- ============================================================================
CREATE TABLE IF NOT EXISTS assessments (
    id               TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    student_id       TEXT REFERENCES students(id) ON DELETE SET NULL,
    subject          VARCHAR(100) NOT NULL,
    topic            VARCHAR(200) NOT NULL,
    grade            INTEGER,
    total_questions  INTEGER DEFAULT 10,
    score            DOUBLE PRECISION DEFAULT 0.0,
    correct_answers  INTEGER DEFAULT 0,
    wrong_answers    INTEGER DEFAULT 0,
    weak_topics      JSONB,
    strong_topics    JSONB,
    status           VARCHAR(20) DEFAULT 'pending'
                     CHECK (status IN ('pending','in_progress','completed')),
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    completed_at     TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_assess_student ON assessments(student_id);

-- ============================================================================
-- 12. ASSESSMENT QUESTIONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS assessment_questions (
    id              TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    assessment_id   TEXT NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    question_number INTEGER NOT NULL,
    question_type   VARCHAR(50) DEFAULT 'mcq',
    hindi_text      TEXT NOT NULL,
    santhali_text   TEXT NOT NULL,
    options         JSONB,
    correct_answer  TEXT NOT NULL,
    student_answer  TEXT,
    is_correct      BOOLEAN,
    topic           VARCHAR(100),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_aq_assessment ON assessment_questions(assessment_id);

-- ============================================================================
-- 13. STUDENT PROGRESS
-- ============================================================================
CREATE TABLE IF NOT EXISTS student_progress (
    id                     TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    student_id             TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    assessment_id          TEXT REFERENCES assessments(id) ON DELETE SET NULL,
    lessons_completed      INTEGER DEFAULT 0,
    assessments_completed  INTEGER DEFAULT 0,
    average_score          DOUBLE PRECISION DEFAULT 0.0,
    learning_streak        INTEGER DEFAULT 0,
    strong_topics          JSONB,
    weak_topics            JSONB,
    badges                 JSONB,
    last_activity_at       TIMESTAMPTZ DEFAULT NOW(),
    created_at             TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sp_student ON student_progress(student_id);

-- ============================================================================
-- 14. RECOMMENDATIONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS recommendations (
    id              TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    student_id      TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    activity_type   VARCHAR(50) NOT NULL,
    title           VARCHAR(200) NOT NULL,
    description     TEXT,
    subject         VARCHAR(100),
    topic           VARCHAR(200),
    reason          TEXT,
    priority        INTEGER DEFAULT 1,
    is_completed    BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_rec_student ON recommendations(student_id);

-- ============================================================================
-- 15. SANTHALI VOCABULARY
-- ============================================================================
CREATE TABLE IF NOT EXISTS santhali_vocabulary (
    id              TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    hindi           VARCHAR(200) NOT NULL,
    santhali        VARCHAR(200) NOT NULL,
    category        VARCHAR(100),
    phonetic        VARCHAR(300),
    usage_example   TEXT,
    is_verified     BOOLEAN DEFAULT FALSE,
    source          VARCHAR(50) DEFAULT 'dictionary',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sv_hindi ON santhali_vocabulary(hindi);
CREATE INDEX IF NOT EXISTS idx_sv_category ON santhali_vocabulary(category);

-- ============================================================================
-- 16. SANTHALI PHRASES
-- ============================================================================
CREATE TABLE IF NOT EXISTS santhali_phrases (
    id              TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    hindi           TEXT NOT NULL,
    santhali        TEXT NOT NULL,
    english         TEXT,
    category        VARCHAR(100),
    audio_path      VARCHAR(500),
    confidence      DOUBLE PRECISION DEFAULT 0.98,
    is_cached       BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sph_category ON santhali_phrases(category);

-- ============================================================================
-- 17. VALIDATION QUEUE
-- ============================================================================
CREATE TABLE IF NOT EXISTS validation_queue (
    id                   TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    hindi                TEXT NOT NULL,
    ai_translation       TEXT NOT NULL,
    corrected_translation TEXT,
    source_language      VARCHAR(5) DEFAULT 'hi',
    target_language      VARCHAR(5) DEFAULT 'sat',
    confidence           DOUBLE PRECISION DEFAULT 0.0,
    status               VARCHAR(20) DEFAULT 'pending'
                         CHECK (status IN ('pending','approved','rejected','edited')),
    validator_id         TEXT REFERENCES users(id) ON DELETE SET NULL,
    notes                TEXT,
    audio_path           VARCHAR(500),
    created_at           TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at          TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_vq_status ON validation_queue(status);

-- ============================================================================
-- 18. LANGUAGE PACKS
-- ============================================================================
CREATE TABLE IF NOT EXISTS language_packs (
    id              TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    version         VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    language_code   VARCHAR(5) NOT NULL DEFAULT 'sat',
    vocabulary_count INTEGER DEFAULT 0,
    phrase_count    INTEGER DEFAULT 0,
    pack_data       JSONB,
    checksum        VARCHAR(64),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 19. CONTENT PACKS
-- ============================================================================
CREATE TABLE IF NOT EXISTS content_packs (
    id              TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    version         VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    content_type    VARCHAR(50) NOT NULL,
    grade           INTEGER,
    pack_data       JSONB,
    checksum        VARCHAR(64),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 20. OFFLINE SYNC
-- ============================================================================
CREATE TABLE IF NOT EXISTS offline_sync (
    id              TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    device_id       VARCHAR(100),
    user_id         TEXT REFERENCES users(id) ON DELETE SET NULL,
    sync_type       VARCHAR(50) NOT NULL,
    data_type       VARCHAR(100) NOT NULL,
    data_payload    JSONB,
    status          VARCHAR(20) DEFAULT 'pending'
                    CHECK (status IN ('pending','synced','failed')),
    version         VARCHAR(20),
    checksum        VARCHAR(64),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    synced_at       TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_os_device ON offline_sync(device_id);
CREATE INDEX IF NOT EXISTS idx_os_status ON offline_sync(status);

-- ============================================================================
-- 21. AUDIO CACHE
-- ============================================================================
CREATE TABLE IF NOT EXISTS audio_cache (
    id              TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    text            TEXT NOT NULL,
    language_code   VARCHAR(5) NOT NULL,
    audio_path      VARCHAR(500) NOT NULL,
    duration_ms     INTEGER,
    file_size_bytes INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_ac_lang ON audio_cache(language_code);
CREATE INDEX IF NOT EXISTS idx_ac_text ON audio_cache(text);

-- ============================================================================
-- 22. SCHOOLS (for future use)
-- ============================================================================
CREATE TABLE IF NOT EXISTS schools (
    id          TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    name        VARCHAR(200) NOT NULL,
    district    VARCHAR(100),
    state       VARCHAR(100) DEFAULT 'Jharkhand',
    block       VARCHAR(100),
    village     VARCHAR(100),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- Row-Level Security (RLS) — enable per table
-- For the prototype, allow all operations. Tighten before production.
-- ============================================================================
ALTER TABLE users                   ENABLE ROW LEVEL SECURITY;
ALTER TABLE students                ENABLE ROW LEVEL SECURITY;
ALTER TABLE translations            ENABLE ROW LEVEL SECURITY;
ALTER TABLE translation_feedback    ENABLE ROW LEVEL SECURITY;
ALTER TABLE classroom_sessions      ENABLE ROW LEVEL SECURITY;
ALTER TABLE classroom_messages      ENABLE ROW LEVEL SECURITY;
ALTER TABLE lessons                 ENABLE ROW LEVEL SECURITY;
ALTER TABLE worksheets              ENABLE ROW LEVEL SECURITY;
ALTER TABLE worksheet_questions     ENABLE ROW LEVEL SECURITY;
ALTER TABLE flashcards              ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessments             ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessment_questions    ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_progress        ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendations         ENABLE ROW LEVEL SECURITY;
ALTER TABLE santhali_vocabulary     ENABLE ROW LEVEL SECURITY;
ALTER TABLE santhali_phrases        ENABLE ROW LEVEL SECURITY;
ALTER TABLE validation_queue        ENABLE ROW LEVEL SECURITY;
ALTER TABLE language_packs          ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_packs           ENABLE ROW LEVEL SECURITY;
ALTER TABLE offline_sync            ENABLE ROW LEVEL SECURITY;
ALTER TABLE audio_cache             ENABLE ROW LEVEL SECURITY;
ALTER TABLE schools                 ENABLE ROW LEVEL SECURITY;

-- Permissive policies for prototype (service_role key bypasses RLS anyway)
DO $$
DECLARE
    tbl TEXT;
    pol_name TEXT;
BEGIN
    FOR tbl IN
        SELECT unnest(ARRAY[
            'users','students','translations','translation_feedback',
            'classroom_sessions','classroom_messages','lessons','worksheets',
            'worksheet_questions','flashcards','assessments','assessment_questions',
            'student_progress','recommendations','santhali_vocabulary','santhali_phrases',
            'validation_queue','language_packs','content_packs','offline_sync',
            'audio_cache','schools'
        ])
    LOOP
        pol_name := tbl || '_prototype_all';
        -- Drop existing policy if present, then create
        EXECUTE format('DROP POLICY IF EXISTS %I ON %I', pol_name, tbl);
        EXECUTE format(
            'CREATE POLICY %I ON %I FOR ALL USING (true) WITH CHECK (true)',
            pol_name, tbl
        );
    END LOOP;
END $$;

-- ============================================================================
-- Done. 23 tables created with indexes, constraints, and permissive RLS.
-- ============================================================================
