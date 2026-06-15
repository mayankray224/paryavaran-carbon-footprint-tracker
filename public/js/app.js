/**
 * Paryavaran - Frontend Controller & SPA Router
 * Manages user state, API calls, dynamic chart drawing, and UI updates.
 */

// Global state
const state = {
  token: localStorage.getItem("token") || null,
  username: null,
  points: 0,
  streak: 0,
  latestLog: null,
  history: [],
  badges: [],
  currentStep: 1,
  activeView: "landing"
};

// Chart instances
let trendsChart = null;
let compositionChart = null;

// DOM Elements
const elements = {
  announcer: document.getElementById("accessibility-announcer"),
  navBar: document.getElementById("nav-bar"),
  userWidget: document.getElementById("nav-user-widget"),
  widgetStreak: document.getElementById("widget-streak"),
  widgetPoints: document.getElementById("widget-points"),
  themeToggle: document.getElementById("btn-theme-toggle"),
  themeIcon: document.getElementById("theme-icon"),
  logoutBtn: document.getElementById("btn-logout"),
  logoLink: document.getElementById("logo-link"),
  
  // Views
  viewLanding: document.getElementById("view-landing"),
  viewDashboard: document.getElementById("view-dashboard"),
  viewCalculator: document.getElementById("view-calculator"),
  viewTracker: document.getElementById("view-tracker"),
  viewAnalytics: document.getElementById("view-analytics"),
  viewBadges: document.getElementById("view-badges"),
  
  // Auth Form Elements
  tabLogin: document.getElementById("tab-login"),
  tabRegister: document.getElementById("tab-register"),
  formLogin: document.getElementById("form-login"),
  formRegister: document.getElementById("form-register"),
  loginError: document.getElementById("login-error"),
  registerError: document.getElementById("register-error"),
  loginUsernameInput: document.getElementById("login-username"),
  
  // Dashboard Elements
  dashUsername: document.getElementById("dash-username"),
  dashFootprintVal: document.getElementById("dash-footprint-val"),
  dashFootprintTarget: document.getElementById("dash-footprint-target-comparison"),
  dashPointsVal: document.getElementById("dash-points-val"),
  dashStreakVal: document.getElementById("dash-streak-val"),
  dashStreakSub: document.getElementById("dash-streak-sub"),
  dashInsightsList: document.getElementById("dashboard-insights-list"),
  dashBadgesSnapshot: document.getElementById("dashboard-badges-snapshot"),
  btnQuickCalc: document.getElementById("btn-quick-calc"),
  btnViewAllBadges: document.getElementById("btn-view-all-badges"),
  
  // Calculator Wizard Elements
  formCalculator: document.getElementById("form-calculator"),
  btnCalcPrev: document.getElementById("btn-calc-prev"),
  btnCalcNext: document.getElementById("btn-calc-next"),
  btnCalcSubmit: document.getElementById("btn-calc-submit"),
  calcResultCard: document.getElementById("calculator-result-card"),
  resPoints: document.getElementById("result-points-earned"),
  resTotal: document.getElementById("result-total-emissions"),
  resTransport: document.getElementById("result-transport-emissions"),
  resElectricity: document.getElementById("result-electricity-emissions"),
  resFood: document.getElementById("result-food-emissions"),
  resWater: document.getElementById("result-water-emissions"),
  resWaste: document.getElementById("result-waste-emissions"),
  resBadges: document.getElementById("result-badges-unlocked"),
  btnResultClose: document.getElementById("btn-result-close"),
  
  // Action Tracker Elements
  actionContainer: document.getElementById("action-list-container"),
  habitHistoryContainer: document.getElementById("habit-history-container"),
  
  // Analytics Table Elements
  tableUserEmissions: document.getElementById("table-user-emissions"),
  tableUserComp: document.getElementById("table-user-comp"),
  tableUserAnnual: document.getElementById("table-user-annual"),
  tableUserAnnualComp: document.getElementById("table-user-annual-comp")
};

// --- INITIALIZATION ---
document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  loadSavedTheme();
  
  if (state.token) {
    authenticateSession();
  } else {
    navigateTo("landing");
  }
});

// --- HELPER FUNCTIONS ---
function announce(message) {
  elements.announcer.textContent = message;
}

function getHeaders() {
  const headers = {
    "Content-Type": "application/json"
  };
  if (state.token) {
    headers["Authorization"] = `Bearer ${state.token}`;
  }
  return headers;
}

// Set saved or system theme
function loadSavedTheme() {
  const savedTheme = localStorage.getItem("theme") || "light";
  document.body.setAttribute("data-theme", savedTheme);
  updateThemeIcon(savedTheme);
}

function updateThemeIcon(theme) {
  if (theme === "dark") {
    elements.themeIcon.innerHTML = `<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="currentColor"/>`;
  } else {
    elements.themeIcon.innerHTML = `<path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m0-12.728l.707.707m11.314 11.314l.707.707M12 7a5 5 0 1 0 0 10 5 5 0 0 0 0-10z" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/>`;
  }
}

// --- ROUTER (SPA VIEW SWITCHING) ---
function navigateTo(viewId) {
  state.activeView = viewId;
  
  // Hide all views
  const views = [elements.viewLanding, elements.viewDashboard, elements.viewCalculator, elements.viewTracker, elements.viewAnalytics, elements.viewBadges];
  views.forEach(view => view.classList.remove("active"));
  
  // Show active view
  const activeViewEl = document.getElementById(`view-${viewId}`);
  if (activeViewEl) {
    activeViewEl.classList.add("active");
  }
  
  // Update active nav links
  const navLinks = document.querySelectorAll(".main-nav a");
  navLinks.forEach(link => {
    if (link.getAttribute("data-view") === viewId) {
      link.classList.add("active");
      link.setAttribute("aria-selected", "true");
    } else {
      link.classList.remove("active");
      link.setAttribute("aria-selected", "false");
    }
  });

  // Shift focus for keyboard/screen-readers
  const mainEl = document.getElementById("main-content");
  mainEl.focus();

  // Announce view change
  announce(`Loaded ${viewId.charAt(0).toUpperCase() + viewId.slice(1)} view.`);

  // Load view-specific actions
  if (viewId === "dashboard") {
    loadDashboardSummary();
  } else if (viewId === "analytics") {
    loadAnalyticsView();
  } else if (viewId === "badges") {
    loadBadgesView();
  } else if (viewId === "tracker") {
    loadTrackerView();
  } else if (viewId === "calculator") {
    resetCalculatorWizard();
  }
}

// --- EVENT LISTENERS ---
function setupEventListeners() {
  // Logo link
  elements.logoLink.addEventListener("click", (e) => {
    e.preventDefault();
    if (state.token) navigateTo("dashboard");
    else navigateTo("landing");
  });

  // Nav link buttons
  document.querySelectorAll(".main-nav a").forEach(link => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const view = link.getAttribute("data-view");
      navigateTo(view);
    });
  });

  // Auth toggle tabs
  elements.tabLogin.addEventListener("click", () => {
    elements.tabLogin.classList.add("active");
    elements.tabLogin.setAttribute("aria-selected", "true");
    elements.tabRegister.classList.remove("active");
    elements.tabRegister.setAttribute("aria-selected", "false");
    elements.formLogin.style.display = "block";
    elements.formRegister.style.display = "none";
  });

  elements.tabRegister.addEventListener("click", () => {
    elements.tabRegister.classList.add("active");
    elements.tabRegister.setAttribute("aria-selected", "true");
    elements.tabLogin.classList.remove("active");
    elements.tabLogin.setAttribute("aria-selected", "false");
    elements.formRegister.style.display = "block";
    elements.formLogin.style.display = "none";
  });

  // Auth form submissions
  elements.formLogin.addEventListener("submit", handleLogin);
  elements.formRegister.addEventListener("submit", handleRegister);
  elements.logoutBtn.addEventListener("click", handleLogout);

  // Theme switcher
  elements.themeToggle.addEventListener("click", () => {
    const currentTheme = document.body.getAttribute("data-theme") || "light";
    const newTheme = currentTheme === "light" ? "dark" : "light";
    document.body.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);
    updateThemeIcon(newTheme);
    announce(`Switched to ${newTheme} theme.`);
  });

  // Dashboard shortcut buttons
  elements.btnQuickCalc.addEventListener("click", () => navigateTo("calculator"));
  elements.btnViewAllBadges.addEventListener("click", () => navigateTo("badges"));

  // Calculator wizard buttons
  elements.btnCalcPrev.addEventListener("click", () => navigateCalculatorStep(-1));
  elements.btnCalcNext.addEventListener("click", () => navigateCalculatorStep(1));
  elements.formCalculator.addEventListener("submit", handleCalculatorSubmit);
  elements.btnResultClose.addEventListener("click", () => {
    elements.calcResultCard.style.display = "none";
    elements.formCalculator.style.display = "block";
    navigateTo("dashboard");
  });

  // Action Tracker Log buttons
  elements.actionContainer.addEventListener("click", (e) => {
    if (e.target.classList.contains("btn-log-action")) {
      const action = e.target.getAttribute("data-action");
      logSustainableAction(action, e.target);
    }
  });
}

// --- AUTHENTICATION FLOWS ---
async function authenticateSession() {
  try {
    const res = await fetch("/api/dashboard/summary", {
      method: "GET",
      headers: getHeaders()
    });
    if (res.ok) {
      const data = await res.json();
      state.username = data.username;
      state.points = data.green_points;
      state.streak = data.streak_count;
      
      updateNavWidget(true);
      navigateTo("dashboard");
    } else {
      handleLogout();
    }
  } catch (error) {
    console.error("Auth validation failed:", error);
    handleLogout();
  }
}

async function handleLogin(e) {
  e.preventDefault();
  elements.loginError.style.display = "none";
  const username = document.getElementById("login-username").value;
  const password = document.getElementById("login-password").value;

  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    if (res.ok) {
      state.token = data.access_token;
      localStorage.setItem("token", state.token);
      await authenticateSession();
    } else {
      elements.loginError.textContent = data.detail || "Authentication failed.";
      elements.loginError.style.display = "block";
      announce("Error: " + (data.detail || "Authentication failed."));
    }
  } catch (err) {
    elements.loginError.textContent = "Unable to reach server. Please try again later.";
    elements.loginError.style.display = "block";
  }
}

async function handleRegister(e) {
  e.preventDefault();
  elements.registerError.style.display = "none";
  const username = document.getElementById("register-username").value;
  const password = document.getElementById("register-password").value;

  try {
    const res = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    if (res.ok) {
      state.token = data.access_token;
      localStorage.setItem("token", state.token);
      await authenticateSession();
    } else {
      elements.registerError.textContent = data.detail || "Registration failed.";
      elements.registerError.style.display = "block";
      announce("Error: " + (data.detail || "Registration failed."));
    }
  } catch (err) {
    elements.registerError.textContent = "Unable to reach server. Please try again later.";
    elements.registerError.style.display = "block";
  }
}

function handleLogout() {
  state.token = null;
  state.username = null;
  state.points = 0;
  state.streak = 0;
  localStorage.removeItem("token");
  
  updateNavWidget(false);
  
  // Clear charts
  if (trendsChart) trendsChart.destroy();
  if (compositionChart) compositionChart.destroy();
  
  navigateTo("landing");
}

function updateNavWidget(show) {
  if (show) {
    elements.navBar.style.display = "block";
    elements.userWidget.style.display = "flex";
    elements.widgetStreak.textContent = state.streak;
    elements.widgetPoints.textContent = state.points;
  } else {
    elements.navBar.style.display = "none";
    elements.userWidget.style.display = "none";
  }
}

// --- DASHBOARD LOADER ---
async function loadDashboardSummary() {
  try {
    const res = await fetch("/api/dashboard/summary", {
      method: "GET",
      headers: getHeaders()
    });
    if (!res.ok) {
      if (res.status === 401) { handleLogout(); return; }
      throw new Error("Failed to load metrics");
    }

    const data = await res.json();
    state.username = data.username;
    state.points = data.green_points;
    state.streak = data.streak_count;
    state.latestLog = data.latest_log;
    state.badges = data.badges;
    state.history = data.historical_data;

    // Update Nav Widget
    updateNavWidget(true);

    // Update Card Values
    elements.dashUsername.textContent = state.username;
    elements.dashPointsVal.textContent = state.points;
    elements.dashStreakVal.textContent = state.streak;
    
    // Streaks subtitles
    if (state.streak >= 3) {
      elements.dashStreakSub.textContent = `🔥 Active streak! 1.2x points multiplier active.`;
      elements.dashStreakSub.style.color = "var(--warning)";
    } else {
      elements.dashStreakSub.textContent = `Log active sustainable habits to build streaks.`;
      elements.dashStreakSub.style.color = "var(--text-muted)";
    }

    // Footprint displays
    if (state.latestLog) {
      elements.dashFootprintVal.textContent = state.latestLog.total_emissions.toFixed(1);
      
      const targetComp = data.target_comparison;
      if (targetComp.meets_target) {
        elements.dashFootprintTarget.textContent = `🎉 Below monthly sustainable target by ${Math.abs(targetComp.difference).toFixed(1)} kg CO2!`;
        elements.dashFootprintTarget.style.color = "var(--success)";
      } else {
        elements.dashFootprintTarget.textContent = `⚠️ Exceeds monthly sustainable target by ${targetComp.difference.toFixed(1)} kg CO2.`;
        elements.dashFootprintTarget.style.color = "var(--warning)";
      }
    } else {
      elements.dashFootprintVal.textContent = "0.0";
      elements.dashFootprintTarget.textContent = "Complete a calculation to estimate emissions.";
      elements.dashFootprintTarget.style.color = "var(--text-muted)";
    }

    // Dynamic Insights list rendering
    elements.dashInsightsList.innerHTML = "";
    if (state.latestLog && data.recommendations.length > 0) {
      const fragment = document.createDocumentFragment();
      data.recommendations.forEach(rec => {
        const item = document.createElement("div");
        item.className = `recommendation-item priority-${rec.priority}`;
        item.innerHTML = `
          <div class="recommendation-header">
            <span>${rec.category} (Priority: ${rec.priority})</span>
          </div>
          <p>${rec.tip}</p>
        `;
        fragment.appendChild(item);
      });
      elements.dashInsightsList.appendChild(fragment);
    } else {
      elements.dashInsightsList.innerHTML = `<p>Complete a Carbon Footprint calculation first to receive custom optimization insights.</p>`;
    }

    // Badges Snapshot rendering
    elements.dashBadgesSnapshot.innerHTML = "";
    if (state.badges.length > 0) {
      const activeBadges = state.badges.slice(0, 3);
      const fragment = document.createDocumentFragment();
      activeBadges.forEach(badge => {
        const badgeEl = document.createElement("div");
        badgeEl.className = "nav-streak"; // small pill styled representation
        badgeEl.innerHTML = `🌟 ${badge.split("_").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ")}`;
        fragment.appendChild(badgeEl);
      });
      elements.dashBadgesSnapshot.appendChild(fragment);
    } else {
      elements.dashBadgesSnapshot.innerHTML = `<p>No badges unlocked yet. Complete calculations or log daily actions to earn them.</p>`;
    }

  } catch (err) {
    console.error(err);
  }
}

// --- CALCULATOR WIZARD FLOWS ---
function resetCalculatorWizard() {
  state.currentStep = 1;
  elements.calcResultCard.style.display = "none";
  elements.formCalculator.style.display = "block";
  updateCalculatorStepView();
}

function updateCalculatorStepView() {
  // Toggle visibility of step containers
  for (let i = 1; i <= 3; i++) {
    const stepEl = document.getElementById(`step-${i}`);
    const dotEl = document.getElementById(`dot-step-${i}`);
    
    if (i === state.currentStep) {
      stepEl.classList.add("active");
      dotEl.className = "step-dot active";
      dotEl.setAttribute("aria-selected", "true");
    } else {
      stepEl.classList.remove("active");
      dotEl.setAttribute("aria-selected", "false");
      if (i < state.currentStep) {
        dotEl.className = "step-dot completed";
      } else {
        dotEl.className = "step-dot";
      }
    }
  }

  // Adjust control buttons
  if (state.currentStep === 1) {
    elements.btnCalcPrev.style.visibility = "hidden";
    elements.btnCalcNext.style.display = "inline-flex";
    elements.btnCalcSubmit.style.display = "none";
  } else if (state.currentStep === 2) {
    elements.btnCalcPrev.style.visibility = "visible";
    elements.btnCalcNext.style.display = "inline-flex";
    elements.btnCalcSubmit.style.display = "none";
  } else if (state.currentStep === 3) {
    elements.btnCalcPrev.style.visibility = "visible";
    elements.btnCalcNext.style.display = "none";
    elements.btnCalcSubmit.style.display = "inline-flex";
  }
  
  announce(`Showing calculation step ${state.currentStep} of 3.`);
}

function navigateCalculatorStep(direction) {
  // Validate current step before advancing
  if (direction === 1 && !validateCalculatorStep(state.currentStep)) {
    return;
  }
  
  state.currentStep += direction;
  updateCalculatorStepView();
}

function validateCalculatorStep(step) {
  if (step === 1) {
    const dist = parseFloat(document.getElementById("calc-distance").value);
    if (isNaN(dist) || dist < 0) {
      alert("Please enter a valid non-negative distance.");
      return false;
    }
  } else if (step === 2) {
    const elec = parseFloat(document.getElementById("calc-electricity").value);
    const water = parseFloat(document.getElementById("calc-water").value);
    if (isNaN(elec) || elec < 0 || isNaN(water) || water < 0) {
      alert("Please enter valid non-negative energy and water usage values.");
      return false;
    }
  }
  return true;
}

async function handleCalculatorSubmit(e) {
  e.preventDefault();
  
  const payload = {
    transport_distance: parseFloat(document.getElementById("calc-distance").value) || 0,
    vehicle_type: document.getElementById("calc-vehicle-type").value,
    electricity_kwh: parseFloat(document.getElementById("calc-electricity").value) || 0,
    water_liters: parseFloat(document.getElementById("calc-water").value) || 0,
    diet_type: document.getElementById("calc-diet-type").value,
    diet_days: parseInt(document.getElementById("calc-diet-days").value) || 0,
    waste_kg: parseFloat(document.getElementById("calc-waste").value) || 0,
    recycles_or_composts: document.getElementById("calc-compost").checked
  };

  try {
    const res = await fetch("/api/calculator/calculate", {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(payload)
    });
    
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || "Calculation request failed");
    }

    const data = await res.json();
    
    // Display results in results overlay card
    elements.resPoints.textContent = data.points_earned;
    elements.resTotal.textContent = data.log.total_emissions.toFixed(1);
    elements.resTransport.textContent = data.log.transport_emissions.toFixed(1);
    elements.resElectricity.textContent = data.log.electricity_emissions.toFixed(1);
    elements.resFood.textContent = data.log.food_emissions.toFixed(1);
    elements.resWater.textContent = data.log.water_emissions.toFixed(1);
    elements.resWaste.textContent = data.log.waste_emissions.toFixed(1);

    if (data.new_badges_unlocked && data.new_badges_unlocked.length > 0) {
      const badgesStr = data.new_badges_unlocked
        .map(b => b.split("_").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" "))
        .join(", ");
      elements.resBadges.textContent = `🌟 Badges Unlocked: ${badgesStr}`;
      elements.resBadges.style.display = "block";
    } else {
      elements.resBadges.style.display = "none";
    }

    // Toggle views inside card container
    elements.formCalculator.style.display = "none";
    elements.calcResultCard.style.display = "block";
    announce("Emissions calculated successfully! Review the output.");
  } catch (err) {
    alert("Error: " + err.message);
  }
}

// --- SUSTAINABLE ACTION TRACKER FLOW ---
async function logSustainableAction(actionType, btnEl) {
  btnEl.disabled = true;
  btnEl.textContent = "Logging...";

  try {
    const res = await fetch("/api/tracker/actions", {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ action_type: actionType })
    });

    if (!res.ok) throw new Error("Failed to log action");

    const data = await res.json();
    
    // Announce to screen-readers
    let msg = `Logged action! Earned ${data.points_earned} points. Carbon saved: ${data.emissions_reduced_kg} kg.`;
    if (data.new_badges_unlocked.length > 0) {
      msg += ` Unlocked badge: ${data.new_badges_unlocked.join(", ")}`;
    }
    announce(msg);
    alert(msg);

    // Refresh state and views
    await authenticateSession(); // Updates streaks & points in nav
    loadTrackerView();
  } catch (err) {
    alert("Error: " + err.message);
  } finally {
    btnEl.disabled = false;
    btnEl.textContent = "Log Habit";
  }
}

async function loadTrackerView() {
  try {
    const res = await fetch("/api/tracker/actions", {
      method: "GET",
      headers: getHeaders()
    });
    
    if (!res.ok) throw new Error("Could not load action history");
    const actions = await res.json();

    elements.habitHistoryContainer.innerHTML = "";
    if (actions.length > 0) {
      const fragment = document.createDocumentFragment();
      actions.forEach(a => {
        const item = document.createElement("div");
        item.className = "action-row";
        item.style.padding = "0.75rem";
        
        const friendlyName = a.action_type
          .split("_")
          .map(w => w.charAt(0).toUpperCase() + w.slice(1))
          .join(" ");

        item.innerHTML = `
          <div class="action-info">
            <h4 style="font-size: 0.95rem;">${friendlyName}</h4>
            <p>${new Date(a.logged_date).toLocaleDateString(undefined, {month: 'short', day: 'numeric'})}</p>
          </div>
          <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 0.2rem;">
            <span class="action-badge" style="font-size: 0.75rem;">+${a.points_earned} GP</span>
            <span style="font-size: 0.75rem; color: var(--success); font-weight: 500;">-${a.emissions_reduced.toFixed(1)} kg CO2</span>
          </div>
        `;
        fragment.appendChild(item);
      });
      elements.habitHistoryContainer.appendChild(fragment);
    } else {
      elements.habitHistoryContainer.innerHTML = `<p>No habits logged recently. Check off items on the left side to get started!</p>`;
    }
  } catch (err) {
    console.error(err);
  }
}

// --- BADGES VIEW LOADER ---
async function loadBadgesView() {
  try {
    const res = await fetch("/api/dashboard/summary", {
      method: "GET",
      headers: getHeaders()
    });
    if (!res.ok) throw new Error();
    const data = await res.json();
    
    // Clear locked classes from cards
    const allBadges = ["eco_novice", "carbon_tracker", "commute_champion", "green_chef", "waste_warrior", "earth_guardian"];
    allBadges.forEach(badgeName => {
      const card = document.getElementById(`badge-${badgeName}`);
      if (card) {
        if (data.badges.includes(badgeName)) {
          card.classList.add("unlocked");
          card.setAttribute("aria-label", `${card.querySelector("h4").textContent} (Unlocked)`);
        } else {
          card.classList.remove("unlocked");
          card.setAttribute("aria-label", `${card.querySelector("h4").textContent} (Locked)`);
        }
      }
    });
  } catch (err) {
    console.error("Failed to load badges gallery:", err);
  }
}

// --- ANALYTICS AND PLOTTING FLOW ---
async function loadAnalyticsView() {
  // Re-fetch database stats
  try {
    const res = await fetch("/api/dashboard/summary", {
      method: "GET",
      headers: getHeaders()
    });
    if (!res.ok) throw new Error();
    const data = await res.json();

    state.latestLog = data.latest_log;
    state.history = data.historical_data;

    // Fill target comparison table
    if (state.latestLog) {
      elements.tableUserEmissions.textContent = state.latestLog.total_emissions.toFixed(1);
      elements.tableUserAnnual.textContent = (state.latestLog.total_emissions * 12).toFixed(1);

      const meets = data.target_comparison.meets_target;
      const diff = data.target_comparison.difference;

      if (meets) {
        elements.tableUserComp.textContent = `Within limit (-${Math.abs(diff).toFixed(1)} kg)`;
        elements.tableUserComp.style.color = "var(--success)";
        
        elements.tableUserAnnualComp.textContent = `Within limit (-${Math.abs(diff * 12).toFixed(1)} kg)`;
        elements.tableUserAnnualComp.style.color = "var(--success)";
      } else {
        elements.tableUserComp.textContent = `Exceeds target (+${diff.toFixed(1)} kg)`;
        elements.tableUserComp.style.color = "var(--warning)";

        elements.tableUserAnnualComp.textContent = `Exceeds target (+${(diff * 12).toFixed(1)} kg)`;
        elements.tableUserAnnualComp.style.color = "var(--warning)";
      }
    } else {
      elements.tableUserEmissions.textContent = "0.0";
      elements.tableUserAnnual.textContent = "0.0";
      elements.tableUserComp.textContent = "No data";
      elements.tableUserComp.style.color = "var(--text-muted)";
      elements.tableUserAnnualComp.textContent = "-";
      elements.tableUserAnnualComp.style.color = "var(--text-muted)";
    }

    // Draw Charts (wait for Chart.js to load)
    if (typeof Chart !== "undefined") {
      drawHistoricalTrendsChart();
      drawCategoryBreakdownChart();
    } else {
      console.warn("Chart.js is not loaded yet");
    }

  } catch (err) {
    console.error("Failed to compile analytics:", err);
  }
}

function drawHistoricalTrendsChart() {
  if (trendsChart) {
    trendsChart.destroy();
  }

  const ctx = document.getElementById("chart-trends").getContext("2d");
  if (state.history.length === 0) {
    // Show empty placeholder text
    ctx.font = "16px Outfit";
    ctx.fillStyle = "#888";
    ctx.textAlign = "center";
    ctx.fillText("No calculations recorded to plot history.", ctx.canvas.width / 2, ctx.canvas.height / 2);
    return;
  }

  const labels = state.history.map(item => item.date);
  const totalEmissions = state.history.map(item => item.total_emissions);

  // Styling helper based on dark mode status
  const isDark = document.body.getAttribute("data-theme") === "dark";
  const lineColor = isDark ? "#52b788" : "#2d6a4f";
  const gridColor = isDark ? "#2a332d" : "rgba(45, 106, 79, 0.1)";
  const textColor = isDark ? "#a4b3ab" : "#212529";

  trendsChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        label: "Total Emissions (kg CO2e)",
        data: totalEmissions,
        borderColor: lineColor,
        backgroundColor: "rgba(82, 183, 136, 0.1)",
        borderWidth: 3,
        tension: 0.35,
        fill: true,
        pointBackgroundColor: lineColor
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          grid: { color: gridColor },
          ticks: { color: textColor, font: { family: "Outfit" } }
        },
        y: {
          grid: { color: gridColor },
          ticks: { color: textColor, font: { family: "Outfit" } },
          title: { display: true, text: "kg CO2e", color: textColor, font: { family: "Outfit", weight: "600" } }
        }
      }
    }
  });
}

function drawCategoryBreakdownChart() {
  if (compositionChart) {
    compositionChart.destroy();
  }

  const ctx = document.getElementById("chart-composition").getContext("2d");
  if (!state.latestLog) {
    ctx.font = "16px Outfit";
    ctx.fillStyle = "#888";
    ctx.textAlign = "center";
    ctx.fillText("No calculation recorded yet.", ctx.canvas.width / 2, ctx.canvas.height / 2);
    return;
  }

  const log = state.latestLog;
  const isDark = document.body.getAttribute("data-theme") === "dark";
  const textColor = isDark ? "#a4b3ab" : "#212529";

  compositionChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Transport", "Electricity", "Food", "Water", "Waste"],
      datasets: [{
        data: [
          log.transport_emissions,
          log.electricity_emissions,
          log.food_emissions,
          log.water_emissions,
          log.waste_emissions
        ],
        backgroundColor: [
          "#e07a5f", // Transport - Coral
          "#f2cc8f", // Electricity - Light Yellow
          "#81b29a", // Food - Soft Green
          "#3d5a80", // Water - Deep Blue
          "#f4f1de"  // Waste - Warm White
        ],
        borderWidth: isDark ? 2 : 1,
        borderColor: isDark ? "#171f1a" : "#ffffff"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: { color: textColor, font: { family: "Outfit" } }
        }
      }
    }
  });
}
