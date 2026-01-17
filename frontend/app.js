const mockData = {
  summary: [
    { label: "Shift", value: "Day 09:00-21:00" },
    { label: "Workout", value: "07:15 Strength" },
    { label: "Job Sprint", value: "60 min" },
    { label: "Meals", value: "4 planned" }
  ],
  plan: [
    {
      time: "07:15",
      title: "Workout: Upper body circuit",
      meta: "Priority: High | Category: workout"
    },
    {
      time: "08:00",
      title: "Breakfast: Tofu scramble + oats",
      meta: "Priority: Medium | Category: health"
    },
    {
      time: "12:30",
      title: "Hydration check",
      meta: "Priority: Low | Category: health"
    },
    {
      time: "21:30",
      title: "Job search sprint (60 min)",
      meta: "Priority: High | Category: job_search"
    }
  ],
  jobs: [
    { id: "daily_brief-1-20260117071500", next_run: "2026-01-17T07:15:00" },
    { id: "reminder-2-20260117080000", next_run: "2026-01-17T08:00:00" },
    { id: "reminder-3-20260117123000", next_run: "2026-01-17T12:30:00" }
  ],
  signals: [
    { label: "Slept", value: "6.5 hours" },
    { label: "Breakfast", value: "Not yet" },
    { label: "Job apps", value: "0" },
    { label: "Workout", value: "Pending" }
  ]
};

const API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:8000";
const TOKEN_KEY = "dailyOpsToken";

function apiUrl(path) {
  return `${API_BASE_URL}${path}`;
}

const statusText = document.getElementById("status-text");
const lastSync = document.getElementById("last-sync");
const jobCount = document.getElementById("job-count");
const navLogin = document.getElementById("nav-login");
const navLogout = document.getElementById("nav-logout");

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setNavAuthState() {
  const hasToken = Boolean(getToken());
  if (navLogin) {
    navLogin.style.display = hasToken ? "none" : "inline-flex";
  }
  if (navLogout) {
    navLogout.style.display = hasToken ? "inline-flex" : "none";
  }
}

function renderSummary(items) {
  const container = document.getElementById("summary-grid");
  container.innerHTML = items
    .map(
      (item) => `
        <div class="metric">
          <div class="label">${item.label}</div>
          <div class="value">${item.value}</div>
        </div>`
    )
    .join("");
}

function renderPlan(items) {
  const container = document.getElementById("plan-list");
  container.innerHTML = items
    .map(
      (item) => `
        <div class="timeline-item">
          <div class="time">${item.time}</div>
          <div class="title">${item.title}</div>
          <div class="meta">${item.meta}</div>
        </div>`
    )
    .join("");
}

function renderJobs(items) {
  const container = document.getElementById("job-list");
  container.innerHTML = items
    .map(
      (item) => `
        <div class="job-card">
          <div>${item.id}</div>
          <div class="mono">${item.next_run}</div>
        </div>`
    )
    .join("");

  jobCount.textContent = String(items.length);
}

function renderSignals(items) {
  const container = document.getElementById("signal-list");
  container.innerHTML = items
    .map(
      (item) => `
        <div class="signal-card">
          <div class="label">${item.label}</div>
          <div class="value">${item.value}</div>
        </div>`
    )
    .join("");
}

function setStatus(text) {
  statusText.textContent = text;
}

function updateSync() {
  const now = new Date();
  lastSync.textContent = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function applyRevealDelays() {
  document.querySelectorAll(".card").forEach((card) => {
    const delay = card.getAttribute("data-delay") || "0";
    card.style.animationDelay = `${delay}ms`;
  });
}

async function refreshJobs() {
  setStatus("Syncing jobs...");
  try {
    const response = await fetch(apiUrl("/jobs"));
    if (!response.ok) {
      throw new Error("Failed to fetch jobs");
    }
    const data = await response.json();
    renderJobs(data.jobs || []);
    setStatus("Jobs updated");
  } catch (error) {
    setStatus("Offline (showing mock data)");
    renderJobs(mockData.jobs);
  } finally {
    updateSync();
  }
}

async function planAndSchedule() {
  setStatus("Planning...");
  try {
    const response = await fetch(apiUrl("/plan-and-schedule/samara"), { method: "POST" });
    if (response.status === 429) {
      const data = await response.json().catch(() => ({}));
      setStatus(data.detail || "Plan update limit reached for today.");
      return;
    }
    if (!response.ok) {
      throw new Error("Plan request failed");
    }
    const data = await response.json();
    renderJobs(data.next_jobs || []);
    setStatus(`Scheduled ${data.scheduled_count} jobs`);
  } catch (error) {
    setStatus("Planner offline (mock mode)");
  } finally {
    updateSync();
  }
}

function init() {
  renderSummary(mockData.summary);
  renderPlan(mockData.plan);
  renderJobs(mockData.jobs);
  renderSignals(mockData.signals);
  updateSync();
  applyRevealDelays();
  setNavAuthState();
  document.getElementById("btn-refresh").addEventListener("click", refreshJobs);
  document.getElementById("btn-plan").addEventListener("click", planAndSchedule);
  if (navLogout) {
    navLogout.addEventListener("click", () => {
      localStorage.removeItem(TOKEN_KEY);
      setNavAuthState();
    });
  }
}

init();
