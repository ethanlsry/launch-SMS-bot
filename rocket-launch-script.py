#get launch schedule
import requests
import json
from apscheduler.schedulers.blocking import BlockingScheduler
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import ssl

def execute_schedule_notification():
    resp = requests.get('https://fdo.rocketlaunch.live/json/launches/next/5')
    if (resp.status_code != 200):
        print(f'issue with API call; error {resp.status_code}') #abort
        
    data = json.loads(resp.text)

    email_message_content_html = "<html><head><link href='https://fonts.googleapis.com/css?family=Lato' rel='stylesheet'><style>body {font-family: 'Lato';font-size: 14px;}</style>Good evening. Here is the upcoming launch schedule:</head><body>"
    text_content = "Good evening. Here is next launch: \n\n"
    text_content_brief = "Next launch: \n\n"

    # Access specific fields
    num_of_launches_provided = 1 #increase for n number of launches
    for n in range(num_of_launches_provided):
        next_launch = data['result'][n]
        month = next_launch['est_date']['month']
        day = next_launch['est_date']['day']
        year = next_launch['est_date']['year']
        name = next_launch['name']
        vehicle = next_launch['vehicle']['name']
        provider = next_launch['provider']['name']
        description = next_launch['mission_description']
        location_place = next_launch['pad']['location']['name']
        location_country = next_launch['pad']['location']['country']

        email_message_content_html += f"<h4>{month}/{day}/{year} @ {location_place}, {location_country}</h4><ul>"
        email_message_content_html += f"<li>{name} via {vehicle}</li>"
        email_message_content_html += f"<li>{provider} provided</li>"

        text_content += f"{month}/{day}/{year} @ {location_place}, {location_country}"
        text_content += f"{name} via {vehicle}"
        text_content += f"{provider} provided"

        text_content_brief += f"{month}/{day}/{year} @ {location_place}, {location_country} \n"
        text_content_brief += f"{name} via {vehicle} \n"
        text_content_brief += f"{provider} provided \n"

        desc_comparator = 'None'
        if not str(description) == desc_comparator:
            email_message_content_html += f"<li>{description}</li>"

        email_message_content_html += "</ul>"

    email_message_content_html += ("</body></html>")
    
    print(text_content_brief)

    #customize sensitive variables:
    phone_number = ''
    email_address = ''
    twilio_api_key = ''
    
    #text next launch
    resp = requests.post('https://textbelt.com/text', {
    'phone': phone_number,
    'message': text_content_brief,
    'key': 'textbelt',
    })
    print(resp.json())

    #send email using twilio sendgrid
    # message = Mail(
    #     from_email=email_address,
    #     to_emails=email_address,
    #     subject='Upcoming Rocket Launches Bot',
    #     html_content=text_message_content)
    # try:
    #     sg = SendGridAPIClient(os.environ.get(twilio_api_key))
    #     response = sg.send(message)
    #     # print(response.status_code)
    #     # print(response.body)
    #     # print(response.headers)
    # except Exception as e:
    #     print(e)
        
execute_schedule_notification()

#run each sunday and thursday
sched = BlockingScheduler()
sched.add_job(execute_schedule_notification, 'cron', day='3,7', hour='20')
sched.start()

try:
    while True:
        pass
except (KeyboardInterrupt, SystemExit):
    # Shutdown the scheduler on exit
    sched.shutdown()