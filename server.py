import os
import json
import logging
import time
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from google import genai
from openai import OpenAI
import anthropic

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("OmniCore")

app = FastAPI(title="Smart Multi-AI Engine", version="2.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AppPayload(BaseModel):
    prompt: str = Field(..., description="यूज़र का सवाल")
    selected_engine: Optional[str] = Field("auto", description="auto, gemini, deepseek, openai, claude")
    system_role: Optional[str] = Field("assistant", description="assistant, coder, gamer, teacher")
    custom_system_prompt: Optional[str] = Field(None)
    temperature: Optional[float] = Field(0.7)
    max_tokens: Optional[int] = Field(1000)

SYSTEM_ROLES = {
    "assistant": "You are a smart, concise AI assistant.",
    "coder": "You are an expert coder. Write clean, bug-free code with explanations.",
    "gamer": "You are an energetic gaming companion and tactical strategist.",
    "teacher": "Explain complex ideas in very simple terms with easy examples."
}

async def run_gemini(prompt: str, sys_inst: str, max_t: int, temp: float) -> str:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY missing")
    client = genai.Client(api_key=key)
    res = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={"max_output_tokens": max_t, "temperature": temp, "system_instruction": sys_inst}
    )
    return res.text

async def run_deepseek(prompt: str, sys_inst: str, max_t: int, temp: float) -> str:
    key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        raise ValueError("DEEPSEEK_API_KEY missing")
    client = OpenAI(api_key=key, base_url="https://api.deepseek.com")
    res = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": sys_inst}, {"role": "user", "content": prompt}],
        max_tokens=max_t,
        temperature=temp
    )
    return res.choices[0].message.content

async def run_openai(prompt: str, sys_inst: str, max_t: int, temp: float) -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY missing")
    client = OpenAI(api_key=key)
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": sys_inst}, {"role": "user", "content": prompt}],
        max_tokens=max_t,
        temperature=temp
    )
    return res.choices[0].message.content

async def run_claude(prompt: str, sys_inst: str, max_t: int, temp: float) -> str:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError("ANTHROPIC_API_KEY missing")
    client = anthropic.Anthropic(api_key=key)
    msg = client.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=max_t,
        temperature=temp,
        system=sys_inst,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text

@app.post("/execute")
async def execute_action(data: AppPayload):
    start_time = time.time()
    user_query = data.prompt.strip()

    if not user_query:
        raise HTTPException(status_code=400, detail="Prompt is empty.")

    active_instruction = data.custom_system_prompt or SYSTEM_ROLES.get(data.system_role.lower(), SYSTEM_ROLES["assistant"])
    engine = data.selected_engine.lower()
    
    order = [engine] if engine in ["gemini", "deepseek", "openai", "claude"] else ["gemini", "deepseek", "openai", "claude"]

    reply = None
    used = None
    last_err = ""

    for eng in order:
        try:
            if eng == "gemini":
                reply = await run_gemini(user_query, active_instruction, data.max_tokens, data.temperature)
            elif eng == "deepseek":
                reply = await run_deepseek(user_query, active_instruction, data.max_tokens, data.temperature)
            elif eng == "openai":
                reply = await run_openai(user_query, active_instruction, data.max_tokens, data.temperature)
            elif eng == "claude":
                reply = await run_claude(user_query, active_instruction, data.max_tokens, data.temperature)

            if reply:
                used = eng
                break
        except Exception as e:
            last_err = str(e)
            continue

    if not reply:
        raise HTTPException(status_code=500, detail=f"All models failed: {last_err}")

    elapsed = round((time.time() - start_time) * 1000, 2)
    return {
        "status": "success",
        "engine_used": used,
        "response": reply,
        "latency_ms": elapsed
    }

@app.get("/")
def home():
    return {"status": "online", "message": "Multi-AI Core is running"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
  
