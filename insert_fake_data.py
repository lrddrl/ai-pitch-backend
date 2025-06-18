import asyncio
import databases
import sqlalchemy

DATABASE_URL = "postgresql://postgres:152535@localhost:5432/ai_pitch_db"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

ai_evaluations = sqlalchemy.Table(
    "ai_evaluations",
    metadata,
    sqlalchemy.Column("ai_eval_id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("ai_pitch_deck_name", sqlalchemy.String(255)),
    sqlalchemy.Column("tca_factor", sqlalchemy.String(100)),
    sqlalchemy.Column("score", sqlalchemy.Integer),
    sqlalchemy.Column("justification", sqlalchemy.Text),
)

fake_data = [
    # Pitch Deck sample 1
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Leadership", "score": 7, "justification": "Founders have relevant experience, including a former Nestlé scientist and logistics expert, indicating strong domain knowledge and operational expertise. However, no mention of prior successful startups or leadership achievements, so slightly below top-tier."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Financials", "score": 4, "justification": "Limited financial data provided; revenue model and projections are not detailed. The funding request suggests growth plans, but without clear unit economics or financial validation, score remains low."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Market Size", "score": 7, "justification": "The plant-based food market is large and growing, with initial presence in Whole Foods and direct-to-consumer channels across multiple states, indicating significant demand and expansion potential."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "GTM Strategy", "score": 6, "justification": "Current distribution through Whole Foods and direct shipping shows initial go-to-market efforts. While promising, the strategy details for scaling nationally are not fully articulated."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Technology/IP", "score": 6, "justification": "Proprietary packaging extending shelf life suggests some innovation, but no mention of patents or strong defensibility measures. The innovation is promising but not yet fully protected."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Exit Potential", "score": 5, "justification": "Potential exits include large food or CPG companies interested in plant-based products, but no explicit exit strategy or acquirer interest detailed. The pathway exists but needs clearer positioning."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Competition", "score": 5, "justification": "The plant-based meal market is competitive with established players. Proprietary packaging offers some differentiation, but barriers to entry and market positioning are moderate."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Risk", "score": 4, "justification": "Risks include scaling production, market acceptance, and supply chain logistics. No detailed mitigation strategies are provided, indicating moderate to high operational risks."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "DealTerms", "score": 5, "justification": "Funding amount sought suggests reasonable valuation, but without specific terms, it's difficult to assess investor protections or dilution impact. Assumes standard terms at this stage."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Traction", "score": 6, "justification": "Presence in 10 Whole Foods stores and direct-to-consumer sales across three states demonstrates early adoption and product-market fit, but scale and growth rate are modest."},

    # Pitch Deck sample 2
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Leadership", "score": 7, "justification": "Founders have relevant experience, including a former Nestlé scientist and logistics expert, indicating strong domain knowledge and operational expertise. However, no mention of prior successful startups or proven leadership track record beyond their backgrounds."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Financials", "score": 4, "justification": "Limited financial data provided; revenue model and projections are not detailed. The current funding goal suggests early-stage traction, but scalability and unit economics are unclear."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Market Size", "score": 7, "justification": "The plant-based food market is large and growing, with initial presence in multiple stores and direct-to-consumer channels, indicating strong demand and expansion potential."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "GTM Strategy", "score": 6, "justification": "Presence in Whole Foods and direct shipping shows some go-to-market efforts, but the strategy details are limited. Expansion plans suggest a clear intent, but execution specifics are lacking."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Technology/IP", "score": 8, "justification": "Proprietary packaging extending shelf life without preservatives indicates innovation and potential defensibility through IP or trade secrets."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Exit Potential", "score": 5, "justification": "While the food sector has potential acquirers, no specific exit pathways or high-value exit strategies are outlined. The early stage limits clarity on exit prospects."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Competition", "score": 5, "justification": "The plant-based meal market is competitive, but proprietary packaging may offer some differentiation. Barriers to entry are moderate; competitive landscape details are limited."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Risk", "score": 4, "justification": "Operational risks include scaling manufacturing and distribution. Market risks are inherent in food innovation, and operational risks are not fully addressed."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "DealTerms", "score": 5, "justification": "Funding amount indicates early-stage valuation; terms are not specified, but the investment size suggests standard early-stage deal terms."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Traction", "score": 6, "justification": "Presence in 10 Whole Foods stores and direct shipping across three states shows initial customer adoption, but overall traction remains modest."},

    # Pitch Deck sample 3
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Leadership", "score": 7, "justification": "Founders have relevant experience, including a former Nestlé scientist and logistics expert, indicating a strong team with industry knowledge. However, no mention of prior startup successes or leadership track record, so slightly below top-tier."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Financials", "score": 4, "justification": "Limited financial data provided; revenue model and projections are not detailed. The company's current stage suggests early traction but lacks validated unit economics or clear profitability metrics."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Market Size", "score": 7, "justification": "The plant-based food market is large and growing, with national expansion plans indicating significant demand potential."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "GTM Strategy", "score": 6, "justification": "Existing presence in 10 Whole Foods stores and direct-to-consumer shipping shows initial go-to-market efforts. However, details on customer acquisition strategies and scalability are limited."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Technology/IP", "score": 8, "justification": "Proprietary packaging extending shelf life without preservatives suggests a strong innovation with defensible IP, providing a competitive edge."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Exit Potential", "score": 5, "justification": "Potential exits could include larger food or CPG companies interested in plant-based innovations, but no explicit pathways or acquirer interest outlined."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Competition", "score": 5, "justification": "Market has competitors in plant-based foods, but proprietary packaging offers some differentiation. Barriers to entry are moderate."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Risk", "score": 4, "justification": "Risks include scaling manufacturing, market acceptance, and supply chain dependencies. Early-stage company with limited risk mitigation details."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "DealTerms", "score": 6, "justification": "Seeking $1.2M for expansion suggests reasonable valuation, but specific terms are not provided. Standard dilution and valuation assumptions likely apply."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Traction", "score": 7, "justification": "Presence in 10 Whole Foods stores and active direct-to-consumer sales demonstrate early product-market fit and customer adoption."},

    # Pitch Deck sample 4
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Leadership", "score": 7, "justification": "Founders have relevant experience, including a former Nestle scientist and logistics expert, indicating strong domain knowledge and operational expertise. However, the overall team size and track record are not detailed, so while promising, it's not yet at the highest level."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Financials", "score": 5, "justification": "The company is currently live in 10 stores and shipping regionally, with a funding ask of $1.2M for expansion. Financial projections and unit economics are not provided, making it difficult to assess scalability and profitability fully."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Market Size", "score": 8, "justification": "The plant-based food market is large and growing rapidly, with national expansion plans indicating significant demand and market potential."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "GTM Strategy", "score": 7, "justification": "Existing presence in Whole Foods and direct-to-consumer channels suggests a clear initial strategy. The plan to expand nationally indicates an actionable go-to-market approach, though details on customer acquisition tactics are limited."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Technology/IP", "score": 8, "justification": "The proprietary packaging system that extends shelf life without preservatives suggests a strong innovation with defensibility, potentially creating market barriers."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Exit Potential", "score": 6, "justification": "While the food industry attracts acquirers, specific exit pathways or interest from major players are not detailed. The company's niche position offers some potential, but more strategic clarity is needed."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Competition", "score": 6, "justification": "The plant-based frozen meal market is competitive, but proprietary packaging provides some differentiation. Barriers to entry exist but are not insurmountable."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Risk", "score": 5, "justification": "Risks include scaling production, supply chain, and market acceptance. The company has some mitigation plans, but operational and market risks remain moderate."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "DealTerms", "score": 6, "justification": "Funding request is clear, but valuation details are not provided. Terms appear reasonable, though further details would clarify investor protection."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Traction", "score": 7, "justification": "Presence in 10 Whole Foods stores and regional shipping demonstrates early customer adoption and product-market fit, with room for growth as they expand nationally."},

    # Pitch Deck sample 5
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Leadership", "score": 7, "justification": "Founders have relevant experience, including a former Nestlé scientist and logistics expert, indicating strong domain knowledge and operational expertise. However, no mention of prior successful startups or leadership achievements, so slightly below top tier."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Financials", "score": 5, "justification": "The company has a clear revenue model with initial traction, but projections and unit economics details are not provided, making the financial outlook moderate and somewhat uncertain."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Market Size", "score": 8, "justification": "The plant-based food market is large and growing, with national expansion plans indicating significant demand and growth potential."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "GTM Strategy", "score": 6, "justification": "Existing presence in Whole Foods and direct-to-consumer sales suggest a basic go-to-market approach. However, details on customer acquisition strategies and scalability are limited."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Technology/IP", "score": 7, "justification": "Proprietary packaging extending shelf life without preservatives indicates innovation and some defensibility. Further details on patents or IP filings would strengthen this score."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Exit Potential", "score": 6, "justification": "Potential exits could include larger food or CPG companies interested in plant-based products, but specific pathways or acquirer interest are not detailed."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Competition", "score": 5, "justification": "The market is competitive with many players in plant-based foods; the proprietary packaging offers some differentiation, but barriers are moderate."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Risk", "score": 5, "justification": "Risks include market acceptance, scaling production, and supply chain logistics. Some mitigation appears in existing operations, but operational risks remain."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "DealTerms", "score": 6, "justification": "Seeking $1.2M for expansion suggests reasonable valuation and terms, but specific deal structures are not provided."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Traction", "score": 7, "justification": "Product is live in 10 Whole Foods stores and shipping across three states, indicating good early customer adoption and proof of concept."},

    # Pitch Deck sample 6
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Leadership", "score": 7, "justification": "Founders have relevant experience, including a former Nestlé scientist and logistics expert, indicating strong domain knowledge and operational expertise. However, no information on prior startup successes or leadership track record is provided, so a slightly conservative score is assigned."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Financials", "score": 5, "justification": "The company has a clear revenue model with initial traction in retail and direct-to-consumer channels. However, detailed projections, unit economics, or profitability data are not provided, making the financial outlook somewhat uncertain."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Market Size", "score": 8, "justification": "The plant-based food market is large and growing rapidly, with initial presence in Whole Foods and online sales across multiple states, indicating strong demand and significant growth potential."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "GTM Strategy", "score": 7, "justification": "EcoMeal's strategy includes retail expansion and direct-to-consumer sales, which are clear and actionable. The plan to expand nationally and build a new processing facility suggests a solid go-to-market approach, though details on customer acquisition tactics are limited."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Technology/IP", "score": 6, "justification": "The proprietary packaging system that extends shelf life without preservatives is a notable innovation, but no information on patents or defensibility is provided, so the score reflects moderate innovation and IP strength."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Exit Potential", "score": 6, "justification": "Potential exit pathways exist through acquisition by larger food or CPG companies interested in plant-based products, but no explicit exit strategy or acquirer interest is detailed, making this an average assessment."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Competition", "score": 6, "justification": "The plant-based frozen meal market has several competitors, but EcoMeal's proprietary packaging offers some differentiation. Barriers to entry are moderate, so the positioning is decent but not exceptional."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Risk", "score": 5, "justification": "Risks include market acceptance, scaling production, and supply chain management. The company appears to have mitigation plans, but operational and market risks remain present."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "DealTerms", "score": 6, "justification": "Seeking $1.2M to fund expansion suggests reasonable valuation and dilution terms, though specific deal terms are not provided. The funding round appears standard for stage."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Traction", "score": 7, "justification": "Having products in 10 Whole Foods stores and shipping across three states indicates good early customer adoption and product-market fit, with room for growth."},

    # Pitch Deck sample 7
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Leadership", "score": 7, "justification": "Founders have relevant experience, including a former Nestlé scientist and logistics expert, indicating a solid leadership foundation. However, no mention of prior startup successes or visionary leadership elevates the score further."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Financials", "score": 5, "justification": "The company has a clear revenue model with current sales in retail and direct-to-consumer, but projections and unit economics details are lacking, making the financial viability moderately clear but not robust."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Market Size", "score": 8, "justification": "The plant-based food market is large and growing, with initial presence in multiple stores and online sales across three states, indicating strong demand and significant growth potential."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "GTM Strategy", "score": 7, "justification": "They have an initial retail presence and direct-to-consumer channels, suggesting a clear plan. Expansion plans indicate a strategic approach, though details on customer acquisition tactics are limited."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Technology/IP", "score": 6, "justification": "Proprietary packaging that extends shelf life without preservatives is a notable innovation, but no mention of patents or strong defensibility measures, limiting the score."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Exit Potential", "score": 6, "justification": "Potential exit pathways through acquisition by larger food or packaging companies exist, but the company is still early-stage with limited revenue, making the exit less certain."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Competition", "score": 5, "justification": "The plant-based food space is competitive with established players; the proprietary packaging offers some differentiation, but barriers to entry are moderate."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Risk", "score": 5, "justification": "Risks include scaling manufacturing, market acceptance, and supply chain, but initial traction reduces some operational risks. Overall, manageable but present."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "DealTerms", "score": 6, "justification": "Seeking $1.2M for expansion suggests reasonable valuation; details on valuation and dilution are not provided, so a moderate score is appropriate."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Traction", "score": 7, "justification": "Currently live in 10 Whole Foods stores and shipping in three states indicates good early customer adoption and product-market fit, with room for growth."},

    # Pitch Deck sample 8
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Leadership", "score": 7, "justification": "Founders have relevant experience, including a former Nestle scientist and logistics expert, indicating strong domain knowledge and operational expertise. However, no mention of prior startup successes or leadership track record, so slightly below top tier."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Financials", "score": 4, "justification": "Limited financial details provided; revenue model and projections are not specified. The focus is on expansion funding rather than demonstrated profitability or unit economics, making financial assessment weak."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Market Size", "score": 7, "justification": "Plant-based food market is large and growing rapidly, with initial traction in Whole Foods and direct-to-consumer channels, indicating strong demand and significant market opportunity."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "GTM Strategy", "score": 6, "justification": "Existing presence in retail stores and online sales suggest a basic go-to-market approach. However, details on customer acquisition strategies and scalability plans are limited."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Technology/IP", "score": 6, "justification": "Proprietary packaging extending shelf life without preservatives indicates some innovation, but no mention of patents or strong defensibility measures."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Exit Potential", "score": 5, "justification": "Potential exits could include larger food or CPG companies interested in plant-based products, but no explicit pathways or acquirer interest outlined."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Competition", "score": 5, "justification": "The plant-based frozen meal market is competitive with established players. Proprietary packaging offers some differentiation, but barriers to entry are moderate."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Risk", "score": 4, "justification": "Risks include scaling manufacturing, supply chain complexities, and market acceptance. Limited information on mitigation strategies."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "DealTerms", "score": 5, "justification": "Funding amount sought is clear, but valuation and equity terms are not specified, making assessment of attractiveness difficult."},
    {"ai_pitch_deck_name": "Pitch Deck sample", "tca_factor": "Traction", "score": 7, "justification": "Product is live in 10 Whole Foods stores and shipping across three states, demonstrating early customer adoption and market validation."},
]


async def create_table():
    import asyncpg
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS ai_evaluations (
            ai_eval_id SERIAL PRIMARY KEY,
            ai_pitch_deck_name VARCHAR(255),
            tca_factor VARCHAR(100),
            score INTEGER,
            justification TEXT
        );
    """)
    await conn.close()

async def insert_fake_data():
    await database.connect()
    for entry in fake_data:
        query = ai_evaluations.insert().values(
            ai_pitch_deck_name=entry["ai_pitch_deck_name"],
            tca_factor=entry["tca_factor"],
            score=entry["score"],
            justification=entry["justification"],
        )
        last_id = await database.execute(query)
        print(f"Inserted record id: {last_id}")
    await database.disconnect()

async def main():
    await create_table()
    await insert_fake_data()

if __name__ == "__main__":
    asyncio.run(main())
