from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

from datetime import datetime, timedelta, date

import json

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Vacation Hours'

WEEKS_PER_YEAR = 52

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials
    
def delete_existing_events(service, new_datetime):
    eventsResult = service.events().list(
        calendarId='primary',
        timeMin=new_datetime.isoformat() + 'Z',
        timeMax=(new_datetime + timedelta(days=1)).isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime',
        q='Vacation Hours:'
        ).execute()
    events = eventsResult.get('items', [])
    
    if not events:
        print('No existing events found')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print('Delete:', start, event['summary'])
        event_id = event['id']
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        
def add_new_event(service, new_date, new_hours):
    new_event = {
      'summary': 'Vacation Hours: ' + str(new_hours)[:5],
      'start': {
        'date': new_date.isoformat()[:10],
      },
      'end': {
        'date': new_date.isoformat()[:10],
      },
      'reminders': {
        'useDefault': True,
      },
    }

    new_event = service.events().insert(calendarId='primary', body=new_event).execute()
    start = new_event['start'].get('dateTime', new_event['start'].get('date'))
    print ('Create:', start, (new_event.get('summary')))
          

def main():
    # Get user credentials and set up link
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    # Load config from file
    with open('config.json') as config_file:
        conf = json.load(config_file)

    # Find starting 'Vacation Hours:' event
    start_year = conf["start_year"]
    start_month = conf["start_month"]
    start_day = conf["start_day"]
    start_datetime = datetime(start_year, start_month, start_day, 0, 0, 0, 0, None)
    
    end_year = conf["end_year"]
    end_month = conf["end_month"]
    end_day = conf["end_day"]
    end_datetime = datetime(end_year, end_month, end_day, 0, 0, 0, 0, None)
    
    eventsResult = service.events().list(
        calendarId='primary',
        timeMin=start_datetime.isoformat() + 'Z',
        timeMax=(start_datetime + timedelta(days=1)).isoformat() + 'Z',
        maxResults=1,
        singleEvents=True,
        orderBy='startTime',
        q='Vacation Hours:'
        ).execute()
    events = eventsResult.get('items', [])
    
    if not events:
        print('No start event found!')
        # xxx:Should crash here
    event = events[0]
    start = event['start'].get('dateTime', event['start'].get('date'))
    print('Start:',start, event['summary'])
    
    # Parse out hours
    start_hours = float(event['summary'][16:])

    # Compute biweekly increments
    prev_datetime = (start_datetime + timedelta(days=1))
    new_datetime = (start_datetime + timedelta(days=14))
    new_hours = start_hours

    # Compute vacation housr increment
    biweekly_vacation_hours = (conf["vacation_days_per_year"]*8/WEEKS_PER_YEAR)*2 
    
    while (new_datetime < end_datetime):
      new_hours = new_hours + biweekly_vacation_hours

      # Find any vacation days between the last date and the current date
      eventsResult = service.events().list(
          calendarId='primary',
          timeMin=prev_datetime.isoformat() + 'Z',
          timeMax=new_datetime.isoformat() + 'Z',
          singleEvents=True,
          orderBy='startTime',
          q='Vacation Day'
          ).execute()
      events = eventsResult.get('items', [])
      
      if not events:
          print('No vacation days found')
      for event in events:
          start = event['start'].get('dateTime', event['start'].get('date'))
          print('Found:', start, event['summary'])
          new_hours = new_hours - 8
      
      # Delete event if existing
      delete_existing_events(service, new_datetime)
      
      # Add new event
      new_date = date(new_datetime.year, new_datetime.month, new_datetime.day)
      add_new_event(service, new_date, new_hours)
      
      prev_datetime = (new_datetime + timedelta(days=1))
      new_datetime = (new_datetime + timedelta(days=14))

if __name__ == '__main__':
    main()
