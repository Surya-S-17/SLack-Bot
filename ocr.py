
import os
from paddleocr import PaddleOCR, draw_ocr
from pdf2image import convert_from_path
import numpy as np
import cv2
from langchain_community.llms import Ollama

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


slm = Ollama(model="phi3")
# Initialize PaddleOCR
paddleocr = PaddleOCR(lang="en", ocr_version="PP-OCRv4", show_log=False, use_gpu=True)

def paddle_scan(paddleocr, img_path_or_nparray):
    result = paddleocr.ocr(img_path_or_nparray, cls=True)
    result = result[0]
    boxes = [line[0] for line in result]  # bounding box
    txts = [line[1][0] for line in result]  # raw text
    scores = [line[1][1] for line in result]  # scores
    return txts, result

def process_image(image_path):
    image = cv2.imread(image_path)
    return paddle_scan(paddleocr, image)

def process_pdf(pdf_path):
    pages = convert_from_path(pdf_path)
    all_texts = []
    all_results = []

    for page in pages:
        page_array = np.array(page)
        page_texts, page_results = paddle_scan(paddleocr, page_array)
        all_texts.extend(page_texts)
        all_results.extend(page_results)

    return all_texts, all_results

def process_file(file_path):
    if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
        return process_image(file_path)
    elif file_path.lower().endswith('.pdf'):
        return process_pdf(file_path)
    else:
        raise ValueError("Unsupported file format. Please provide an image or PDF file.")

# Example usage:
file_path = "Safari.pdf"  # Replace with the actual file path
receipt_texts, receipt_boxes = process_file(file_path)
print(receipt_texts)
ex = " ".join(receipt_texts)
print("\n\n",ex)



def extract_info(data):
    prompt =( f"""### Instruction:
    You are POS receipt data expert, parse, detect, recognize and convert following receipt OCR image result into structured receipt data object.
    Don't make up values not in the input. Output must be as a dictionary which can later converted into json object by json.load(),consider the rule that output must be as specified.
    strictly don't give output as   ```json``` give as a dict
             
    ### Note:
    if anything couldn't be found specify it as "NA"
    strictly don't give output as   ```json``` give as a dict
    inside items list give item_name in each dict
    
    ### example input and Output:

    "input": "LOGU SILKS ANLREADYMADES 3/44BErode Main Road Near Weekly Market Perumanallur,Tirupur-641 666. Phone0421-23519359952488335 GSTIN:33AWAPS4959E1ZF CA TAX INVOICE Bill No: 000991/24-25 NAME:KALADEVI Add: Date06/05/24 PH: 6383018546 Time: 02:41PM Particulars Qty MRP GST%Amount LINING PES 6.00 45.00 5 270.00 BLOUSE PES SILK 1.00 95.00 5 95.00 BLOUSE COTTON SILK PES 1.00 145.00 145.00 FALLS 2.00 30.00 5 60.00 FALLS 1.00 25.00 5 25.00 Total MRP: 595.00 Tot Items: 5 Tot Disc: 15.00 Tot Qty: 11 Round off: 0.00 Net Amt : 580.00 GST DETAILS: % Amt 5 27.62 LOGUSILKS USER NAME: Terms & Conditlon- 1.No Cash Return 2.Please Retaln Bill Copy & the Tag 3.Exchange or Garments within 7 working days 4.Altered/Used/Washed garments will not be considered for an Exchange 5.Blouse, Cloth & Innerwears cant be exchan 7.Offer Garments cannot be exchange. E & OEFor LOGU SILKS AND READYMADES\" THANK YOUIVISIT AGAIN!! 991",
    dict(
    "output": [
      ["LOGU SILKS ANLREADYMADES", "ORG"],
      ["06/05/24", "DATE"],
      ["LINING PES", "ITEM"],
      ["BLOUSE PES SILK", "ITEM"],
      ["BLOUSE COTTON SILK PES", "ITEM"],
      ["FALLS", "ITEM"],
      ["FALLS", "ITEM"],
      ["595.00", "TOTAL_AMOUNT"]
    ]
    )
             
    generate output for this input 
             
    input ----> {data}
    """)
    response=slm.invoke(prompt)
    liss=[]

    return response

y=extract_info(ex)
print("\n\n",y)

def extract_entity(data):
    prompt =( f"""### Instruction:
    You are POS receipt data expert, parse, detect, recognize and extract following structured receipt data object into a list that should contain required entity.
    Don't make up values not in the input. Output must be as a list of 4 elements, they were name of the organisation,date,total amount,expense category.
    
    rules for each value in the list
    1.name of the organisation :
             it should be the first element of the list
             name should be extracted from the given input only
             if the name is not found make the first value of list as 0
    2.Date:
             it should be the second element of the list
             date should be extracted from the given input only
             if the date is not found make the second value of list as 0
    3.total_amount:
             it should be the third element of the list
             total amount should be extracted from the given input only
             total amount may given as net amount, amount, total, grand total,etc,..
             ensure that total amount is the highest amount value in the input
    4.expense_category:
             it should be the fourth element of the list
             it should be classified based on the name of the organisation and items name 
             it can have any of these four values ["food","hotel","electronic","travel"]

             
             
    ### Note:
    if anything couldn't be found specify it as 0
    strictly give output as list don't generate any other unneccessary contents


    ### example input and Output:

    "input": "dict([
        dict("text": "VIEW ONLY FlightBridge Air Travel Receipt", "type": "ORG"),
        dict("text": "1/17/2e+002", "type": "DATE"),
        dict("text": "United Airlines", "type": "ORG"),
        dict("text": "SBA to KOA Tue, 1 Feb 2022", "type": "LOCATION"),
        dict("text": "United Airlines", "type": "ORG"),
        dict("text": "KOA to SBA Sun, 6 Feb 2022", "type": "LOCATION"),
        dict("text": "Economy - Non-Refundable", "type": "CLASS"),
        dict("text": "9h 9m", "type": "TIME"),
        dict("text": "10:00 - 20:43", "type": "FLIGHT_DETAILS"),
        dict("text": "Passenger Name: Smith, John KRTQDO Ticketed Payment Information Base Fare", "type": "PASSENGER_INFO"),
        dict("text": "Total 389.60", "type": "TOTAL_AMOUNT")
    ]
    )",
    
    "output": ["VIEW ONLY FlightBridge Air Travel Receipt","1 Feb 2022","389.60","travel"]
    ]
             
    generate output for 
    
    input----> {data}
    
    """)
    response=slm.invoke(prompt)
    liss=[]

    return response

ress=[]
for _ in range (10):
    z=extract_entity(y)
    my_list = eval(z)
    ress.append(my_list)
print(ress)

def extract_check(ress):
    prompt =( f"""### Instruction:
    
    rules for each value in the list
    1.name of the organisation :
             it should be the first element of the list
             name should be extracted from the given input only
             if the name is not found make the first value of list as 0
    2.Date:
             it should be the second element of the list
             date should be extracted from the given input only
             if the date is not found make the second value of list as 0
    3.total_amount:
             it should be the third element of the list
             total amount should be extracted from the given input only
             total amount may given as net amount, amount, total, grand total,etc,..
             ensure that total amount is the highest amount value in the input
    
    ##note 
       i have given a list which contains 10 lists which should follow the rules based on that rules return a perfect list from that 10 lists
       don't makeup answers on your own, just return a single list

             
    input list---> {ress}
    give output list for my above given input list
    """)
    response=slm.invoke(prompt)
    liss=[]

    return response

l=extract_check(ress)
print("\n\n",l)


ls = eval(l)

print(ls)
print(type(ls))
