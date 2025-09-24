import re
from pdfminer.high_level import extract_text

def extract_and_clean(path: str) -> str:
    # Step 1: extract raw text
    raw_text = extract_text(path)

    if not raw_text:
        return ""

    # Step 2: normalize whitespace
    text = re.sub(r'\s+', ' ', raw_text)

    # Step 3: remove headers/footers like "Page X"
    text = re.sub(r'Page \d+', '', text, flags=re.IGNORECASE)

    # Step 4: strip weird symbols (keep letters, numbers, punctuation)
    text = re.sub(r'[^a-zA-Z0-9.,;!?()\-–&%\'\s]', '', text)

    # Step 5: trim
    return text.strip()