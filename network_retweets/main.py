import pyomnisci
import pandas as pd
import re

# 1️⃣ Connect to OmniSci
conn = pyomnisci.connect(user='admin', password='HyperInteractive', host='localhost', port=6274)
cursor = conn.cursor()

# 2️⃣ Query your yearly table (e.g., Twitter_2017)
query = """
SELECT
    created_at,
    tweet_id_str,
    user_name,
    tweet_text
FROM Twitter_2017
LIMIT 10; 
"""
cursor.execute(query)
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]
df = pd.DataFrame(rows, columns=columns)

# 3️⃣ Add isRetweet field (1 if "RT@" is present, else 0)
df['isRetweet'] = df['tweet_text'].str.contains(r'RT@', case=False, regex=True).astype(int)

# 4️⃣ Extract edgeB (the username being retweeted)
df['edgeB'] = df['tweet_text'].str.extract(r'RT@([A-Za-z0-9_]+)')

# Optional: preview
print(df[['tweet_text', 'isRetweet', 'edgeB']].head())

# 5️⃣ Close connection
conn.close()
