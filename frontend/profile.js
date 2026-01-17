const TOKEN_KEY = "dailyOpsToken";
const API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:8000";

function apiUrl(path) {
  return `${API_BASE_URL}${path}`;
}

const statusText = document.getElementById("status-text");
const lastSync = document.getElementById("last-sync");
const jobCount = document.getElementById("job-count");
const accountStatus = document.getElementById("account-status");
const profileGrid = document.getElementById("profile-grid");
const scheduleList = document.getElementById("schedule-list");
const planList = document.getElementById("plan-list");
const signalList = document.getElementById("signal-list");
const dayScheduleLabel = document.getElementById("day-schedule-label");
const dayOverrideEl = document.getElementById("day-override");
const planButton = document.getElementById("btn-plan");
const logoutButton = document.getElementById("btn-logout");
const navLogin = document.getElementById("nav-login");
const profileForm = document.getElementById("profile-form");
const profileMessage = document.getElementById("profile-message");
const profileEdit = document.getElementById("profile-edit");
const profileSave = document.getElementById("profile-save");
const profileActions = document.getElementById("profile-actions");
const profileMessageReadonly = document.getElementById("profile-message-readonly");
const pageLoader = document.getElementById("page-loader");
const profileModal = document.getElementById("profile-modal");
const profileModalClose = document.getElementById("profile-modal-close");

const calendarStrip = document.getElementById("calendar-strip");
const calendarInput = document.getElementById("calendar-input");
const calendarSelected = document.getElementById("calendar-selected");
const loadDayButton = document.getElementById("btn-load-day");
const scheduleDayButton = document.getElementById("btn-schedule-day");
const scheduleModal = document.getElementById("schedule-modal");
const modalClose = document.getElementById("modal-close");
const scheduleForm = document.getElementById("schedule-form");
const modalDateLabel = document.getElementById("modal-date-label");
const modalLastUpdated = document.getElementById("modal-last-updated");
const modalMessage = document.getElementById("modal-message");
const modalShiftType = document.getElementById("modal-shift-type");
const modalShiftStart = document.getElementById("modal-shift-start");
const modalShiftEnd = document.getElementById("modal-shift-end");
const modalGoal = document.getElementById("modal-goal");
const modalDiet = document.getElementById("modal-diet");
const modalNotes = document.getElementById("modal-notes");
const addAppointmentButton = document.getElementById("add-appointment");
const appointmentsList = document.getElementById("appointments-list");

const profileName = document.getElementById("profile-name");
const profilePhone = document.getElementById("profile-phone");
const profileTimezone = document.getElementById("profile-timezone");
const healthHeight = document.getElementById("health-height");
const healthWeight = document.getElementById("health-weight");
const healthTarget = document.getElementById("health-target");
const healthActivity = document.getElementById("health-activity");
const healthExperience = document.getElementById("health-experience");
const healthGoal = document.getElementById("health-goal");
const healthWater = document.getElementById("health-water");

let currentUserData = null;
let selectedDate = new Date();
let currentOverride = null;

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function setStatus(text) {
  statusText.textContent = text;
}

function updateSync() {
  const now = new Date();
  lastSync.textContent = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function setLoading(isLoading) {
  if (!pageLoader) {
    return;
  }
  if (isLoading) {
    pageLoader.classList.remove("hidden");
  } else {
    pageLoader.classList.add("hidden");
  }
}

function toDateInputValue(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function toLocalIso(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const hour = String(date.getHours()).padStart(2, "0");
  const minute = String(date.getMinutes()).padStart(2, "0");
  const second = String(date.getSeconds()).padStart(2, "0");
  return `${year}-${month}-${day}T${hour}:${minute}:${second}`;
}

function buildNowIsoForDate(date) {
  const copy = new Date(date);
  copy.setHours(9, 0, 0, 0);
  return toLocalIso(copy);
}

function setSelectedDate(date) {
  selectedDate = date;
  if (calendarInput) {
    calendarInput.value = toDateInputValue(date);
  }
  if (calendarSelected) {
    const label = date.toLocaleDateString(undefined, { weekday: "long", month: "short", day: "numeric" });
    calendarSelected.textContent = `Selected: ${label}`;
  }
  if (dayScheduleLabel) {
    const label = date.toLocaleDateString(undefined, { weekday: "long", month: "short", day: "numeric" });
    dayScheduleLabel.textContent = `Selected: ${label}`;
  }
  renderCalendar();
}

function appointmentRowTemplate() {
  return `
    <div class="appointment-row">
      <input type="time" class="appt-start" />
      <input type="time" class="appt-end" />
      <input type="text" class="appt-label" placeholder="Appointment details" />
      <button class="btn ghost appt-remove" type="button">Remove</button>
    </div>`;
}

async function openScheduleModal() {
  if (!scheduleModal || !modalDateLabel) {
    return;
  }
  modalDateLabel.textContent = selectedDate.toLocaleDateString(undefined, {
    weekday: "long",
    month: "short",
    day: "numeric"
  });
  if (modalMessage) {
    modalMessage.textContent = "Loading saved schedule...";
  }
  setModalDisabled(true);
  const override = await fetchDayOverride(selectedDate);
  populateModalFromOverride(override);
  setModalDisabled(false);
  if (modalMessage) {
    modalMessage.textContent = override ? "Loaded last saved schedule." : "No saved schedule yet.";
  }
  scheduleModal.classList.remove("hidden");
  scheduleModal.setAttribute("aria-hidden", "false");
}

function closeScheduleModal() {
  if (!scheduleModal) {
    return;
  }
  scheduleModal.classList.add("hidden");
  scheduleModal.setAttribute("aria-hidden", "true");
}

function setModalDisabled(isDisabled) {
  const fields = [
    modalShiftType,
    modalShiftStart,
    modalShiftEnd,
    modalGoal,
    modalDiet,
    modalNotes,
    addAppointmentButton
  ];
  fields.forEach((field) => {
    if (!field) {
      return;
    }
    field.disabled = isDisabled;
  });
  if (scheduleForm) {
    scheduleForm.classList.toggle("is-disabled", isDisabled);
  }
}

function collectAppointments() {
  if (!appointmentsList) {
    return [];
  }
  return Array.from(appointmentsList.querySelectorAll(".appointment-row")).map((row) => ({
    start: row.querySelector(".appt-start")?.value || "",
    end: row.querySelector(".appt-end")?.value || "",
    label: row.querySelector(".appt-label")?.value || ""
  }));
}

async function saveDayConfig() {
  const key = `dailyOpsDayConfig-${toDateInputValue(selectedDate)}`;
  const shiftStart = modalShiftStart?.value || "";
  const shiftEnd = modalShiftEnd?.value || "";
  let shiftType = modalShiftType?.value || "off";

  if (shiftType === "off" && shiftStart && shiftEnd) {
    shiftType = shiftStart > shiftEnd ? "night" : "day";
  }
  const payload = {
    shift_type: shiftType,
    shift_start: shiftStart,
    shift_end: shiftEnd,
    goal: modalGoal?.value || "",
    diet: modalDiet?.value || "",
    notes: modalNotes?.value || "",
    appointments: collectAppointments()
  };
  localStorage.setItem(key, JSON.stringify(payload));
  try {
    await fetchWithAuth(`/day-overrides/${toDateInputValue(selectedDate)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  } catch (error) {
    setStatus("Failed to save day override");
  }
  return payload;
}

function renderCalendar() {
  if (!calendarStrip) {
    return;
  }
  const start = new Date();
  start.setHours(0, 0, 0, 0);
  calendarStrip.innerHTML = Array.from({ length: 7 }).map((_, idx) => {
    const day = new Date(start);
    day.setDate(start.getDate() + idx);
    const label = day.toLocaleDateString(undefined, { weekday: "short" });
    const dateLabel = day.toLocaleDateString(undefined, { month: "short", day: "numeric" });
    const isActive = toDateInputValue(day) === toDateInputValue(selectedDate);
    return `
      <button class="calendar-day ${isActive ? "active" : ""}" data-date="${toDateInputValue(day)}" type="button">
        <span>${label}</span>
        <strong>${dateLabel}</strong>
      </button>`;
  }).join("");

  calendarStrip.querySelectorAll(".calendar-day").forEach((button) => {
    button.addEventListener("click", () => {
      const value = button.getAttribute("data-date");
      if (value) {
        setSelectedDate(new Date(`${value}T09:00:00`));
        loadPlanForDate(selectedDate);
      }
    });
  });
}

function renderProfile(user, profile, context) {
  const items = [
    { label: "Name", value: profile?.name || "--" },
    { label: "Member since", value: user.created_at ? new Date(user.created_at).toLocaleDateString() : "--" },
    { label: "Mail", value: user.email || "--" },
    { label: "Phone", value: profile?.phone || "--" },
    { label: "Timezone", value: profile?.timezone || "--" }
  ];

  profileGrid.innerHTML = items
    .map(
      (item) => `
        <div class="profile-card">
          <div class="label">${item.label}</div>
          <div class="value">${item.value}</div>
        </div>`
    )
    .join("");

  profileName.value = profile?.name || "";
  profilePhone.value = profile?.phone || "";
  profileTimezone.value = profile?.timezone || "";
}

function renderSchedule(actions) {
  const sorted = [...actions].sort((a, b) => {
    const aTime = a.run_at_iso || "";
    const bTime = b.run_at_iso || "";
    return aTime.localeCompare(bTime);
  });

  scheduleList.innerHTML = sorted
    .map(
      (action) => `
        <div class="timeline-item">
          <div class="time">${(action.run_at_iso || "--").slice(11, 16)}</div>
          <div class="title">${action.title || "Untitled"}</div>
          <div class="meta">${action.category || ""} | ${action.priority || ""}</div>
        </div>`
    )
    .join("");
}

function renderPlan(actions) {
  planList.innerHTML = actions
    .map(
      (action) => `
        <div class="timeline-item">
          <div class="time">${action.type || "reminder"}</div>
          <div class="title">${action.title || "Untitled"}</div>
          <div class="meta">${action.message || ""}</div>
        </div>`
    )
    .join("");
}

function renderSignals(signals) {
  const items = Object.entries(signals || {}).map(([key, value]) => ({
    label: key.replace(/_/g, " "),
    value: String(value)
  }));
  signalList.innerHTML = items
    .map(
      (item) => `
        <div class="signal-card">
          <div class="label">${item.label}</div>
          <div class="value">${item.value}</div>
        </div>`
    )
    .join("");
}

async function fetchWithAuth(url, options = {}) {
  const headers = new Headers(options.headers || {});
  const token = getToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  const finalUrl = url.startsWith("http") ? url : apiUrl(url);
  return fetch(finalUrl, { ...options, headers });
}

async function loadProfile() {
  const token = getToken();
  if (!token) {
    window.location.href = "login.html";
    return null;
  }

  setLoading(true);
  setStatus("Loading profile...");
  try {
    const response = await fetchWithAuth("/auth/me");
    if (!response.ok) {
      throw new Error("Session expired");
    }
    const user = await response.json();

    const profileResponse = await fetchWithAuth("/profile/me");
    if (!profileResponse.ok) {
      throw new Error("Profile unavailable");
    }
    const bundle = await profileResponse.json();
    const profile = bundle.profile;
    const health = bundle.health;

    accountStatus.textContent = "Authenticated";
    currentUserData = { user, profile, health };
    return currentUserData;
  } catch (error) {
    clearToken();
    window.location.href = "login.html";
    return null;
  }
}

function renderDayOverride(override) {
  if (!dayOverrideEl) {
    return;
  }
  if (!override) {
    dayOverrideEl.innerHTML = "";
    return;
  }
  const shift = override.shift_type
    ? `${override.shift_type.toUpperCase()} ${override.shift_start || "--"}-${override.shift_end || "--"}`
    : "OFF";
  const appointments = (override.appointments || []).filter((item) => item.label || item.start || item.end);
  const appointmentLines = appointments
    .map((item) => `${item.start || "--"}-${item.end || "--"} ${item.label || ""}`.trim())
    .join(", ");

  dayOverrideEl.innerHTML = `
    <div class="day-override-row">
      <span>Shift</span>
      <strong>${shift}</strong>
    </div>
    <div class="day-override-row">
      <span>Goal</span>
      <strong>${override.goal || "--"}</strong>
    </div>
    <div class="day-override-row">
      <span>Diet</span>
      <strong>${override.diet || "--"}</strong>
    </div>
    <div class="day-override-row">
      <span>Appointments</span>
      <strong>${appointmentLines || "--"}</strong>
    </div>
    <div class="day-override-row">
      <span>Notes</span>
      <strong>${override.notes || "--"}</strong>
    </div>
  `;
}

function setAppointments(items) {
  if (!appointmentsList) {
    return;
  }
  appointmentsList.innerHTML = "";
  (items || []).forEach((item) => {
    appointmentsList.insertAdjacentHTML("beforeend", appointmentRowTemplate());
    const row = appointmentsList.lastElementChild;
    if (!row) {
      return;
    }
    row.querySelector(".appt-start").value = item.start || "";
    row.querySelector(".appt-end").value = item.end || "";
    row.querySelector(".appt-label").value = item.label || "";
  });
}

async function fetchDayOverride(date) {
  const dateKey = toDateInputValue(date);
  try {
    const response = await fetchWithAuth(`/day-overrides/${dateKey}`);
    if (!response.ok) {
      currentOverride = null;
      renderDayOverride(null);
      return null;
    }
    const data = await response.json();
    currentOverride = data;
    renderDayOverride(data);
    return data;
  } catch (error) {
    currentOverride = null;
    renderDayOverride(null);
    return null;
  }
}

function populateModalFromOverride(override) {
  if (!override) {
    if (modalLastUpdated) {
      modalLastUpdated.textContent = "No saved schedule";
    }
    if (modalShiftType) {
      modalShiftType.value = "off";
    }
    if (modalShiftStart) {
      modalShiftStart.value = "";
    }
    if (modalShiftEnd) {
      modalShiftEnd.value = "";
    }
    if (modalGoal) {
      modalGoal.value = "";
    }
    if (modalDiet) {
      modalDiet.value = "";
    }
    if (modalNotes) {
      modalNotes.value = "";
    }
    setAppointments([]);
    if (modalMessage) {
      modalMessage.textContent = "No saved schedule yet.";
    }
    return;
  }

  if (modalShiftType) {
    modalShiftType.value = override.shift_type || "off";
  }
  if (modalShiftStart) {
    modalShiftStart.value = override.shift_start || "";
  }
  if (modalShiftEnd) {
    modalShiftEnd.value = override.shift_end || "";
  }
  if (modalGoal) {
    modalGoal.value = override.goal || "";
  }
  if (modalDiet) {
    modalDiet.value = override.diet || "";
  }
  if (modalNotes) {
    modalNotes.value = override.notes || "";
  }
  setAppointments(override.appointments || []);
  if (modalLastUpdated) {
    const updated = override.updated_at ? new Date(override.updated_at) : null;
    modalLastUpdated.textContent = updated
      ? `Last updated: ${updated.toLocaleString()}`
      : "Saved schedule loaded";
  }
  if (modalMessage) {
    modalMessage.textContent = "Loaded last saved schedule.";
  }
}

async function loadPlanForDate(date) {
  if (!currentUserData) {
    return;
  }

  await fetchDayOverride(date);
  setLoading(true);
  setStatus("Loading selected day...");
  try {
    const nowIso = buildNowIsoForDate(date);
    const response = await fetchWithAuth(`/plan/me?now_iso=${encodeURIComponent(nowIso)}`);
    if (response.status === 429) {
      const data = await response.json().catch(() => ({}));
      setStatus(data.detail || "Plan update limit reached for today.");
      return;
    }
    if (!response.ok) {
      throw new Error("Failed to fetch plan");
    }
    const planData = await response.json();
    renderProfile(currentUserData.user, currentUserData.profile, planData.context);
    renderDayOverride(planData.context?.day_override);
    renderSchedule(planData.actions || []);
    renderPlan(planData.actions || []);
    renderSignals(planData.context?.signals || {});
    accountStatus.textContent = "Authenticated";
    setStatus("Profile loaded");
  } catch (error) {
    setStatus("Planner offline");
  } finally {
    setLoading(false);
  }
}

async function loadJobs() {
  try {
    const response = await fetchWithAuth("/jobs");
    if (!response.ok) {
      throw new Error("Failed to fetch jobs");
    }
    const data = await response.json();
    jobCount.textContent = String((data.jobs || []).length);
  } catch (error) {
    jobCount.textContent = "0";
  }
}

async function runPlannerForDate(date) {
  setStatus("Planning...");
  try {
    const nowIso = buildNowIsoForDate(date);
    const response = await fetchWithAuth(`/plan-and-schedule/me?now_iso=${encodeURIComponent(nowIso)}`, {
      method: "POST"
    });
    if (response.status === 429) {
      const data = await response.json().catch(() => ({}));
      setStatus(data.detail || "Plan update limit reached for today.");
      if (modalMessage) {
        modalMessage.textContent = data.detail || "Limit reached. Try again later.";
      }
      return;
    }
    if (!response.ok) {
      throw new Error("Planner failed");
    }
    const data = await response.json();
    jobCount.textContent = String(data.scheduled_count || 0);
    setStatus(`Scheduled ${data.scheduled_count} jobs`);
    await loadPlanForDate(date);
    await loadJobs();
  } catch (error) {
    setStatus("Planner offline");
  }
}

function buildProfilePayload() {
  return {
    profile: {
      name: profileName.value.trim() || null,
      phone: profilePhone.value.trim() || null,
      timezone: profileTimezone.value.trim() || null
    },
    health: {
      height_cm: healthHeight.value ? Number(healthHeight.value) : null,
      weight_kg: healthWeight.value ? Number(healthWeight.value) : null,
      target_weight_kg: healthTarget.value ? Number(healthTarget.value) : null,
      activity_level: healthActivity.value.trim() || null,
      workout_experience: healthExperience.value.trim() || null,
      dietary_goal: healthGoal.value.trim() || null,
      water_goal_ml: healthWater.value ? Number(healthWater.value) : null
    }
  };
}

function openProfileModal() {
  if (!profileModal) {
    return;
  }
  profileModal.classList.remove("hidden");
  profileModal.setAttribute("aria-hidden", "false");
}

function closeProfileModal() {
  if (!profileModal) {
    return;
  }
  profileModal.classList.add("hidden");
  profileModal.setAttribute("aria-hidden", "true");
}

async function saveProfile(event) {
  event.preventDefault();
  profileMessage.textContent = "Saving profile...";

  try {
    const response = await fetchWithAuth("/profile/me", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(buildProfilePayload())
    });
    if (!response.ok) {
      throw new Error("Failed to save profile");
    }
    const updated = await response.json();
    profileMessage.textContent = "Profile saved.";
    currentUserData = {
      user: currentUserData.user,
      profile: updated.profile,
      health: updated.health
    };
    renderProfile(currentUserData.user, currentUserData.profile, null);
    if (currentUserData.health) {
      healthHeight.value = currentUserData.health.height_cm || "";
      healthWeight.value = currentUserData.health.weight_kg || "";
      healthTarget.value = currentUserData.health.target_weight_kg || "";
      healthActivity.value = currentUserData.health.activity_level || "";
      healthExperience.value = currentUserData.health.workout_experience || "";
      healthGoal.value = currentUserData.health.dietary_goal || "";
      healthWater.value = currentUserData.health.water_goal_ml || "";
    }
    await loadPlanForDate(selectedDate);
    closeProfileModal();
  } catch (error) {
    profileMessage.textContent = "Save failed. Check your inputs.";
  }
}

function logout() {
  clearToken();
  window.location.href = "login.html";
}

function setNavAuthState() {
  const hasToken = Boolean(getToken());
  if (navLogin) {
    navLogin.style.display = hasToken ? "none" : "inline-flex";
  }
}

function applyRevealDelays() {
  document.querySelectorAll(".card").forEach((card) => {
    const delay = card.getAttribute("data-delay") || "0";
    card.style.animationDelay = `${delay}ms`;
  });
}

function initCalendar() {
  const today = new Date();
  setSelectedDate(today);
  fetchDayOverride(today);
  if (calendarInput) {
    calendarInput.value = toDateInputValue(today);
    calendarInput.addEventListener("change", () => {
      const value = calendarInput.value;
      if (value) {
        setSelectedDate(new Date(`${value}T09:00:00`));
        fetchDayOverride(selectedDate);
      }
    });
  }
  if (loadDayButton) {
    loadDayButton.addEventListener("click", () => {
      loadPlanForDate(selectedDate);
    });
  }
  if (scheduleDayButton) {
    scheduleDayButton.addEventListener("click", () => {
      openScheduleModal();
    });
  }
}

function init() {
  applyRevealDelays();
  initCalendar();
  loadProfile().then(() => loadPlanForDate(selectedDate));
  loadJobs();
  updateSync();

  planButton.addEventListener("click", () => runPlannerForDate(selectedDate));
  logoutButton.addEventListener("click", logout);
  profileForm.addEventListener("submit", saveProfile);
  setNavAuthState();
  if (profileEdit) {
    profileEdit.addEventListener("click", () => {
      if (currentUserData) {
        profileName.value = currentUserData.profile?.name || "";
        profilePhone.value = currentUserData.profile?.phone || "";
        profileTimezone.value = currentUserData.profile?.timezone || "";
        if (currentUserData.health) {
          healthHeight.value = currentUserData.health.height_cm || "";
          healthWeight.value = currentUserData.health.weight_kg || "";
          healthTarget.value = currentUserData.health.target_weight_kg || "";
          healthActivity.value = currentUserData.health.activity_level || "";
          healthExperience.value = currentUserData.health.workout_experience || "";
          healthGoal.value = currentUserData.health.dietary_goal || "";
          healthWater.value = currentUserData.health.water_goal_ml || "";
        }
      }
      profileMessage.textContent = "Editing profile.";
      openProfileModal();
    });
  }

  if (modalClose) {
    modalClose.addEventListener("click", closeScheduleModal);
  }
  if (profileModalClose) {
    profileModalClose.addEventListener("click", closeProfileModal);
  }
  if (profileModal) {
    profileModal.addEventListener("click", (event) => {
      if (event.target === profileModal) {
        closeProfileModal();
      }
    });
  }
  if (scheduleModal) {
    scheduleModal.addEventListener("click", (event) => {
      if (event.target === scheduleModal) {
        closeScheduleModal();
      }
    });
  }
  if (addAppointmentButton && appointmentsList) {
    addAppointmentButton.addEventListener("click", () => {
      appointmentsList.insertAdjacentHTML("beforeend", appointmentRowTemplate());
    });
    appointmentsList.addEventListener("click", (event) => {
      const target = event.target;
      if (target && target.classList.contains("appt-remove")) {
        target.closest(".appointment-row")?.remove();
      }
    });
  }
  if (scheduleForm) {
    scheduleForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      await saveDayConfig();
      if (modalMessage) {
        modalMessage.textContent = "Saved. Planning the day...";
      }
      await runPlannerForDate(selectedDate);
      closeScheduleModal();
    });
  }
}

init();
