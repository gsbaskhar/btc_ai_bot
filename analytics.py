import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from config import *

# ============= LOAD ENV ===================

load_dotenv()

client = OpenAI(

    api_key=os.getenv(
        "OPENAI_API_KEY"
    )
)

# ============= AI MARKET FILTER ====================

def ask_ai(df):

    rows = df.iloc[-20:]

    data = "\n".join([

        f"{r.time.strftime('%H:%M')} | "
        f"C={r.close:.2f} | "
        f"RSI={r.rsi:.2f}"

        for _, r in rows.iterrows()
    ])

    prompt = f"""
Analyze BTCUSD M5 market condition.

Return ONLY JSON.

{{
    "market":"TRENDING/RANGING",
    "confidence":0-1
}}

Data:
{data}
"""

    try:

        response = client.chat.completions.create(

            model=OPENAI_MODEL,

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.2,

            response_format={
                "type": "json_object"
            }
        )

        result = json.loads(

            response.choices[0]
            .message
            .content
        )

        return result

    except Exception as e:

        print(f"AI ERROR : {e}")

        return None