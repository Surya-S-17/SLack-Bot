import random
import json
from faker import Faker

fake = Faker()

# Function to generate synthetic receipt data
def generate_receipt():
    shop_name = fake.company()
    address = fake.address().replace("\n", ", ")
    phone_number = fake.phone_number()
    date = fake.date_time().strftime("%m-%d-%Y %H:%M")
    
    items = []
    total_amount = 0
    for _ in range(random.randint(3, 7)):
        item_name = " ".join(fake.words(nb=2))
        price = round(random.uniform(0.5, 50.0), 2)
        items.append({"item_name": item_name, "price": price})
        total_amount += price

    sub_total = round(total_amount, 2)
    sales_tax = round(sub_total * 0.1, 2)  # Assuming 10% sales tax
    total_amount = round(sub_total + sales_tax, 2)
    balance = total_amount

    # OCR text input
    ocr_text = f"Receipt Adress:{address} Te1:{phone_number} Date:{date} "
    for item in items:
        ocr_text += f"{item['item_name']} {item['price']} "
    ocr_text += f"AMOUNT {total_amount} Sub-total {sub_total} Sales Tax {sales_tax} Balance {balance} {shop_name} {shop_name}.com"

    # JSON output
    json_output = {
        "shop_name": shop_name,
        "address": address,
        "phone_number": phone_number,
        "date": date,
        "items": items,
        "total_amount": total_amount,
        "sub_total": sub_total,
        "sales_tax": sales_tax,
        "balance": balance
    }
    
    return ocr_text, json_output

# Generate the dataset
dataset = []
for _ in range(100000):  # Generate 10,000 examples
    ocr_text, json_output = generate_receipt()
    dataset.append({"input": ocr_text, "output": json.dumps(json_output)})



# Save to a file
with open("synthetic_receipts.json", "w") as f:
    json.dump(dataset, f, indent=4)


print(dataset)