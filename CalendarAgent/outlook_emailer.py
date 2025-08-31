# domains/calendar/outlook_emailer.py
import win32com.client

def send_email(to, subject, body):
    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)  # 0 = olMailItem
    mail.To = to
    mail.Subject = subject
    mail.Body = body
    mail.Send()
    print(f"📤 Email sent to {to}")
