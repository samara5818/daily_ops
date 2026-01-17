const TOKEN_KEY = "dailyOpsToken";
const API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:8000";

function apiUrl(path) {
  return `${API_BASE_URL}${path}`;
}

const form = document.getElementById("register-form");
const emailInput = document.getElementById("register-email");
const passwordInput = document.getElementById("register-password");
const message = document.getElementById("register-message");

function setMessage(text) {
  message.textContent = text;
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

async function login(email, password) {
  const response = await fetch(apiUrl("/auth/login"), {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username: email, password })
  });

  if (!response.ok) {
    throw new Error("Login failed");
  }

  const data = await response.json();
  setToken(data.access_token);
}

async function register(email, password) {
  setMessage("Creating account...");
  try {
    const response = await fetch(apiUrl("/auth/register"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      const detail = data.detail || "Could not create account.";
      throw new Error(detail);
    }

    await login(email, password);
    window.location.href = "profile.html";
  } catch (error) {
    setMessage(String(error.message || "Registration failed."));
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  register(emailInput.value.trim(), passwordInput.value);
});
