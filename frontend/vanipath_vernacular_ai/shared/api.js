/**
 * VaniPath Frontend API Client
 * Shared utility for all frontend pages.
 * Talks to the FastAPI backend at VITE_API_BASE_URL or http://localhost:8000/api
 */
const API_BASE = 'http://localhost:8000/api';

// ─── Auth helpers ──────────────────────────────────────
function getToken() {
  return localStorage.getItem('vanipath_token');
}

function setToken(token) {
  localStorage.setItem('vanipath_token', token);
}

function clearToken() {
  localStorage.removeItem('vanipath_token');
  localStorage.removeItem('vanipath_user');
}

function getUser() {
  try {
    return JSON.parse(localStorage.getItem('vanipath_user'));
  } catch {
    return null;
  }
}

function setUser(user) {
  localStorage.setItem('vanipath_user', JSON.stringify(user));
}

// ─── Fetch wrapper ─────────────────────────────────────
async function apiFetch(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const headers = { ...options.headers };

  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Don't set Content-Type for FormData (browser handles multipart)
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(url, { ...options, headers });
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || data.message || `API error ${response.status}`);
  }
  return data;
}

// ─── Auth API ──────────────────────────────────────────
async function apiLogin(email, password) {
  const data = await apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  setToken(data.access_token);
  setUser(data.user);
  return data;
}

async function apiRegister(name, email, password, role = 'teacher', school = '') {
  const data = await apiFetch('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ name, email, password, role, school }),
  });
  setToken(data.access_token);
  setUser(data.user);
  return data;
}

async function apiGetMe() {
  return apiFetch('/auth/me');
}

// ─── Translation API ──────────────────────────────────
async function apiTranslate(text, sourceLang = 'hi', targetLang = 'sat', context = null) {
  const body = { text, source_language: sourceLang, target_language: targetLang };
  if (context) body.context = context;
  return apiFetch('/translation/text', { method: 'POST', body: JSON.stringify(body) });
}

// ─── Speech API ───────────────────────────────────────
async function apiSpeechTranslate(audioFile, sourceLang = 'hi', targetLang = 'sat', grade = null, subject = null) {
  const formData = new FormData();
  formData.append('audio', audioFile);
  formData.append('source_language', sourceLang);
  formData.append('target_language', targetLang);
  if (grade) formData.append('grade', grade);
  if (subject) formData.append('subject', subject);
  return apiFetch('/speech/translate', { method: 'POST', body: formData });
}

async function apiTTS(text, language = 'sat') {
  const formData = new FormData();
  formData.append('text', text);
  formData.append('language', language);
  return apiFetch('/speech/tts', { method: 'POST', body: formData });
}

// ─── Classroom API ────────────────────────────────────
async function apiTeacherToStudent(text, sessionId = null, grade = null, subject = null) {
  const body = { text };
  if (sessionId) body.session_id = sessionId;
  if (grade) body.grade = grade;
  if (subject) body.subject = subject;
  return apiFetch('/classroom/teacher-to-student', { method: 'POST', body: JSON.stringify(body) });
}

async function apiStudentToTeacher(text, sessionId = null, grade = null) {
  const body = { text };
  if (sessionId) body.session_id = sessionId;
  if (grade) body.grade = grade;
  return apiFetch('/classroom/student-to-teacher', { method: 'POST', body: JSON.stringify(body) });
}

async function apiGetClassroomPhrases() {
  return apiFetch('/classroom/phrases');
}

async function apiGetSessionHistory(sessionId) {
  return apiFetch(`/classroom/${sessionId}/history`);
}

// ─── Copilot API ──────────────────────────────────────
async function apiGenerateLesson(grade, subject, topic, learningOutcome = null, language = 'sat') {
  const body = { grade, subject, topic, language };
  if (learningOutcome) body.learning_outcome = learningOutcome;
  return apiFetch('/copilot/lesson', { method: 'POST', body: JSON.stringify(body) });
}

// ─── Worksheets API ───────────────────────────────────
async function apiGenerateWorksheet(grade, subject, topic, questionCount = 10, language = 'sat') {
  return apiFetch('/worksheets/generate', {
    method: 'POST',
    body: JSON.stringify({ grade, subject, topic, question_count: questionCount, language }),
  });
}

async function apiGetWorksheet(worksheetId) {
  return apiFetch(`/worksheets/${worksheetId}`);
}

// ─── Flashcards API ───────────────────────────────────
async function apiGenerateFlashcards(category = 'Animals', count = 6, grade = 1) {
  return apiFetch('/flashcards/generate', {
    method: 'POST',
    body: JSON.stringify({ category, count, grade }),
  });
}

async function apiGetFlashcardCategories() {
  return apiFetch('/flashcards/categories');
}

// ─── Assessment API ───────────────────────────────────
async function apiGenerateAssessment(subject, topic, grade = 2, questionCount = 10) {
  return apiFetch('/assessment/generate', {
    method: 'POST',
    body: JSON.stringify({ subject, topic, grade, question_count: questionCount }),
  });
}

async function apiSubmitAssessment(assessmentId, answers) {
  return apiFetch('/assessment/submit', {
    method: 'POST',
    body: JSON.stringify({ assessment_id: assessmentId, answers }),
  });
}

// ─── Students API ─────────────────────────────────────
async function apiGetStudents() {
  return apiFetch('/students/');
}

async function apiGetStudentProgress(studentId) {
  return apiFetch(`/students/${studentId}/progress`);
}

async function apiGetRecommendations(studentId) {
  return apiFetch(`/students/${studentId}/recommendations`);
}

// ─── Validation API ───────────────────────────────────
async function apiGetPendingValidations() {
  return apiFetch('/validation/pending');
}

async function apiApproveValidation(itemId) {
  return apiFetch(`/validation/${itemId}/approve`, { method: 'POST' });
}

async function apiRejectValidation(itemId) {
  return apiFetch(`/validation/${itemId}/reject`, { method: 'POST' });
}

async function apiSubmitValidation(hindi, aiTranslation, confidence = 0) {
  return apiFetch('/validation/submit', {
    method: 'POST',
    body: JSON.stringify({ hindi, ai_translation: aiTranslation, confidence }),
  });
}

// ─── Language Learning API ────────────────────────────
async function apiGetLearningPhrases() {
  return apiFetch('/language-learning/phrases');
}

async function apiGetLearningProgress() {
  return apiFetch('/language-learning/progress');
}

// ─── Offline API ──────────────────────────────────────
async function apiGetSyncManifest() {
  return apiFetch('/offline/sync-manifest');
}

async function apiGetLanguagePack() {
  return apiFetch('/offline/language-pack');
}

async function apiGetContentPack(contentType = 'all', grade = null) {
  let path = `/offline/content-pack?content_type=${contentType}`;
  if (grade) path += `&grade=${grade}`;
  return apiFetch(path);
}

async function apiSync(data = {}) {
  return apiFetch('/offline/sync', { method: 'POST', body: JSON.stringify(data) });
}

// ─── Dashboard API ────────────────────────────────────
async function apiGetTeacherDashboard() {
  return apiFetch('/dashboard/teacher');
}

async function apiGetDashboardStats() {
  return apiFetch('/dashboard/stats');
}

// ─── Cache API ────────────────────────────────────────
async function apiGetPopularCache() {
  return apiFetch('/cache/popular');
}

// ─── UI Helpers ───────────────────────────────────────
function showLoading(el) {
  if (el) el.innerHTML = '<span class="animate-spin material-symbols-outlined">sync</span> Loading...';
}

function showError(el, msg) {
  if (el) el.innerHTML = `<span class="text-error">${msg}</span>`;
}

function showSuccess(el, msg) {
  if (el) el.innerHTML = `<span class="text-tertiary">${msg}</span>`;
}
