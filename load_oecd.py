import requests
import pandas as pd
from io import StringIO
from sqlalchemy import create_engine, text
from datetime import datetime

def get_engine():
    DATABASE_URL = "postgresql://postgres:152535@localhost:5432/ai_pitch_db"
    return create_engine(DATABASE_URL)

def create_macro_trends_table(engine):
    create_sql = """
    CREATE TABLE IF NOT EXISTS macro_trends (
        trend_id SERIAL PRIMARY KEY,
        country VARCHAR(3),
        indicator VARCHAR(100),
        period VARCHAR(20),
        value FLOAT,
        source TEXT,
        last_updated TIMESTAMP
    );
    """
    with engine.begin() as conn:
        conn.execute(text(create_sql))

def ensure_domains_table_schema(engine):
  
    with engine.begin() as conn:
        result = conn.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name='domains' AND column_name='description';")
        )
        
        if result.rowcount == 0 or len(result.fetchall()) == 0:
            conn.execute(text("ALTER TABLE domains ADD COLUMN description TEXT;"))
            print("Added description column to domains table.")

def create_benchmark_scores_table(engine):
    create_sql = """
    CREATE TABLE IF NOT EXISTS benchmark_scores (
        benchmark_id SERIAL PRIMARY KEY,
        country VARCHAR(3),
        domain_id INTEGER REFERENCES domains(domain_id),
        industry VARCHAR(100),
        avg_score FLOAT,
        low_threshold FLOAT,
        high_threshold FLOAT,
        source TEXT,
        last_updated TIMESTAMP
    );
    """
    with engine.begin() as conn:
        conn.execute(text(create_sql))

def fetch_and_transform_data(url):
    response = requests.get(url)
    response.raise_for_status()
    df_raw = pd.read_csv(StringIO(response.text))

    df = pd.DataFrame({
        'country': df_raw['REF_AREA'],
        'indicator': df_raw['INDICATOR'] if 'INDICATOR' in df_raw else 'OECD_Indicator',
        'period': df_raw['TIME_PERIOD'],
        'value': df_raw['OBS_VALUE'],
        'source': 'OECD API CSV',
        'last_updated': datetime.now()
    })
    return df

def truncate_fields(df):
    df['country'] = df['country'].astype(str).str[:3]
    df['indicator'] = df['indicator'].astype(str).str[:100]
    df['period'] = df['period'].astype(str).str[:20]
    return df

def ensure_domain_exists(engine, domain_id=1, name="Default", description="Default domain"):
    with engine.begin() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM domains WHERE domain_id = :id"), {'id': domain_id}).scalar()
        if result == 0:
            conn.execute(
                text("INSERT INTO domains (domain_id, name, description) VALUES (:id, :name, :desc)"),
                {"id": domain_id, "name": name, "desc": description}
            )
            print(f"Inserted domain_id={domain_id} into domains table.")

def generate_benchmark_scores(engine):
    df = pd.read_sql("SELECT country, indicator, value FROM macro_trends", engine)
    if df.empty:
        print("macro_trends表暂无数据，无法生成benchmark_scores。")
        return

    agg = (
        df.groupby(['country', 'indicator'])
        .agg(avg_score=('value', 'mean'))
        .reset_index()
    )
    agg['low_threshold'] = agg['avg_score'] * 0.9
    agg['high_threshold'] = agg['avg_score'] * 1.1
    agg['domain_id'] = 1  # 可自定义映射
    agg['industry'] = agg['indicator']
    agg['source'] = 'Macro Trends Aggregation'
    agg['last_updated'] = datetime.now()

    agg = agg[['country', 'domain_id', 'industry', 'avg_score', 'low_threshold', 'high_threshold', 'source', 'last_updated']]
    agg.to_sql('benchmark_scores', engine, if_exists='append', index=False)
    print("Data inserted into benchmark_scores table successfully.")

def main():
    engine = get_engine()
    create_macro_trends_table(engine)
    ensure_domains_table_schema(engine)  # 只补字段不删表
    create_benchmark_scores_table(engine)

    api_url = "https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_CLI/.M.LI...AA...H?startPeriod=2023-02&dimensionAtObservation=AllDimensions&format=csvfilewithlabels"

    df = fetch_and_transform_data(api_url)
    df = truncate_fields(df)
    print(df.head())
    df.to_sql('macro_trends', engine, if_exists='append', index=False)
    print("Data inserted into macro_trends table successfully.")

    ensure_domain_exists(engine, domain_id=1, name="Default", description="Default domain")

    generate_benchmark_scores(engine)

if __name__ == '__main__':
    main()
import requests
import pandas as pd
from io import StringIO
from sqlalchemy import create_engine, text
from datetime import datetime

def get_engine():
    DATABASE_URL = "postgresql://postgres:152535@localhost:5432/ai_pitch_db"
    return create_engine(DATABASE_URL)

def create_macro_trends_table(engine):
    create_sql = """
    CREATE TABLE IF NOT EXISTS macro_trends (
        trend_id SERIAL PRIMARY KEY,
        country VARCHAR(3),
        indicator VARCHAR(100),
        period VARCHAR(20),
        value FLOAT,
        source TEXT,
        last_updated TIMESTAMP
    );
    """
    with engine.begin() as conn:
        conn.execute(text(create_sql))

def ensure_domains_table_schema(engine):
    # 只补 description 字段，不DROP表
    with engine.begin() as conn:
        result = conn.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name='domains' AND column_name='description';")
        )
        # PostgreSQL rowcount=0代表没找到字段
        if result.rowcount == 0 or len(result.fetchall()) == 0:
            conn.execute(text("ALTER TABLE domains ADD COLUMN description TEXT;"))
            print("Added description column to domains table.")

def create_benchmark_scores_table(engine):
    create_sql = """
    CREATE TABLE IF NOT EXISTS benchmark_scores (
        benchmark_id SERIAL PRIMARY KEY,
        country VARCHAR(3),
        domain_id INTEGER REFERENCES domains(domain_id),
        industry VARCHAR(100),
        avg_score FLOAT,
        low_threshold FLOAT,
        high_threshold FLOAT,
        source TEXT,
        last_updated TIMESTAMP
    );
    """
    with engine.begin() as conn:
        conn.execute(text(create_sql))

def fetch_and_transform_data(url):
    response = requests.get(url)
    response.raise_for_status()
    df_raw = pd.read_csv(StringIO(response.text))

    df = pd.DataFrame({
        'country': df_raw['REF_AREA'],
        'indicator': df_raw['INDICATOR'] if 'INDICATOR' in df_raw else 'OECD_Indicator',
        'period': df_raw['TIME_PERIOD'],
        'value': df_raw['OBS_VALUE'],
        'source': 'OECD API CSV',
        'last_updated': datetime.now()
    })
    return df

def truncate_fields(df):
    df['country'] = df['country'].astype(str).str[:3]
    df['indicator'] = df['indicator'].astype(str).str[:100]
    df['period'] = df['period'].astype(str).str[:20]
    return df

def ensure_domain_exists(engine, domain_id=1, name="Default", description="Default domain"):
    with engine.begin() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM domains WHERE domain_id = :id"), {'id': domain_id}).scalar()
        if result == 0:
            conn.execute(
                text("INSERT INTO domains (domain_id, name, description) VALUES (:id, :name, :desc)"),
                {"id": domain_id, "name": name, "desc": description}
            )
            print(f"Inserted domain_id={domain_id} into domains table.")

def generate_benchmark_scores(engine):
    df = pd.read_sql("SELECT country, indicator, value FROM macro_trends", engine)
    if df.empty:
        print("macro_trends表暂无数据，无法生成benchmark_scores。")
        return

    agg = (
        df.groupby(['country', 'indicator'])
        .agg(avg_score=('value', 'mean'))
        .reset_index()
    )
    agg['low_threshold'] = agg['avg_score'] * 0.9
    agg['high_threshold'] = agg['avg_score'] * 1.1
    agg['domain_id'] = 1  # 可自定义映射
    agg['industry'] = agg['indicator']
    agg['source'] = 'Macro Trends Aggregation'
    agg['last_updated'] = datetime.now()

    agg = agg[['country', 'domain_id', 'industry', 'avg_score', 'low_threshold', 'high_threshold', 'source', 'last_updated']]
    agg.to_sql('benchmark_scores', engine, if_exists='append', index=False)
    print("Data inserted into benchmark_scores table successfully.")

def main():
    engine = get_engine()
    create_macro_trends_table(engine)
    ensure_domains_table_schema(engine)  # 只补字段不删表
    create_benchmark_scores_table(engine)

    api_url = "https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_CLI/.M.LI...AA...H?startPeriod=2023-02&dimensionAtObservation=AllDimensions&format=csvfilewithlabels"

    df = fetch_and_transform_data(api_url)
    df = truncate_fields(df)
    print(df.head())
    df.to_sql('macro_trends', engine, if_exists='append', index=False)
    print("Data inserted into macro_trends table successfully.")

    ensure_domain_exists(engine, domain_id=1, name="Default", description="Default domain")

    generate_benchmark_scores(engine)

if __name__ == '__main__':
    main()
