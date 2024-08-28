from langchain_community.llms import Ollama

llm = Ollama(model="phi3")

prompt="""**Prompt:**

Create a digital bill from the extracted text of a receipt. The receipt text includes various pieces of information such as the shop name if available,date, items purchased, and total amounts. However, some information might be missing or not available.

Extracted text: 
```
('Adress:1234Lorem Ipsum,Dolor', 0.9805384278297424) 
('Te1:123-456-7890', 0.9793164730072021) 
('Date:01-01-2018', 0.9802768230438232) 
('10:35', 0.9892295598983765) 
('biriyani', 0.9978181719779968) 
('6.50', 0.9998798966407776) 
('dosa', 0.9976849555969238) 
('7.50', 0.9998290538787842) 
('mint lime', 0.9698657989501953) 
('48.00', 0.999677836894989) 
('Amet', 0.9942843914031982) 
('9.30', 0.9995850324630737) 
('dairy milk', 0.996554434299469) 
('11.90', 0.9995803833007812) 
('sweet beeda', 0.9768193960189819) 
('1.20', 0.9992435574531555) 
('Sed Do', 0.9294896721839905) 
('0.40', 0.9997846484184265) 
('AMOUNT', 0.9958465099334717) 
('84.80', 0.9999648332595825) 
('Sub-total', 0.9950140714645386) 
('76.80', 0.9998213648796082) 
('Sales Tax', 0.983623206615448) 
('8.00', 0.9998384714126587) 
('Balance', 0.9951011538505554) 
('84.80', 0.9997941255569458)
```

**Requirements:**

1. Extract and include the following information if available:
   - Shop name (e.g., "cafe coffe restraurant")
   - Date of purchase
   - Items purchased
   - Total amount
   - Catogory of items (e.g., "food expense")
   
2. If any of the above pieces of information are not present in the extracted text, specify "not available" next to the corresponding field.

3. Categorize items purchased into an expense category (e.g., food expense, travel expenses, electronic expense). If unable to categorize, specify "category: unavailable" in catogory column.

4. Ensure that the generated digital bill contains only relevant information and does not include any extraneous content.

5. give only 

**Example Output:**

```
Shop name: not available

Date: 01-01-2018

Items purchased:
1.biriyani
2.dosa
3.mint lime
4.Amet
5.dairy milk
6.sweet beeda

Total amount: $84.80

catogory: food
```


like this provide the same for :"""


extracted_text="""Extracted text: ('65C:1', 0.5510744452476501) ('etlo', 0.64700847864151) ('CE BLACKCDFFE', 0.9324168562889099) ('82,000', 0.9539313316345215) ('AVOCADO COFFEE', 0.9210839867591858) ('61,000', 0.9784939885139465) ('UDO', 0.5550515651702881) ('CHIKEN KATSU FF', 0.9458047151565552) ('51,000', 0.8939609527587891) ('SUSTOTAL', 0.6952725648880005) ('194,000', 0.9521867036819458) ('DISCOONT', 0.7565416097640991) ('19,400', 0.9660425782203674) ('TOTAL', 0.7556143999099731) ('174,600', 0.9035593271255493) ('CASH', 0.9515474438667297) ('200,000', 0.9780449867248535) ('CHANGE', 0.9885963797569275) ('25,400', 0.874233067035675)"""

response=llm.invoke(prompt+extracted_text)

print(response)