from fastapi import FastAPI, Response, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF

app = FastAPI()

# Allow CORS for any origin (for Vercel frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TIP: In production, replace with frontend domain like ["https://yourapp.vercel.app"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.get("/")
# def read_root():
#     return {"message": "Hello, this is the root!"}

@app.get("/")
def read_root():
    try:
        return Response(content='{"message": "Hello, this is the root!"}', media_type="application/json", status_code=200)
    except Exception:
        return Response(content='{"error": "Internal Server Error"}', media_type="application/json", status_code=500)

@app.post("/extract")
async def extract_text(file: UploadFile = File(...)):
    contents = await file.read()
    with open("temp.pdf", "wb") as f:
        f.write(contents)

    doc = fitz.open("temp.pdf")
    text = "\n".join(page.get_text() for page in doc)
    return {"text": text.strip()}
