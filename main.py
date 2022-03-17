import poplib
import const
import smtplib
import ssl
import imaplib
import email
import random
from itertools import chain
from email.header import decode_header

port = 465
context = ssl.create_default_context()
sender_email = const.EMAIL
receiver_email = const.EMAIL
pop3_server = 'pop.gmail.com'


def get_stat_data():
    data = {}
    for i in range(10):
        mail = email_obj.retr(message_num - i)[1]
        data.update({mail[10].decode("UTF-8")[8::]: mail[12].decode('UTF-8')})
    return data


def make_stats_message(data):
    text = "Subject:Mail Test\n\n"
    for theme in data:
        body = data[theme]
        count_letters = len([i for i in theme if i.isalpha()]) + len([i for i in body if i.isalpha()])
        count_numbers = len([i for i in theme if i.isdigit()]) + len([i for i in body if i.isdigit()])
        text += const.MESSAGE.format(Theme=theme, Body=body,
                                        Count_of_letters=count_letters, Count_of_numbers=count_numbers) + "\n"
    return text


def generate_list():
    chr_range = list(chain(range(48, 58), range(65, 91), range(97, 123)))
    return [chr(i) for i in [random.choice(chr_range) for _ in range(10)]]


def get_text():
    return "Subject:" +\
           "".join(generate_list()) + "\n" +\
           "".join(generate_list())


def send_stats(data1):
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(const.EMAIL, const.PASSWORD)
        resp = server.sendmail(sender_email, receiver_email, make_stats_message(data1))
        if resp:
            print("Stats not send")
        else:
            print("Stats send")


def send_ten_mails():
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(const.EMAIL, const.PASSWORD)
        for i in range(10):
            resp = server.sendmail(sender_email, receiver_email, get_text())
            if len(resp) > 0:
                print(f"Message {i+1} not send")
                for j in resp:
                    print(resp[j])
            else:
                print(f"Message {i+1} send")


def delete_mail(data):
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(const.EMAIL, const.PASSWORD)
    imap.select("INBOX")
    for subject in data:
        status, messages = imap.search(None, f'SUBJECT "{subject}"')
        messages = messages[0].split()
        for mail in messages:
            _, msg = imap.fetch(mail, "(RFC822)")
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


while __name__ == '__main__':
    send_ten_mails()

    email_obj = poplib.POP3_SSL(pop3_server)
    email_obj.user(const.EMAIL)
    email_obj.pass_(const.PASSWORD)
    message_num = email_obj.stat()[0]

    send_stats(get_stat_data())

    delete_mail(get_stat_data())

    exit()








