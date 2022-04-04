import smtplib
from email.message import EmailMessage

def send_mail(sender_mail, sender_passwd, receiver_mail, message_text):
    msg = EmailMessage()
    msg.set_content(message_text)
    msg['From'] = sender_mail
    msg['To'] = receiver_mail
    msg['Subject'] = "Text"
    server = smtplib.SMTP("smtp.gmail.com", port=587)
    try:
        server.starttls()
        server.login(sender_mail, sender_passwd)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        server.quit()
        print(e)
