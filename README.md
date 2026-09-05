# Market Memory

### Don't just watch stocks. Understand what changed.

Market Memory is a smart, intent-aware watchlist that helps users understand **what meaningfully changed since they last checked the market and what deserves their attention now.**

---

## The Problem

Traditional stock watchlists make it easy to monitor many companies, but they mainly show **what is happening now**.

When a user returns after being away, they may have to go through dozens of price movements, volume changes, market movements, and other events to figure out:

* What actually changed?
* Was the movement unusual?
* Was it caused by the broader market or sector?
* Does it matter to the reason I am watching this stock?
* What evidence supports the change?

This creates information overload.

A stock moving 4% does not automatically mean it deserves more attention than a stock moving 2%.

For example, a 4% decline when the entire market is declining may be less unusual than a 2% decline while the market and sector are stable.

The real problem is therefore not the lack of information.

> **The problem is knowing which information deserves attention.**

---

## The Solution

Market Memory turns a traditional watchlist into an **attention-oriented market monitoring system**.

It remembers the user's last checkpoint and evaluates what changed since then.

Instead of treating every market event equally, Market Memory follows a structured process:

**What happened?**

↓

**Was it unusual?**

↓

**How significant is it?**

↓

**Is it relevant to the user's watch intent?**

↓

**How trustworthy is the supporting data?**

↓

**Does it deserve attention?**

↓

**Why does it matter?**

↓

**What evidence supports it?**

The goal is to turn a large stream of market events into a small number of understandable insights.

---

## Core Features

### 1. Smart Watchlists

Users can create and manage watchlists and track stocks along with their current market information and attention status.

---

### 2. Watch Intent

Users can specify **why they are watching a particular stock**.

For example:

> "I'm watching Tata Motors to track EV growth."

Another user could watch the same stock because they are interested in its valuation.

The same market event can therefore have different relevance for different users.

Market Memory uses this intent when evaluating relevance.

### Significance ≠ Relevance

A change can be objectively significant without being particularly relevant to the user's reason for watching the stock.

Market Memory considers both.

---

### 3. While You Were Away

Market Memory remembers the user's last checkpoint.

When the user returns, it looks at what happened since that checkpoint instead of simply showing the latest market state.

For example:

**WHILE YOU WERE AWAY**

**20 stocks watched**

**73 events detected**

**61 Normal**
**8 Worth Knowing**
**4 Need Attention**

This allows the user to quickly understand what they missed without manually reviewing every event.

---

### 4. Meaningful Change Detection

Market Memory does not simply rank stocks by the largest percentage movement.

It evaluates changes in context using signals such as:

* Stock price movement
* Trading volume
* Broader market movement
* Sector movement
* Historical behavior
* Company or event signals
* Relevant information

For example:

**TATA MOTORS**

Stock movement: **-4.3%**

Market movement: **+0.2%**

Sector movement: **+0.6%**

Volume: **3.1× normal**

The important observation is not simply:

> "Tata Motors fell 4.3%."

The system can identify that the stock moved unusually relative to its broader market and sector context while trading activity was elevated.

This helps distinguish **signal from noise**.

---

### 5. Attention Ranking

After detecting meaningful changes, Market Memory considers:

* **Significance** — how unusual or important the change appears.
* **Relevance** — how closely it relates to the user's watch intent.
* **Confidence** — how trustworthy and complete the supporting information is.

These factors contribute to an attention score.

For example:

**TATA MOTORS**

**HIGH ATTENTION**

Significance: **91**

Relevance: **86**

Attention Score: **90/100**

Confidence: **94%**

This helps the user answer:

> **"What should I look at first?"**

---

### 6. Trace the Change

Finding an important change is only the beginning.

Market Memory provides a **Trace the Change** experience that helps users understand the context behind an insight.

The investigation can include:

**Market Context**

↓

**Sector Context**

↓

**Stock Movement**

↓

**Trading Activity**

↓

**Company or Event Signal**

↓

**Why This Matters**

↓

**Supporting Evidence**

This makes the system more transparent than presenting an unexplained alert.

The application does not automatically claim that an event caused a price movement. It presents observed signals and relevant evidence instead.

---

### 7. Evidence and Trust

Important insights can be connected to supporting evidence.

Evidence can include:

* Market observations
* Price and volume information
* Sector context
* Company or event information
* Relevant signals

The system also tracks information such as **freshness and verification status**.

If supporting information is unavailable or uncertain, the system can communicate that uncertainty rather than presenting an unsupported conclusion.

---

### 8. Market-Wide Noise Reduction

Many stocks can move together because of the same market-wide or sector-wide movement.

Treating every movement as an individual alert can overwhelm the user.

Market Memory can identify broader movements and help focus attention on the unusual changes that stand out from that context.

The objective is simple:

**More events → fewer things that actually need attention.**

---

## Why This Is Different

A traditional watchlist generally follows:

**Market Event → Display / Alert**

Market Memory follows:

**Market Event → Change Detection → Significance → Relevance → Confidence → Attention → Explanation → Evidence**

This changes the purpose of a watchlist.

Instead of asking the user to continuously monitor everything, Market Memory helps answer:

> **"What meaningfully changed since I last checked, and what deserves my attention?"**

---

## AI Approach

AI is treated as an **explanation layer**, not as the source of truth.

The core market analysis determines the signals, significance, relevance, confidence, and supporting evidence.

AI can then be used to turn those verified inputs into a human-readable explanation.

**Market Data**

↓

**Deterministic Analysis**

↓

**Significance + Relevance**

↓

**Evidence**

↓

**Human-readable Explanation**

This design reduces the risk of an AI model inventing market events, numbers, or unsupported conclusions.

Market Memory is an information and monitoring tool, not a buy/sell recommendation system.

---

## Example User Journey

Imagine an investor tracking 20 stocks.

### Step 1 — Create a Watchlist

The user creates a watchlist and adds stocks they want to monitor.

### Step 2 — Set Watch Intent

For Tata Motors, the user selects:

> **"Track EV growth."**

### Step 3 — Check the Market

The user checks their watchlist and leaves the application.

Market Memory records the checkpoint.

### Step 4 — Changes Occur

While the user is away, multiple market events occur.

Some are normal market movements.

Some are sector-wide movements.

Others are unusual company-specific changes.

### Step 5 — Return to Market Memory

Instead of forcing the user to review everything, the system summarizes what happened:

**73 events**

**61 Normal**

**8 Worth Knowing**

**4 Need Attention**

### Step 6 — Investigate

The user opens a high-attention insight.

They can see its significance, relevance, attention score, confidence, context, and supporting evidence.

### Step 7 — Trace the Change

The user follows the change through its market context, sector context, stock movement, trading activity, relevant event signals, and evidence.

The user gets the answer they actually wanted:

> **"What changed, and why should I care?"**

---

## Tech Stack

### Frontend

* React
* TypeScript
* Vite
* Tailwind CSS

### Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy

### Database

* PostgreSQL

### Development

* Alembic
* Pytest

---

## Project Structure

**backend/**

Contains the FastAPI application, API routes, database models, services, providers, migrations, and tests.

**frontend/**

Contains the React/TypeScript interface, watchlist experience, attention insights, Trace the Change experience, and evidence views.

**backend/alembic/**

Database migration configuration and migration versions.

**backend/tests/**

Automated tests for the backend and core functionality.

---

## Running Locally

### Backend

From the project root:

```
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Start the backend:

```
uvicorn app.main:app --reload
```

### Frontend

Open another terminal:

```
cd frontend
npm install
npm run dev
```

Open the local URL provided by Vite.

---

## Environment Configuration

Environment variable templates are provided in:

**backend/.env.example**

**frontend/.env.example**

Create local `.env` files as required.

Do not commit API keys, passwords, database credentials, or other secrets.

---

## Testing

From the backend directory:

```
pytest
```

The project includes tests covering areas such as:

* Application health
* Market intelligence
* Watchlists
* Starting/demo data
* Database migrations

---

## Responsible Design

Market Memory is designed to help users **understand market changes**, not to make investment decisions for them.

It does not aim to provide:

* Buy/sell recommendations
* Guaranteed returns
* Unsupported predictions
* Fabricated market information
* Unsupported causal claims

When evidence is incomplete or uncertain, the system should communicate that uncertainty.

---

## Core Idea

Market Memory is built around one simple principle:

> **A watchlist should help investors monitor less, while missing less.**

Instead of making users consume more alerts and information, Market Memory helps them focus on the changes that actually deserve attention.

# Market Memory

**Don't just watch stocks. Understand what changed.**
