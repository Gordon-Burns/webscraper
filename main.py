import requests
import selectorlib
import smtplib
import ssl
import os
import creds
import time
import sqlite3

URL = "http://programmer100.pythonanywhere.com/tours/"

connection = sqlite3.connect("data.db")


def scrape(url):
    """Scrape the page source from the URL"""
    response = requests.get(url)
    source = response.text
    return source


def extract(source):
    extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
    value = extractor.extract(source)["tours"]
    return value


def send_email(message):
    host = "smtp.gmail.com"
    port = 465

    username = creds.getusername()
    password = creds.get_password()
    receiver = creds.get_receiver()

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, receiver, message)


def store(extracted):
    row = extracted.split(",")
    row = [item.strip() for item in row]
    curser = connection.cursor()
    curser.execute("INSERT INTO EVENTS VALUES(?,?,?)", row)
    connection.commit()


def read(extracted):
    row = extracted.split(",")
    row = [item.strip() for item in row]
    band, city, date = row
    curser = connection.cursor()
    curser.execute("Select * from events where band = ? and city = ? and date = ?", (band, city, date))
    rows = curser.fetchall()
    return rows


if __name__ == "__main__":
    while True:
        scraped = (scrape(URL))
        extracted = extract(scraped)
        print(extracted)

        if extracted != "No upcoming tours":
            row = read(extracted)
            if not row:
                store(extracted)
                send_email(message=f"Hey, New event was found \n {extracted}")
        time.sleep(2)
