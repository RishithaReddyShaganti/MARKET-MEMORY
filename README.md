# Market Memory

### Don't just watch stocks. Understand what changed.

Market Memory is a smart, intent-aware watchlist that helps users understand **what meaningfully changed since they last checked the market and what deserves their attention now**.

---

## Problem

Traditional watchlists show prices, percentage changes, news, and alerts, but users still have to figure out:

* What actually changed?
* Was the movement just market noise?
* Is the change company-specific?
* Does it matter to the reason I am watching this stock?
* What evidence supports the insight?

For a user tracking many stocks, checking everything individually creates information overload.

A stock falling 4% does not automatically mean it deserves more attention than a stock falling 2%.

---

## Solution

**Market Memory turns a watchlist from an event-monitoring tool into an attention-management system.**

When a user returns, the system compares the current market state with their last checkpoint and identifies the changes that matter most.

```text
Market Events
      ↓
Change Detection
      ↓
Significance
      ↓
User Relevance
      ↓
Confidence
      ↓
Attention Ranking
      ↓
Explanation + Evidence
```

Instead of showing:

```text
RELIANCE      +2.1%
INFY          -1.8%
TATA MOTORS   -4.3%
```

Market Memory can show:

```text
WHILE YOU WERE AWAY

73 events detected

61 Normal
8 Worth knowing
4 Need attention

TATA MOTORS
-4.3%

HIGH ATTENTION
91/100

Market: +0.2%
Sector: +0.6%
Volume: 3.1× normal

Company-specific divergence detected.
```

---

## Key Features

### 1. Smart Watchlists

Create watchlists, add stocks, and view current market information together with their attention status.

### 2. Watch Intent

Users can specify why they are watching a stock.

Example:

> "I'm watching Tata Motors to track EV growth."

The system remembers this intent and uses it to determine relevance.

### 3. Meaningful Change Detection

The system evaluates:

* Price movement
* Volume anomalies
* Market movement
* Sector movement
* Historical behavior
* Company events
* Fundamental changes
* Relevant information

### 4. Significance Score

Each change receives a transparent `0–100` significance score rather than relying only on percentage movement.

### 5. Signal vs Noise

Market-wide movements can be grouped together while unusual company-specific movements receive higher attention.

### 6. Trace the Change

Users can follow an important change through its supporting context:

```text
Stock Movement
      ↓
Market
      ↓
Sector
      ↓
Volume
      ↓
Company Event
      ↓
Watch Intent
      ↓
Why It Matters
      ↓
Evidence
```

### 7. Evidence-backed Explanations

Important insights show the underlying evidence and data freshness.

### 8. Data Resilience

The system handles:

* Stale data
* Missing data
* Duplicate events
* Conflicting sources
* Market-wide movements
* External API failures

---

## What Makes It Different?

Most watchlists follow:

```text
Event → Alert
```

Market Memory follows:

```text
Event
  ↓
Is it significant?
  ↓
Is it relevant to this user?
  ↓
Is the data trustworthy?
  ↓
Does it deserve attention?
  ↓
Why?
  ↓
Show evidence
```

The core idea is:

> **A watchlist should help investors monitor less, while missing less.**

---

## AI Approach

AI is used for **explanation, not decision-making**.

The significance score is calculated deterministically from market signals.

```text
Market Data
     ↓
Deterministic Engine
     ↓
Significance Score
     ↓
Relevance + Evidence
     ↓
AI Explanation
```

This prevents the LLM from inventing the underlying market signal or deciding what is important without evidence.

Market Memory does not provide buy/sell recommendations or guaranteed predictions.

---

## Architecture

```text
React + TypeScript
        │
        ▼
     FastAPI
        │
 ┌──────┼────────┐
 ▼      ▼        ▼
Watchlist Attention Evidence
Service  Engine    Service
            │
     ┌──────┴──────┐
     ▼             ▼
Change         Relevance
Detection       Engine
     │
     ▼
Significance
 Engine
     │
     ▼
 PostgreSQL
     │
     ▼
   Redis
     │
     ▼
Market / Event / News Providers
```

The project uses a **modular monolith** rather than unnecessary microservices.

---

## Tech Stack

**Frontend**

* React
* TypeScript
* Vite
* Tailwind CSS

**Backend**

* Python
* FastAPI
* Pydantic
* SQLAlchemy

**Database**

* PostgreSQL

**Cache**

* Redis

**AI**

* LLM API for evidence-based explanations

---

## Demo Flow

```text
Create Watchlist
       ↓
Add Stock
       ↓
Set Watch Intent
       ↓
Record Checkpoint
       ↓
Market Events Occur
       ↓
Return to App
       ↓
"While You Were Away"
       ↓
Attention Feed
       ↓
Trace the Change
       ↓
Inspect Evidence
```

The demo focuses on showing how many raw market events can be reduced to a small number of meaningful things worth the user's attention.

---

## Running Locally

### Backend

```bash
cd backend

python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

npm install
npm run dev
```

Configure the required environment variables using:

```text
backend/.env.example
```

---

## Testing

```bash
pytest
```

Tests cover core areas such as:

* Change detection
* Significance scoring
* Relevance
* Event deduplication
* Stale-data handling
* Demo scenarios

---

## Project Goal

Market Memory is built around one simple question:

> **"What meaningfully changed since I last checked, and what deserves my attention?"**

Instead of making investors monitor more information, it helps them **understand less information better**.

### Market Memory

**Don't just watch stocks. Understand what changed.**
