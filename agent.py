import time
import json
import os
import uuid
import datetime
from db import get_recent_events

try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    LLM_ENABLED = True
except Exception:
    LLM_ENABLED = False
print("Agent started...")
def generate_root_cause(summary, evidence):
    if not LLM_ENABLED:
        return f"Based on recent system metrics, the likely cause is: {summary}"

    prompt = f"""
You are a Site Reliability Engineer.

System monitoring detected the following events:
{evidence}

Detected issue:
{summary}

Explain the likely root cause and recommend an action in 1-2 sentences.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception:
        return f"Based on recent system metrics, the likely cause is: {summary}"


while True:
    events = get_recent_events(window_seconds=30)
    cpu_high = False
    mem_high = False
    disk_high = False
    evidence = []

    for e in events:
        text = e[3]
        evidence.append(text)
        if "CPU=" in text:
            cpu = float(text.split("CPU=")[1].split()[0])
            if cpu > 85:
                cpu_high = True

        if "MEM=" in text:
            mem = float(text.split("MEM=")[1].split()[0])
            if mem > 65:
                mem_high = True

        if "DISK=" in text:
            disk = float(text.split("DISK=")[1].split()[0])
            if disk > 90:
                disk_high = True

    root = "System operating normally"
    severity = "LOW"
    confidence = 0.7
    recommended_action = "No immediate action required"
    predicted_label = "normal"
    if mem_high and cpu_high:
        root = "System resource exhaustion due to high memory and CPU usage"
        severity = "HIGH"
        confidence = 0.9
        recommended_action = "Inspect running applications and terminate heavy processes"
        predicted_label = "resource_exhaustion"

    elif mem_high:
        root = "High memory usage detected"
        severity = "HIGH"
        confidence = 0.85
        recommended_action = "Identify memory-intensive processes"
        predicted_label = "memory_pressure"

    elif cpu_high:
        root = "CPU overload detected"
        severity = "HIGH"
        confidence = 0.8
        recommended_action = "Check CPU-intensive tasks"
        predicted_label = "cpu_overload"

    elif disk_high:
        root = "Disk usage critically high"
        severity = "HIGH"
        confidence = 0.8
        recommended_action = "Clean unnecessary files or expand disk capacity"
        predicted_label = "disk_pressure"

    root_cause = generate_root_cause(root, evidence)

    needs_more_data = False
    window_seconds = 30

    if confidence < 0.6:
        print("Low confidence detected. Gathering additional context...")
        events = get_recent_events(window_seconds=60)
        evidence = [e[3] for e in events]
        confidence += 0.2
        needs_more_data = True
        window_seconds = 60

    ground_truth = "memory_pressure_from_stress_memory_script"
    if predicted_label == "memory_pressure":
        validation_status = "matched"
    elif predicted_label == "normal":
        validation_status = "no_active_injected_incident_detected"
    else:
        validation_status = "mismatch_or_different_incident"

    diagnosis = {
        "incident_id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.now().isoformat(),
        "window_seconds": window_seconds,
        "incident_summary": root,
        "root_cause": root_cause,
        "causal_chain": evidence,
        "evidence": evidence,
        "data_source": "own-machine",
        "severity": severity,
        "recommended_action": recommended_action,
        "confidence": confidence,
        "ground_truth": ground_truth,
        "predicted_label": predicted_label,
        "validation_status": validation_status,
        "needs_more_data": needs_more_data
    }
    with open("output.json", "w") as f:
        json.dump(diagnosis, f, indent=4)
    print("\n" + "=" * 65)
    print("AI SYSTEM DIAGNOSIS AGENT")
    print("=" * 65)
    print(f"Incident ID        : {diagnosis['incident_id']}")
    print(f"Timestamp          : {diagnosis['timestamp']}")
    print(f"Window Seconds     : {diagnosis['window_seconds']}")
    print(f"Incident Summary   : {diagnosis['incident_summary']}")
    print(f"Severity           : {diagnosis['severity']}")
    print(f"Confidence         : {diagnosis['confidence']}")
    print(f"Predicted Label    : {diagnosis['predicted_label']}")
    print(f"Ground Truth       : {diagnosis['ground_truth']}")
    print(f"Validation Status  : {diagnosis['validation_status']}")
    print(f"Recommended Action : {diagnosis['recommended_action']}")
    print("=" * 65 + "\n")
    time.sleep(10)
