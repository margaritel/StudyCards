// Базовый URL API
const API = '/api';

// Получить токен из localStorage
function getToken() {
  return localStorage.getItem('token');
}

// Сохранить токен и пользователя
function saveAuth(token, user) {
  localStorage.setItem('token', token);
  localStorage.setItem('user', JSON.stringify(user));
}

// Удалить токен (выход)
function clearAuth() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
}

// Получить текущего пользователя из localStorage
function getCurrentUser() {
  const u = localStorage.getItem('user');
  return u ? JSON.parse(u) : null;
}

// Базовая функция запроса
async function apiRequest(method, url, body = null) {
  const headers = { 'Content-Type': 'application/json' };
  const token = getToken();
  if (token) headers['Authorization'] = 'Bearer ' + token;

  const options = { method, headers };
  if (body) options.body = JSON.stringify(body);

  const res = await fetch(API + url, options);
  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.error || 'Что-то пошло не так');
  }
  return data;
}

// Показать ошибку в элементе
function showError(elementId, message) {
  const el = document.getElementById(elementId);
  if (el) {
    el.innerHTML = `<div class="alert-error">${message}</div>`;
    el.style.display = 'block';
  }
}

// Показать успех в элементе
function showSuccess(elementId, message) {
  const el = document.getElementById(elementId);
  if (el) {
    el.innerHTML = `<div class="alert-success">${message}</div>`;
    el.style.display = 'block';
  }
}

// Скрыть сообщение
function hideMessage(elementId) {
  const el = document.getElementById(elementId);
  if (el) el.style.display = 'none';
}

// Получить CSS класс для предмета
function getSubjectClass(subject) {
  const map = {
    'Математика': 'subject-math',
    'История': 'subject-history',
    'Английский язык': 'subject-english',
    'Биология': 'subject-biology',
    'Химия': 'subject-chemistry',
    'Физика': 'subject-physics',
    'Обществознание': 'subject-social',
  };
  return map[subject] || 'subject-default';
}

// Обновить навбар в зависимости от авторизации
function updateNavbar() {
  const user = getCurrentUser();
  const navAuth = document.getElementById('nav-auth');
  const navUser = document.getElementById('nav-user');

  if (!navAuth || !navUser) return;

  if (user) {
    navAuth.setAttribute('style', 'display:none!important');
    navUser.setAttribute('style', 'display:flex!important');
  } else {
    navAuth.setAttribute('style', 'display:flex!important');
    navUser.setAttribute('style', 'display:none!important');
  }
}

// Склонение слова "карточка"
function cardWord(n) {
  const abs = Math.abs(n) % 100;
  const n1 = abs % 10;
  if (abs > 10 && abs < 20) return n + ' карточек';
  if (n1 > 1 && n1 < 5) return n + ' карточки';
  if (n1 === 1) return n + ' карточка';
  return n + ' карточек';
}

// Выход из аккаунта
function logout() {
  clearAuth();
  window.location.href = 'index.html';
}
