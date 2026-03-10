import time
import json
import os
from db import get_recent_events

try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    LLM_ENABLED = True
except:
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

    if mem_high and cpu_high:
        root = "System resource exhaustion due to high memory and CPU usage"
        severity = "HIGH"
        confidence = 0.9
        recommended_action = "Inspect running applications and terminate heavy processes"

    elif mem_high:
        root = "High memory usage detected"
        severity = "HIGH"
        confidence = 0.85
        recommended_action = "Identify memory-intensive processes"

    elif cpu_high:
        root = "CPU overload detected"
        severity = "HIGH"
        confidence = 0.8
        recommended_action = "Check CPU-intensive tasks"

    elif disk_high:
        root = "Disk usage critically high"
        severity = "HIGH"
        confidence = 0.8
        recommended_action = "Clean unnecessary files or expand disk capacity"

    root_cause = generate_root_cause(root, evidence)
    needs_more_data = False

    if confidence < 0.6:
        print("Low confidence detected. Gathering additional context...")
        events = get_recent_events(window_seconds=60)
        evidence = [e[3] for e in events]

        confidence += 0.2
        needs_more_data = True

    diagnosis = {
        "incident_summary": root,
        "root_cause": root_cause,
        "causal_chain": evidence,
        "evidence": evidence,
        "data_source": "own-machine",
        "severity": severity,
        "recommended_action": recommended_action,
        "confidence": confidence,
        "needs_more_data": needs_more_data
    }
    with open("output.json", "w") as f:
        json.dump(diagnosis, f, indent=4)

    print("Diagnosis updated:", root)
    time.sleep(10)