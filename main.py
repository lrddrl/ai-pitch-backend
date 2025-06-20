from fastapi import FastAPI, Response, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import fitz  # PyMuPDF
import os
import json
import openai
import re
import traceback 
import pandas as pd
from sqlalchemy import create_engine
from pdf2image import convert_from_path
import pytesseract


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# from db import init_db, save_score_to_db    

def get_engine():
    DATABASE_URL = "postgresql://postgres:152535@localhost:5432/ai_pitch_db"
    return create_engine(DATABASE_URL)

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

# @app.lifespan ("startup")
def on_startup():
    init_db()  

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
    You are an expert investment analyst. Evaluate the following 10 criteria using a scale from 1 (worst) to 10 (best).


    Scoring guide:
    - 1-2: Very Bad
    - 3-4: Bad
    - 5-6: OK
    - 7-8: Good
    - 9-10: Very Good

    Rubric:

    Leadership (Founder and team experience, CEO):
    - 1-2: Founders lack relevant experience or leadership skills.
    - 3-4: Minimal experience, no proven track record.
    - 5-6: Some relevant experience; moderate track record; coachable.
    - 7-8: Substantial relevant experience; strong CEO; prior successes.
    - 9-10: Recognized experts; visionary CEO; proven significant achievements.

    Financials (Revenue model, projections, unit economics):
    - 1-2: No credible revenue plan or unrealistic projections.
    - 3-4: Revenue model unclear; projections lack data.
    - 5-6: Model is reasonable, but scalability/profitability unclear.
    - 7-8: Achievable projections with scalable, profitable model.
    - 9-10: Robust, validated projections; excellent unit economics.

    MarketSize (Addressable market, growth potential):
    - 1-2: Market is too small or demand is unproven.
    - 3-4: Small/niche market, limited growth.
    - 5-6: Moderate market size, some growth potential.
    - 7-8: Large, growing market; strong demand.
    - 9-10: Massive market; growth and demand highly evident.

    GTMStrategy (Go-to-market plan, customer acquisition):
    - 1-2: No defined strategy; entry unclear.
    - 3-4: Strategy exists but not feasible/deep enough.
    - 5-6: Basic strategy, initial customer plans.
    - 7-8: Clear, actionable strategy; market penetration likely.
    - 9-10: Innovative strategy; ensures strong, rapid entry.

    TechnologyIP (Product innovation, IP, defensibility):
    - 1-2: No innovation or defensibility; easily copied.
    - 3-4: Minimal differentiation; weak IP/barriers.
    - 5-6: Some unique features; moderate defensibility.
    - 7-8: Strong innovation; IP filed; market barriers exist.
    - 9-10: Exceptional innovation; robust IP; hard to replicate.

    ExitPotential (Exit pathways, acquirer interest):
    - 1-2: No clear exit; unrealistic assumptions.
    - 3-4: Weak understanding of exit/acquirers.
    - 5-6: Basic exit strategy; needs refinement.
    - 7-8: Well-defined strategy; clear acquirer interest.
    - 9-10: Multiple strong exit pathways; high-value prospects.

    Competition (Market positioning, barriers to entry):
    - 1-2: No differentiation; easily replaced.
    - 3-4: Minimal barriers; poor positioning.
    - 5-6: Some differentiation; moderate barriers.
    - 7-8: Strong positioning; significant barriers.
    - 9-10: Exceptional defensibility; leading market position.

    Risk (Market, operational, execution risks) :
    - 1-2: Major risks unaddressed; high vulnerability.
    - 3-4: Multiple significant risks; partial mitigation.
    - 5-6: Manageable risks; mitigation plans in place.
    - 7-8: Few risks; well-controlled/mitigated.
    - 9-10: Minimal risks; highly diversified and resilient.

    DealTerms (Valuation, equity, dilution risk):
    - 1-2: Valuation grossly inflated or unclear; high dilution.
    - 3-4: Questionable valuation; minimal investor protection.
    - 5-6: Reasonable valuation; standard dilution terms.
    - 7-8: Well-structured terms; protect investor interests.
    - 9-10: Highly attractive valuation and dilution terms.

    Traction (Product-market fit, customer adoption):
    - 1-2: No traction; no evidence of demand.
    - 3-4: Minimal adoption; weak evidence of product-market fit.
    - 5-6: Some early traction; moderate adoption.
    - 7-8: Good customer adoption; strong product-market fit.
    - 9-10: Excellent traction; rapid and growing adoption.

    Startup Info:
    {pitch}



    JSON output format example:
    {{
      "Leadership": {{"Score": 7, "Color": "Yellow", "Justification": "Experienced founder with strong vision but limited team."}},
      "Market Size & Product-Market Fit": {{"Score": 8, "Color": "Green", "Justification": "Large growing market with clear demand."}},
      ...
      "Exit Potential": {{"Score": 6, "Color": "Yellow", "Justification": "Potential acquirers identified but revenue still low."}},
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
            # images = convert_from_path("temp.pdf")
            images = convert_from_path("temp.pdf", poppler_path=r"C:\poppler-24.08.0\Library\bin")
            ocr_text = ""
            for img in images:
                ocr_text += pytesseract.image_to_string(img)
            full_text = ocr_text

        if len(full_text.strip()) < 100:
            return {"error": "Extracted text too short. Please upload a valid business plan PDF."}

        scores = score_pitch_with_openai(full_text)

        preview_length = 100
        preview_text = full_text[:preview_length] + ("..." if len(full_text) > preview_length else "")

        return {
            "scores": scores,
            "preview_text": preview_text,
            "preview_text_full": full_text,
        }

    except Exception as e:
        traceback.print_exc()
        return Response(
            content=json.dumps({"error": str(e)}),
            media_type="application/json",
            status_code=500
        )


#generate report
@app.post("/generate_analysis_report")
async def generate_analysis_report(request: Request):
    try:
        body = await request.json()
        scores = body.get("scores")
        project_text = body.get("project_text")
        prompt = f"""
        You are a professional VC investment analyst. Based on the following project description and factor scoring, write a detailed, structured, and insight-driven investment analysis report in fluent English, with sections for Executive Summary, Elevator Pitch, Weighted Scoring Table, Category Breakdown (strengths, concerns, suggestions), Risk Catalog, Strategic Questions for CEO, and Final Recommendation. 
        Project Description:
        {project_text}

        Factor Scoring (JSON):
        {json.dumps(scores, indent=2)}

        Use clear titles and emojis as in the following example, and provide actionable suggestions for improvement.
        """
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4.1-nano-2025-04-14",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2048
        )
        content = response.choices[0].message.content
        return {"report": content}
    except Exception as e:
        return {"error": str(e)}


@app.post("/macro_risk_analysis")
async def macro_risk_analysis(request: Request):
    try:
        body = await request.json()
        startup_text = body.get("startup_text", "")

        engine = get_engine()
        sql = """
        SELECT indicator, period, value, source FROM public.macro_trends
        WHERE country = 'USA'
        ORDER BY period DESC
        LIMIT 12;
        """
        df = pd.read_sql(sql, engine)


        macro_data_str = df.to_csv(index=False)
        macro_prompt = f"""
        What macro-level risks could impact this startup, including political, technical, environmental, or ESG factors?
        Here is the startup description:
        {startup_text}

        Here are the latest USA macro trends (last 12 months, from OECD data):

        {macro_data_str}

        Based on this data, provide an expert-level analysis of potential macro risks (political, economic, technical, regulatory, ESG, environmental, etc) that may affect the business, with concrete examples and suggestions.
        Output in fluent English with clear sections for each risk type.
        """

        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4.1-nano-2025-04-14",
            messages=[{"role": "user", "content": macro_prompt}],
            temperature=0.4,
            max_tokens=1024
        )
        content = response.choices[0].message.content
        return {"analysis": content}
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}


def analyze_subjectivity(df):
    # Calculate standard deviation of scores per evaluator and category
    subjectivity = df.groupby(['evaluator_id', 'category'])['score'].std().unstack().fillna(0)
    
    # Calculate absolute deviation from group mean per score
    group_avg = df.groupby(['startup_id', 'category'])['score'].mean().reset_index()
    df_merged = df.merge(group_avg, on=['startup_id', 'category'], suffixes=('', '_avg'))
    df_merged['abs_dev'] = abs(df_merged['score'] - df_merged['score_avg'])
    
    # Mean absolute deviation per evaluator (summary of subjectivity)
    subjectivity_summary = df_merged.groupby('evaluator_id')['abs_dev'].mean()
    
    return subjectivity.to_dict(), subjectivity_summary.to_dict()

def analyze_rubric_inconsistency(df):
    # Pivot scores: evaluators x categories
    pivot = df.pivot_table(index='evaluator_id', columns='category', values='score', aggfunc='mean')
    
    # Calculate deviation from each category mean
    rubric_drift = pivot.apply(lambda x: x - x.mean(), axis=0)
    
    # Average absolute deviation per evaluator
    rubric_drift_avg = rubric_drift.abs().mean(axis=1)
    
    return rubric_drift.to_dict(), rubric_drift_avg.to_dict()
