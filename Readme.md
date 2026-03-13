# AI System Diagnosis Agent

## Problem Statement

* Build an autonomous AI system diagnosis agent that can:
* continuously collect raw system logs + machine metrics
* detect related abnormal events
* correlate them automatically
* infer root cause like a senior engineer
* produce a structured diagnosis
* expose that diagnosis through an API in real time

## Overview

This project implements an **AI-powered system diagnosis agent** that continuously monitors system metrics, detects abnormal system behavior, and generates a structured root-cause diagnosis.

The system ingests monitoring events, groups related events into incidents, performs reasoning to hypothesize the root cause, and exposes the latest diagnosis through a REST API.

The architecture simulates a simplified **AI-based Site Reliability Engineering (SRE) agent**.

---

# Data Source

This implementation uses **live system metrics from the host machine** collected using the `psutil` library.

The following metrics are monitored:

* CPU usage
* Memory usage
* Disk usage

Metrics are collected periodically and stored as log events for analysis.

---

# System Architecture

```
Observer → SQLite Database → Agent → Diagnosis JSON → REST API
```

### Observer (Log Ingestion)

The **Observer** continuously collects system metrics every **5 seconds** and stores them in a **SQLite database**.

Each event contains:

* Timestamp
* Source
* Severity
* Raw metric text

Example event:

```
CPU=25.4 MEM=82.1 DISK=67.2
```

This satisfies the assignment requirement of **log ingestion into SQLite**.

---

# Agent (Reasoning Engine)

The **Agent** performs incident analysis every **10 seconds**.

The reasoning workflow is:

1. Retrieve recent events from the database
2. Apply **incident windowing** (last 30 seconds of events)
3. Detect abnormal system conditions
4. Generate a **root cause hypothesis using an LLM**
5. Apply **reflection logic** if confidence is low
6. Produce a structured diagnosis
7. Save the diagnosis to `output.json`

### Incident Windowing

Events that occur within the last **30 seconds** are grouped into a single incident window.

This allows the agent to analyze **temporally related system events**.

---

### Root Cause Hypothesis

The agent generates a **root cause theory** from the observed metrics.

Example diagnosis:

```
High memory usage detected likely caused by a memory-intensive process.
```

The reasoning layer supports **LLM-based analysis using OpenAI models**.

If an API key is not provided, the agent falls back to a rule-based reasoning system.

---

### Reflection Logic

If the agent confidence score is below **0.6**, the system automatically gathers additional context:

* Expands the incident window to **60 seconds**
* Collects more events
* Re-evaluates the diagnosis

This mimics an **AI reflection loop** used in autonomous agents.

---

# Diagnosis Output

The agent produces a structured diagnosis every **10 seconds**.

Example output (`output.json`):

```json
{
 "incident_summary": "High memory usage detected",
 "root_cause": "High memory usage likely caused by a memory-intensive process",
 "severity": "HIGH",
 "confidence": 0.85,
 "recommended_action": "Identify and terminate memory-heavy processes"
}
```

---

# API (FastAPI Backend)

A **FastAPI server** exposes the latest diagnosis.

Endpoint:

```
GET /diagnosis
```

Example request:

```
http://127.0.0.1:8000/diagnosis
```

Example response:

```json
{
 "incident_summary": "High memory usage detected",
 "severity": "HIGH",
 "confidence": 0.85
}
```

---

# Stress Testing

To simulate abnormal system behavior, the repository includes a **stress testing script**.

`stress_memory.py` gradually allocates memory to create controlled memory pressure.

This allows the system to detect incidents such as:

```
High memory usage detected
Severity: HIGH
```

This validates that the monitoring pipeline can detect and diagnose real system anomalies.

---

# How to Run

## 1. Install dependencies

```
pip install -r requirements.txt
```

---

## 2. Start the Observer

```
python observer.py
```

---

## 3. Start the Agent

```
python agent.py
```

---

## 4. Start the API server

```
uvicorn api:app --reload
```

---

## 5. Trigger stress test

```
python stress_memory.py
```

---

## 6. View diagnosis

Open a browser:

```
http://127.0.0.1:8000/diagnosis
```

---

# Technologies Used

* Python
* FastAPI
* SQLite
* psutil
* OpenAI API (optional LLM reasoning)
* JSON

---

# Project Structure

```
ai-assignment
│
├── observer.py
├── agent.py
├── api.py
├── db.py
├── stress_memory.py
├── output.json
├── incidents.db
├── requirements.txt
└── README.md
```

---

# Conclusion

This project demonstrates a simplified **AI-driven system monitoring and diagnosis pipeline** capable of:

* collecting system telemetry
* detecting abnormal system behavior
* generating root cause explanations
* exposing results through an API

The architecture is modular and can be extended for **real-world AI-based system reliability monitoring**.


