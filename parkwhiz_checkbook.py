"""Using the Arrive API to book at Mt. Bachelor via ParkWhiz
author: marcus_sharp
"""

import requests
import argparse
import datetime

from twilio.rest import Client

import booking_data

QUOTES_URL = "https://api.parkwhiz.com/v4/quotes/"
BOOKING_URL = "https://api.parkwhiz.com/v4/bookings/"
TOKEN_URL = "https://api.parkwhiz.com/v4/oauth/token?grant_type=password&scope=public&customer_email=<youremailhere>&customer_password=<your_parkwhiz_password>"


def get_event_id(desired_date):
    """Lists all the events avaiable at Mt. Bachelor"""
    url = "http://api.parkwhiz.com/v4/venues/478498/events"  # mt bachelor id = 478498
    resp = requests.get(url)
    events = resp.json()
    for event in events:
        if f"{desired_date}" in event["name"]:
            return event["id"]


def check_available(event_id):
    # 292 feet away is nordic location_id = 37788
    # 305 ft away is what we want. location_id = 37720
    url = f"{QUOTES_URL}?q=event_id:{event_id}&capabilities=capture_plate:always&response=bookable&return=curated"
    resp = requests.get(url)
    results = resp.json()
    quote_id = ""
    if results == []:
        quote_id = "Not Available"

    else:
        for result in results:
            if result["distance"]["straight_line"]["feet"] == 305:
                if (
                    result["purchase_options"][0]["space_availability"]["status"]
                    == "available"
                ):
                    quote_id = result["purchase_options"][0]["id"]

    return quote_id


def get_token():
    response = requests.post(TOKEN_URL)
    token_info = response.json()
    my_token = token_info["access_token"]
    return my_token


def attempt_booking(quote_id, license_plate, email, new_token, desired_date):
    """Leaving for now as it looks good, but need a token"""
    url = f"{BOOKING_URL}?final_price=0.00&quote_id={quote_id}&plate_number={license_plate}&email={email}&send_email_confirmation=True"
    payload = {}
    headers = {f"Authorization": "Bearer {new_token}"}
    response = requests.request("POST", url, headers=headers, data=payload)
    return response


def send_text(desired_date):
    account_sid = "<your_twilio_account_sid>"
    auth_token = "<your_twilio_auth_token>"
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f"{desired_date} has been booked on ParkWhiz.",
        from_="+1<twilio_phone_number>",
        to="+1<your_phone_number>",
    )


def log_output(desired_date, can_park):
    with open("log.txt", "a") as f:
        f.write(
            f"\nThe result of the search performed at {datetime.datetime.now()} was {desired_date} is {can_park}"
        )


def main():
    parser = argparse.ArgumentParser(description="get desired date")
    parser.add_argument(
        "--desireddate",
        required=True,
        default="Mar 3",
        type=str,
        help="Date in 3 letter titled month, day format example = Mar 3",
    )
    args = parser.parse_args()
    desired_date = args.desireddate
    is_already_booked = booking_data.check_booking(desired_date)
    if is_already_booked:
        print(f"Already have a reservation for {desired_date}.  Exiting....")
        exit()
    event_id = get_event_id(desired_date)
    quote_id = check_available(event_id)
    license_plate = "<your_license_plate>"
    email = "<your_email_for ParkWhiz>"
    if quote_id != "Not Available":
        new_token = get_token()
        book_response = attempt_booking(
            quote_id, license_plate, email, new_token, desired_date
        )
        if book_response.status_code == 201:
            # successfully booked
            book_result = book_response.json()
            booking_id = book_result[0].get("id")
            booking_data.log_booking(desired_date, booking_id)
            send_text(desired_date)


if __name__ == "__main__":
    main()
