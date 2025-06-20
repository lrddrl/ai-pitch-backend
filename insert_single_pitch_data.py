import asyncio
import databases
import sqlalchemy
from datetime import datetime

DATABASE_URL = "postgresql://postgres:152535@localhost:5432/ai_pitch_db"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

pitch_deck_scores = sqlalchemy.Table(
    "pitch_deck_scores",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("pitch_deck_name", sqlalchemy.String(255)),
    sqlalchemy.Column("factor", sqlalchemy.String(100)),
    sqlalchemy.Column("score", sqlalchemy.Integer),
    sqlalchemy.Column("justification", sqlalchemy.Text),
    sqlalchemy.Column("evaluated_at", sqlalchemy.TIMESTAMP),
)

fake_pitch_data = [
    {"factor": "Features & Benefits", "score": 8, "justification": "Strong features."},
    {"factor": "Readiness", "score": 7, "justification": "Market readiness is good."},
    {"factor": "Barrier to Entry", "score": 5, "justification": "Moderate competition."},
    {"factor": "Market Size", "score": 9, "justification": "Large market."},
    {"factor": "GTM Strategy", "score": 6, "justification": "Go-to-market plan needs work."},
    {"factor": "Technology IP", "score": 8, "justification": "Strong technology and IP."},
    {"factor": "Exit Potential", "score": 7, "justification": "Clear exit pathways."},
    {"factor": "Competition", "score": 5, "justification": "Some strong competitors."},
    {"factor": "Risk", "score": 6, "justification": "Risks are manageable."},
    {"factor": "Deal Terms", "score": 7, "justification": "Fair deal terms."},
]

async def create_table():
    import asyncpg
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS pitch_deck_scores (
            id SERIAL PRIMARY KEY,
            pitch_deck_name VARCHAR(255),
            factor VARCHAR(100),
            score INTEGER,
            justification TEXT,
            evaluated_at TIMESTAMP
        );
    """)
    await conn.close()

async def insert_fake_data():
    await database.connect()
    pitch_name = "Pitch Deck Single Example"
    evaluated_time = datetime.utcnow()

    for entry in fake_pitch_data:
        query = pitch_deck_scores.insert().values(
            pitch_deck_name=pitch_name,
            factor=entry["factor"],
            score=entry["score"],
            justification=entry["justification"],
            evaluated_at=evaluated_time
        )
        last_id = await database.execute(query)
        print(f"Inserted record id: {last_id}")

    await database.disconnect()

async def main():
    await create_table()
    await insert_fake_data()

if __name__ == "__main__":
    asyncio.run(main())
