from fastapi import FastAPI
import json
app=FastAPI()
@app.get("/diagnosis")
def get_diagnosis():
    with open("output.json") as f:
        data = json.load(f)
    return data