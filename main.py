from fastapi import FastAPI, Response, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import fitz  # PyMuPDF
import os
import json
import openai
import re
import traceback

# Load environment variables
load_dotenv()

app = FastAPI()

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "*")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

cfa_factors = [
    "Features & Benefits",
    "Readiness",
    "Barrier to Entry",
    "Adoption Potential",
    "Supply Chain",
    "Market Size",
    "Entrepreneur Experience",
    "Financial Expectations"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return Response(
        content='{"message": "Hello, this is the root!"}',
        media_type="application/json",
        status_code=200
    )

def fix_json(json_str):
    # Replace single quotes with double quotes
    json_str = re.sub(r"'", '"', json_str)
    # Remove trailing commas
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    return json_str

def score_pitch_with_openai(pitch):
    prompt = f"""
    You are an expert investment analyst evaluating an early-stage startup pitch.
    Please score the startup on the following 10 factors on a scale from 1 (lowest) to 10 (highest):
    1. Leadership
    2. Market Size & Product-Market Fit
    3. Technology & Intellectual Property (IP)
    4. Competition & Moat
    5. Deal Terms & Valuation
    6. Financials
    7. Traction
    8. FDA Approval (if applicable, otherwise mark N/A)
    9. Go-to-Market Strategy
    10. Exit Potential

    Additionally, assess Risk separately (Low, Medium, High) and adjust each category score if needed based on risk factors.
    Provide color coding for each category score: Green (score 8-10), Yellow (5-7), Red (1-4).
    
    For each factor, return a JSON object with:
    - "Score": integer 1 to 10 or "N/A" if not applicable,
    - "Color": "Green", "Yellow", or "Red",
    - "Justification": one concise sentence explaining the score.

    Also include a top-level "OverallRisk" field with one of ["Low", "Medium", "High"].

    Your output must be strictly valid JSON, no extra text, keys and strings in double quotes.

    Startup Pitch:
    {pitch}

    JSON output format example:
    {{
      "Leadership": {{"Score": 7, "Color": "Yellow", "Justification": "Experienced founder with strong vision but limited team."}},
      "Market Size & Product-Market Fit": {{"Score": 8, "Color": "Green", "Justification": "Large growing market with clear demand."}},
      ...
      "Exit Potential": {{"Score": 6, "Color": "Yellow", "Justification": "Potential acquirers identified but revenue still low."}},
      "Risk": "Medium"
    }}
    """

    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
         model="gpt-4.1-nano-2025-04-14", 
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1000
    )
    content = response.choices[0].message.content
    print("GPT returned:", content)
    try:
        return json.loads(content)
    except Exception:
        json_str = re.search(r"\{[\s\S]+\}", content)
        if json_str:
            try:
                return json.loads(fix_json(json_str.group()))
            except Exception as e:
                print("Manual JSON fix still failed:", e)
                raise e
        else:
            raise


@app.post("/score")
async def score_pdf(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        with open("temp.pdf", "wb") as f:
            f.write(contents)
        doc = fitz.open("temp.pdf")
        full_text = "\n".join(page.get_text() for page in doc)

        if len(full_text.strip()) < 100:
            return {"error": "Extracted text too short. Please upload a valid business plan PDF."}

        scores = score_pitch_with_openai(full_text)

        preview_length = 100
        preview_text = full_text[:preview_length] + ("..." if len(full_text) > preview_length else "")

        return {
            "scores": scores,
            "preview_text": preview_text,
            "preview_text_full": full_text,
            "Risk": scores.get("Risk") or scores.get("OverallRisk") or "N/A"
        }
    except Exception as e:
        traceback.print_exc()
        return Response(content=json.dumps({"error": str(e)}), media_type="application/json", status_code=500)


