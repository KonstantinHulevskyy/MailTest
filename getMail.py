import poplib
import const
import smtplib
import ssl
import imaplib
import email
import random
from itertools import chain
from email.header import decode_header

port = 465  # For SSL
context = ssl.create_default_context()
sender_email = const.EMAIL
receiver_email = const.EMAIL
pop3_server = 'pop.gmail.com'
email_obj = poplib.POP3_SSL(pop3_server)
email_obj.user(const.EMAIL)
email_obj.pass_(const.PASSWORD)
# email_stat = email_obj.stat()
# num_of_msgs = email_stat[0]


def get_stat_data():
    data = {}
    for i in range(10):
        mail = email_obj.retr(i+1)[1]
        print(mail[10].decode("UTF-8")[10::], "\n", mail[12].decode('UTF-8'))
        data.update({mail[10].decode("UTF-8")[10::]: mail[12].decode('UTF-8')})
        print(len(data))
    return data


def make_stats_message(data):
    message = "Subject: Mail Test statistic\n"
    for theme in data:
        body = data[theme]
        count_letters = len([i for i in theme if i.isalpha()]) + len([i for i in body if i.isalpha()])
        count_numbers = len([i for i in theme if i.isdigit()]) + len([i for i in body if i.isdigit()])
        message += const.MESSAGE.format(Theme=theme, Body=body,
                                        Count_of_letters=count_letters, Count_of_numbers=count_numbers) + "\n"
    return message


def generate_list():
    chr_range = list(chain(range(48, 58), range(65, 91), range(97, 123)))
    return [chr(i) for i in [random.choice(chr_range) for _ in range(11)]]


def get_text():
    return "Subject:" +\
           "".join(generate_list()) + "\n" +\
           "".join(generate_list())


def send_stats():
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(const.EMAIL, const.PASSWORD)
        server.sendmail(sender_email, receiver_email, make_stats_message(make_stats_message(get_stat_data())))


def send_ten_mails():
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(const.EMAIL, const.PASSWORD)
        # TODO: Send email here
        for _ in range(10):
            server.sendmail(sender_email, receiver_email, get_text())


def delete_mail(data):
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(const.EMAIL, const.PASSWORD)
    imap.select("INBOX")
    for subject in data:
        status, messages = imap.search(None, f'SUBJECT "{subject}"')
        # messages = bytes(messages[0])
        messages = messages[0].split(b" ")
        for mail in messages:
            _, msg = imap.fetch(mail, "(RFC822)")
            # you can delete the for loop for performance if you have a long list of emails
            # because it is only for printing the SUBJECT of target email to delete
            for response in msg:
                if isinstance(response, tuple):
                    msg = email.message_from_bytes(response[1])
                    # decode the email subject
                    subject = decode_header(msg["Subject"])[0][0]
                    if isinstance(subject, bytes):
                        # if it's a bytes type, decode to str
                        subject = subject.decode()
                    print("Deleting", subject)
            # mark the mail as deleted
            imap.store(mail, "+FLAGS", "\\Deleted")
    imap.expunge()
