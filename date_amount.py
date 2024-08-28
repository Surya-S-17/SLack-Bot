import spacy
nlp2 = spacy.load("date_amount")
from extract_da import extract_date, extract_amount

def extract_date_and_highest_amount(doc_ents,text):
    dates = []
    amounts = []

    # Extract dates and amounts from entities
    for ent in doc_ents:
        if ent.label_ == "DATE":
            dates.append(ent.text)
        elif ent.label_ == "AMOUNT":
            amount_str = ent.text.replace('$', '').replace('₹', '').replace('Rs.', '').replace(',', '').strip()
            try:
                amount = float(amount_str)
                amounts.append(amount)
            except ValueError:
                continue

    # If there are no dates or amounts, return None
    if not dates and amounts:
        return [extract_date(text), max(amounts)]
    elif not amounts and dates:
        return [dates[0],extract_amount(text)]
    elif not amounts and not dates:
        return [extract_date(text),extract_amount(text)]

    # Return the first date and the highest amount
    highest_amount = max(amounts)
    return [dates[0], highest_amount]

def extract_date_and_amount(text):
    
    doc = nlp2(text)
    result = extract_date_and_highest_amount(doc.ents,text)
    return result


    dates = []
    amounts = []

    # Extract dates and amounts from entities
    for ent in doc_ents:
        if ent.label_ == "DATE":
            dates.append(ent.text)
        elif ent.label_ == "AMOUNT":
            amount_str = ent.text.replace('$', '').replace('₹', '').replace('Rs.', '').replace(',', '').strip()
            try:
                amount = float(amount_str)
                amounts.append(amount)
            except ValueError:
                continue

    # If there are no dates or amounts, return None
    if not dates or not amounts:
        return [None, None]

    # Return the first date and the highest amount
    highest_amount = max(amounts)
    return [dates[0], highest_amount]