import re
import json
import spacy
from spacy.training import Example

# Define a function to clean and validate date and amount annotations
def clean_data(dataset):
    cleaned_data = []

    # Regular expressions to match valid date and amount formats
    date_pattern = re.compile(r'\b\d{4}-\d{2}-\d{2}\b')
    amount_pattern = re.compile(r'\$\d+(?:\.\d{2})?')

    for entry in dataset:
        text, annotations = entry
        entities = annotations["entities"]

        # Clean and validate date and amount entities
        new_entities = []
        for entity in entities:
            start, end, label = entity
            if label == "DATE":
                match = date_pattern.search(text[start:end])
            elif label == "AMOUNT":
                match = amount_pattern.search(text[start:end])
            else:
                continue
            
            if match:
                match_start, match_end = match.span()
                new_entities.append([match_start, match_end, label])
        
        # Remove overlapping entities
        new_entities = remove_overlapping_entities(new_entities)
        
        cleaned_data.append([text, {"entities": new_entities}])

    return cleaned_data

# Function to remove overlapping entities
def remove_overlapping_entities(entities):
    entities = sorted(entities, key=lambda x: x[0])
    filtered_entities = []
    last_end = -1
    
    for start, end, label in entities:
        if start >= last_end:
            filtered_entities.append([start, end, label])
            last_end = end
    
    return filtered_entities

# Read the dataset from a JSON file
with open('synthetic_receipts.json', 'r') as f:
    dataset = json.load(f)

# Clean the dataset
cleaned_dataset = clean_data(dataset)

# Validate cleaned dataset with spacy's offsets_to_biluo_tags
nlp = spacy.blank("en")
for entry in cleaned_dataset:
    text, annotations = entry
    doc = nlp.make_doc(text)
    try:
        Example.from_dict(doc, annotations)
    except ValueError as e:
        print(f"Skipping invalid entry due to error: {e}")

# Save the cleaned dataset to a new JSON file
with open('synthetic_receipts.json', 'w') as f:
    json.dump(cleaned_dataset, f, indent=4)

print("Dataset cleaned and saved to 'cleaned_dataset.json'")


# Load the existing data
#with open('synthetic_receipts.json', 'r') as file:
#    data = json.load(file)
#data.extend(output)
#with open("synthetic_receipts.json", "w") as f:
#    json.dump(data, f)

#print("Synthetic data saved to synthetic_receipts.json")
