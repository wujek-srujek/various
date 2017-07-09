#!/usr/bin/env python3

import os
import os.path
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

email = ''
password = ''
to = '@kindle.com'
group = 5

def send_email(s, i, paths):
    msg = MIMEMultipart()
    msg['Subject'] = 'Kindle docs ' + str(i)
    print(msg['Subject'])
    msg['From'] = email
    msg['To'] = to

    for path in paths:
        msg.attach(new_attachment(path))

    msg = msg.as_string()
    s.sendmail(email, to, msg)
    print()

def new_attachment(path):
    with open(path, 'rb') as book:
        attachment = MIMEBase('application', 'x-mobipocket-ebook')
        attachment.set_payload(book.read())
        fname = filename(path)
        print('  ', fname)
        attachment.add_header('Content-Disposition', 'attachment', filename=fname)
        encoders.encode_base64(attachment)
    return attachment

def filename(path):
    basename = os.path.basename(path)
    name, ext = os.path.splitext(basename)
    title, author = name.rsplit('-', 1)
    return title.strip() + ext

def main():
    s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    s.login(email, password)

    paths = []
    for root, dirs, files in os.walk('books'):
        for file in files:
            paths.append(os.path.join(root, file))

    i = 1
    for start in range(0, len(paths), group):
        send_email(s, i, paths[start:start+group])
        i += 1

    s.quit()

if __name__ == '__main__':
    main()
