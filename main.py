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
    Read the following startup pitch and assign CFA scores (A+ to C-) for each of the 8 CFA factors listed.
    Provide a one-line justification for each score.

    Startup Pitch:
    {pitch}

    IMPORTANT: Only return valid JSON, with all keys and string values in double quotes, no comments or extra text.
    Output format as JSON:
    {{
      "Features & Benefits": {{"Grade": "", "Justification": ""}},
      "Readiness": {{"Grade": "", "Justification": ""}},
      "Barrier to Entry": {{"Grade": "", "Justification": ""}},
      "Adoption Potential": {{"Grade": "", "Justification": ""}},
      "Supply Chain": {{"Grade": "", "Justification": ""}},
      "Market Size": {{"Grade": "", "Justification": ""}},
      "Entrepreneur Experience": {{"Grade": "", "Justification": ""}},
      "Financial Expectations": {{"Grade": "", "Justification": ""}}
    }}
    """

    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Change to gpt-4-turbo if you have access
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
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
        print("PDF uploaded, size:", len(contents))
        with open("temp.pdf", "wb") as f:
            f.write(contents)
        doc = fitz.open("temp.pdf")
        text = "\n".join(page.get_text() for page in doc)
        print("Extracted text length:", len(text))
        if len(text.strip()) < 100:
            return {"error": "Extracted text too short. Please upload a valid business plan PDF."}
        result = score_pitch_with_openai(text)
        print("Score result:", result)
        return result
    except Exception as e:
        traceback.print_exc()
        return Response(content=json.dumps({"error": str(e)}), media_type="application/json", status_code=500)
