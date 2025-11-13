import os
import json
from groq import Groq
import re
# -------------------------------
# CONFIG
# -------------------------------
client = Groq(api_key="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")
INPUT_JSON = "interventions_converted.json"
OUTPUT_JSON = "interventions_updated.json"
MODEL = "llama-3.1-8b-instant"

# -------------------------------
# FUNCTION TO UPDATE ENTRY
# -------------------------------
def update_entry(entry):
    context_text = entry["context"]

    prompt = f"""
You are an expert in road safety and traffic engineering.
Given the context below, generate structured data fields to describe an appropriate intervention.

Rules:
- Keep the 'context' unchanged.
- Use the context to infer what type of safety intervention it is.
- 'intervention': a clear, descriptive title (max 10 words)
- 'impact': 1-line describing how it improves safety or prevents accidents
- 'keywords': a list of 5–8 short phrases describing *accident types, risk factors, or road conditions* that this intervention helps mitigate.
  Examples of such keywords: ["rear-end crash", "overspeeding", "rural road", "pedestrian conflict", "low visibility"]

Return only valid JSON like:
{{
  "intervention": "...",
  "impact": "...",
  "keywords": ["...", "...", "..."]
}}

Context:
\"\"\"{context_text}\"\"\"
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You generate structured JSON for road safety interventions, optimizing for accident-related keywords."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=200
    )

    content = response.choices[0].message.content.strip()

   

    # Try to extract JSON even if model adds extra text
    try:
        # Find the first JSON block in the output
        match = re.search(r'\{[\s\S]*\}', content)
        if match:
            json_text = match.group(0)
            generated = json.loads(json_text)
        else:
            raise json.JSONDecodeError("No JSON found", content, 0)
    except json.JSONDecodeError:
        print(f"⚠️ JSON parse error for entry. Raw output:\n{content}\n")
        generated = {
            "intervention": entry.get("intervention", ""),
            "impact": entry.get("impact", ""),
            "keywords": entry.get("keywords", [])
        }


    updated = {
        "intervention": generated.get("intervention", entry["intervention"]),
        "context": entry["context"],
        "source": entry.get("source", ""),
        "impact": generated.get("impact", entry["impact"]),
        "keywords": generated.get("keywords", entry.get("keywords", [])),
    }
    return updated

# -------------------------------
# MAIN LOOP
# -------------------------------
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

updated_data = []
for i, entry in enumerate(data, 1):
    print(f"🔁 Processing {i}/{len(data)}...")
    updated_data.append(update_entry(entry))

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(updated_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Updated JSON saved to {OUTPUT_JSON}")
