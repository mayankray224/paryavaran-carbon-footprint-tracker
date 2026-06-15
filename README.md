# Paryavaran - Carbon Footprint Tracker

Paryavaran (Sanskrit: *Environment*) is a production-grade, secure, fully accessible, and gamified web platform that helps individuals calculate, track, and reduce their daily carbon footprint through personalized insights and sustainable habits logging.

---

## 🍃 Hackathon Pitch

Climate change is one of the most critical challenges of our time, yet many people feel powerless to address it, thinking their individual actions don't matter. **Paryavaran** bridges the gap between intention and action.

Paryavaran helps individuals realize the compound power of their choices. By providing an **accessible, scientific multi-step calculator**, users can easily estimate their monthly footprint over five key indicators: transportation, energy, food, water, and waste. 

Once calculated, Paryavaran doesn't just display a number; it translates it into **targeted, prioritized optimizations** and compares their score directly against the **Paris Climate Agreement targets** (<2 tonnes/year).

To turn insights into long-term habits, Paryavaran implements an engaging **Gamification engine**:
1. **Green Points (GP)** rewarded for logging calculations and positive eco-habits.
2. **Eco Log Streaks** with point multipliers (1.2x points for streaks of 3+ days) that motivate daily engagement.
3. **Badges Gallery** representing milestones achieved (e.g. *Waste Warrior*, *Green Chef*, *Commute Champion*).

Through simple actions, Paryavaran demonstrates that small daily habits yield massive collective impact.

---

## ✨ Core Features

1. **Carbon Footprint Calculator**:
   - Multi-step guided wizard checking transportation (fuel types), energy (electricity kWh), diet patterns (vegan, vegetarian, meat), water, and waste.
2. **Sustainable Action Tracker**:
   - Log daily green habits (public transit, biking, composting, recycling, unplugging standby) and get rewarded instantly.
3. **Personalized Analytics & Insights**:
   - Visual trend line charts and category composition doughnut charts utilizing **Chart.js**.
   - Direct comparison tables showing how closer the user is to sustainable targets.
4. **Interactive Gamification**:
   - Green points tracking, daily streak maintenance, and custom badge unlocks.
5. **Universal Accessibility (WCAG 2.1 AA Compliant)**:
   - High contrast themes (Light/Dark toggling).
   - Proper HTML5 semantic elements (`header`, `main`, `footer`, `section`).
   - Explicit ARIA landmark labeling, skip-to-content links, keyboard-navigable forms, and reduced motion considerations.
6. **Robust Security Controls**:
   - Password hashing via **bcrypt** and authorization via secure **JWT session tokens**.
   - Input sanitization via **Pydantic** schema models and SQL Injection protection using **SQLAlchemy ORM**.
   - Complete custom error boundaries preventing application trace leaks.

---

## 🛠️ Architecture & Tech Stack

Following **Clean Architecture** and **SOLID** design principles:

* **Backend**:
  - **FastAPI**: Lightweight, asynchronous web framework with automatic docs and schema validation.
  - **SQLAlchemy (ORM)**: Clean repository pattern separating data queries from business services.
  - **Pydantic**: Type-hinting and data schemas validation.
  - **SQLite**: Self-contained, robust file-based database.
* **Frontend**:
  - Single Page Application (SPA) utilizing semantic **HTML5**, modern **Vanilla CSS3**, and **JavaScript (ES6)**.
  - **Chart.js** via CDN for impact visualization.
  - **Lucide Icons** via CDN for lightweight SVG iconography.
* **Testing**:
  - **pytest** with **pytest-cov** targeting 90%+ code coverage.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ installed on your system.

### Installation & Run

1. Clone or navigate to the project directory:
   ```bash
   cd paryavaran-carbon-footprint-tracker
   ```

2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create your local environment file:
   ```bash
   cp .env.example .env
   ```

5. Run the application:
   ```bash
   python run.py
   ```
   Open your browser to [http://localhost:8000](http://localhost:8000) to view the application!

---

## 🧪 Testing and Quality Control

### Running Tests
To execute the automated unit and integration tests:
```bash
pytest
```

### Coverage Report
To verify that code coverage exceeds the 90% target:
```bash
pytest --cov=src tests/
```
