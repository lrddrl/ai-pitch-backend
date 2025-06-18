import asyncio
import databases
import sqlalchemy
from datetime import date

DATABASE_URL = "postgresql://postgres:152535@localhost:5432/ai_pitch_db"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

async def create_tables():
    async with database.connection() as conn:
        try:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS startups (
                    startup_id SERIAL PRIMARY KEY,
                    name VARCHAR(255),
                    industry VARCHAR(100),
                    subsector VARCHAR(100),
                    target_market VARCHAR(255),
                    trend_tag VARCHAR(100),
                    stage VARCHAR(50),
                    location VARCHAR(100),
                    website VARCHAR(255),
                    avg_score NUMERIC(5,2),
                    total_evaluations INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS reviewers (
                    reviewer_id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    email VARCHAR(255) UNIQUE NOT NULL,
                    role VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS evaluations (
                    eval_id SERIAL PRIMARY KEY,
                    startup_id INTEGER REFERENCES startups(startup_id) ON DELETE CASCADE,
                    reviewer_id INTEGER REFERENCES reviewers(reviewer_id) ON DELETE CASCADE,
                    team_score NUMERIC(5,2),
                    market_score NUMERIC(5,2),
                    product_score NUMERIC(5,2),
                    total_score NUMERIC(5,2),
                    eval_date DATE,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    category_id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    weight NUMERIC(5,2) CHECK (weight BETWEEN 0 AND 100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS criteria (
                    criteria_id SERIAL PRIMARY KEY,
                    category_id INTEGER REFERENCES categories(category_id) ON DELETE CASCADE,
                    name VARCHAR(100),
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS eval_criteria (
                    eval_criteria_id SERIAL PRIMARY KEY,
                    eval_id INTEGER REFERENCES evaluations(eval_id) ON DELETE CASCADE,
                    criteria_id INTEGER REFERENCES criteria(criteria_id) ON DELETE CASCADE,
                    score NUMERIC(5,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS prompts (
                    prompt_id SERIAL PRIMARY KEY,
                    criteria_id INTEGER REFERENCES criteria(criteria_id) ON DELETE CASCADE,
                    text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS dimensions (
                    dimension_id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS prompt_dimension (
                    prompt_dimension_id SERIAL PRIMARY KEY,
                    prompt_id INTEGER REFERENCES prompts(prompt_id) ON DELETE CASCADE,
                    dimension_id INTEGER REFERENCES dimensions(dimension_id) ON DELETE CASCADE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS transaction_log (
                    transaction_id SERIAL PRIMARY KEY,
                    action_type VARCHAR(50) NOT NULL,
                    entity_affected VARCHAR(100) NOT NULL,
                    entity_id INTEGER NOT NULL,
                    actor VARCHAR(100),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("All tables created successfully.")
        except Exception as e:
            print("Error creating tables:", e)
            raise

async def seed_data():
    try:
        query_startups = """
            INSERT INTO startups (name, industry, subsector, target_market, trend_tag, stage, location, website, avg_score, total_evaluations)
            VALUES (:name, :industry, :subsector, :target_market, :trend_tag, :stage, :location, :website, :avg_score, :total_evaluations)
            RETURNING startup_id;
        """
        query_reviewers = """
            INSERT INTO reviewers (name, email, role) VALUES (:name, :email, :role) RETURNING reviewer_id;
        """
        query_categories = """
            INSERT INTO categories (name, weight) VALUES (:name, :weight) RETURNING category_id;
        """
        query_criteria = """
            INSERT INTO criteria (category_id, name, description) VALUES (:category_id, :name, :description) RETURNING criteria_id;
        """
        query_evaluations = """
            INSERT INTO evaluations (startup_id, reviewer_id, team_score, market_score, product_score, total_score, eval_date, notes)
            VALUES (:startup_id, :reviewer_id, :team_score, :market_score, :product_score, :total_score, :eval_date, :notes)
            RETURNING eval_id;
        """
        query_eval_criteria = """
            INSERT INTO eval_criteria (eval_id, criteria_id, score) VALUES (:eval_id, :criteria_id, :score);
        """

        startups = [
            {"name":"TechNova","industry":"Technology","subsector":"AI","target_market":"Global Enterprises","trend_tag":"AI","stage":"Seed","location":"San Francisco, CA","website":"https://technova.ai","avg_score":8.5,"total_evaluations":5},
            {"name":"GreenEnergy","industry":"Energy","subsector":"Solar","target_market":"Residential","trend_tag":"Clean Energy","stage":"Series A","location":"Austin, TX","website":"https://greenenergy.com","avg_score":7.8,"total_evaluations":8},
        ]

        reviewers = [
            {"name":"Alice Johnson","email":"alice.johnson@example.com","role":"Lead Reviewer"},
            {"name":"Bob Smith","email":"bob.smith@example.com","role":"Reviewer"},
        ]

        categories = [
            {"name":"Team","weight":30.0},
            {"name":"Market","weight":25.0},
        ]

        criteria = [
            {"category_name":"Team","name":"Founder Experience","description":"Experience of the founding team."},
            {"category_name":"Team","name":"Leadership","description":"Quality of leadership."},
            {"category_name":"Market","name":"Market Size","description":"Addressable market size."},
            {"category_name":"Market","name":"Growth Potential","description":"Potential for market growth."},
        ]

        await database.connect()
        startup_ids = []
        for s in startups:
            sid = await database.execute(query_startups, s)
            print(f"Inserted startup {s['name']} with id {sid}")
            startup_ids.append(sid)

        reviewer_ids = []
        for r in reviewers:
            rid = await database.execute(query_reviewers, r)
            print(f"Inserted reviewer {r['name']} with id {rid}")
            reviewer_ids.append(rid)

        category_id_map = {}
        for c in categories:
            cid = await database.execute(query_categories, c)
            print(f"Inserted category {c['name']} with id {cid}")
            category_id_map[c['name']] = cid

        criteria_id_map = {}
        for crit in criteria:
            crit['category_id'] = category_id_map[crit['category_name']]
            cid = await database.execute(query_criteria, crit)
            print(f"Inserted criteria {crit['name']} with id {cid}")
            criteria_id_map[crit['name']] = cid

        # Insert one evaluation example
        evals = [
            {
                "startup_id": startup_ids[0],
                "reviewer_id": reviewer_ids[0],
                "team_score": 8.5,
                "market_score": 7.0,
                "product_score": 8.0,
                "total_score": 7.8,
                "eval_date": date.today(),
                "notes": "Good founding team, solid market potential."
            }
        ]

        eval_ids = []
        for e in evals:
            eid = await database.execute(query_evaluations, e)
            print(f"Inserted evaluation with id {eid}")
            eval_ids.append(eid)

        eval_criteria_scores = [
            {"eval_id": eval_ids[0], "criteria_id": criteria_id_map["Founder Experience"], "score": 8.5},
            {"eval_id": eval_ids[0], "criteria_id": criteria_id_map["Leadership"], "score": 7.5},
            {"eval_id": eval_ids[0], "criteria_id": criteria_id_map["Market Size"], "score": 7.0},
            {"eval_id": eval_ids[0], "criteria_id": criteria_id_map["Growth Potential"], "score": 7.5},
        ]
        for ecs in eval_criteria_scores:
            await database.execute(query_eval_criteria, ecs)
            print(f"Inserted eval_criteria for eval_id {ecs['eval_id']} and criteria_id {ecs['criteria_id']}")

        await database.disconnect()
        print("All fake data inserted successfully.")
    except Exception as e:
        print("Error during data seeding:", e)
        raise

async def main():
    await database.connect()
    await create_tables()
    await seed_data()
    await database.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
