import os
import datetime


def log_booking(date_desired, booking_id):
    today_str = str(datetime.date.today())
    filename = os.path.abspath(os.path.join("bookings" + ".pwz"))
    with open(filename, "a") as fout:
        entry = f"\nDate Reserved = {date_desired}, Reserved On = {today_str}, reservation_id = {booking_id}"
        fout.write(entry)


def check_booking(date_desired):
    filename = os.path.abspath(os.path.join("bookings" + ".pwz"))
    data = []
    if os.path.exists(filename):
        with open(filename) as fin:
            for entry in fin.readlines():
                data.append(entry.rstrip())
    for i in range(len(data)):
        if f"Date Reserved = {date_desired}" in data[i].split(","):
            return True
    return False
