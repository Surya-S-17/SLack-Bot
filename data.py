import pandas as pd
import random

# Define lists of items for each category
food_items = [
    "apple", "banana", "chicken sandwich", "pizza", "coffee", "burger", 
    "sushi", "salad", "pasta", "steak", "cake", "ice cream", "orange juice"
]

travel_items = [
    "bus ticket", "train ticket", "flight ticket", "taxi fare", "hotel booking",
    "car rental", "metro pass", "gasoline", "toll fee", "parking fee", 
    "ferry ticket", "cruise ticket"
]

entertainment_items = [
    "movie ticket", "concert ticket", "amusement park ticket", "gaming subscription", 
    "music subscription", "theater ticket", "sports event ticket", "streaming service",
    "museum ticket", "exhibition ticket"
]

work_items = [
    "wifi bill", "office supplies", "printer ink", "laptop", "software license", 
    "coworking space rental", "stationery", "notebook", "pen", "business card",
    "desk chair", "mouse", "keyboard"
]

na_items = [
    "charity donation", "clothing", "groceries", "medical bill", "insurance premium",
    "phone bill", "electricity bill", "water bill", "gym membership", 
    "beauty products", "haircut", "cleaning service"
]

# Combine all items into a list with their respective categories
items = [(item, "food") for item in food_items] + \
        [(item, "travel") for item in travel_items] + \
        [(item, "entertainment") for item in entertainment_items] + \
        [(item, "work") for item in work_items] + \
        [(item, "NA") for item in na_items]

# Function to generate dataset
def generate_expense_dataset(num_rows):
    data = random.choices(items, k=num_rows)
    return pd.DataFrame(data, columns=["item", "category"])

# Generate dataset
num_rows = 1000000
dataset = generate_expense_dataset(num_rows)

# Save dataset to a CSV file
dataset.to_csv("/mnt/data/expense_dataset.csv", index=False)

dataset.head()
