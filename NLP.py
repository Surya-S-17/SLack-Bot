
data1 = """LOGU SILKS ANLREADYMADES 3/44BErode Main Road Near Weekly Market Perumanallur,Tirupur-641 666. Phone0421-23519359952488335 GSTIN:33AWAPS4959E1ZF CA TAX INVOICE Bill No: 000991/24-25 NAME:KALADEVI Add: Date06/05/24 PH: 6383018546 Time: 02:41PM Particulars Qty MRP GST%Amount LINING PES 6.00 45.00 5 270.00 BLOUSE PES SILK 1.00 95.00 5 95.00 BLOUSE COTTON SILK PES 1.00 145.00 145.00 FALLS 2.00 30.00 5 60.00 FALLS 1.00 25.00 5 25.00 Total MRP: 595.00 Tot Items: 5 Tot Disc: 15.00 Tot Qty: 11 Round off: 0.00 Net Amt : 580.00 GST DETAILS: % Amt 5 27.62 LOGUSILKS USER NAME: Terms & Conditlon- 1.No Cash Return 2.Please Retaln Bill Copy & the Tag 3.Exchange or Garments within 7 working days 4.Altered/Used/Washed garments will not be considered for an Exchange 5.Blouse, Cloth & Innerwears cant be exchan 7.Offer Garments cannot be exchange. E & OEFor LOGU SILKS AND READYMADES" THANK YOUIVISIT AGAIN!! 991"""



from langchain_community.llms import Ollama

llm = Ollama(model="phi3")

def extract(data):
    prompt =( f"""### Instruction:
    You are POS receipt data expert, parse, detect, recognize and convert following receipt OCR image result into structured receipt data object.
    Don't make up values not in the input. Output must be a well-formed JSON object, give it as a dictionary which can later converted into json by json.load().

    ### Input:
    {data}

    ### Output:
    shop name:
    date:
    items:[]
    total amount:
    """)
    response=llm.invoke(prompt)
    liss=[]

    return response

data= extract(data1)





print(data)

import json
json_data = json.loads(data)

# Extract required information
shop_name = json_data["shop_name"]
date = json_data["date"]
items = [item["description" or "item_code"] for item in json_data["items"]]
total_amount = json_data["total_amount"]

print(f"Shop Name: {shop_name}")
print(f"Date: {date}")
print(f"Items: {items}")
print(f"Total Amount: {total_amount}")