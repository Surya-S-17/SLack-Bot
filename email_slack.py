import smtplib

email="22d152@psgitech.ac.in"
receive="suryait263@gmail.com"

def send_email(emp_id,string):
    subject= f"EXPENSE REPORT {emp_id}"
    message= string

    text = f"Subject: {subject}\n\n{message}"
    server =smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()

    server.login(email,"sxbmfatghybkjehn")

    server.sendmail(email,receive,text)

    print("sent")
