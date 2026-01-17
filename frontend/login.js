const TOKEN_KEY = "dailyOpsToken";
const API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:8000";

function apiUrl(path) {
  return `${API_BASE_URL}${path}`;
}

const form = document.getElementById("login-form");
const emailInput = document.getElementById("login-email");
const passwordInput = document.getElementById("login-password");
const message = document.getElementById("auth-message");

function setMessage(text) {
  message.textContent = text;
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

async function login(email, password) {
  setMessage("Signing in...");
  try {
    const response = await fetch(apiUrl("/auth/login"), {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username: email, password })
    });

    if (!response.ok) {
      throw new Error("Invalid credentials");
    }

    const data = await response.json();
    setToken(data.access_token);
    window.location.href = "profile.html";
  } catch (error) {
    setMessage("Login failed. Check your email and password.");
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  login(emailInput.value.trim(), passwordInput.value);
});
