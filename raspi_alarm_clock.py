import httplib2
import os
import time
from feed.date.rfc3339 import tf_from_timestamp #also for the comparator
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
import datetime
import ConfigParser
from players import spop_play

settings = ConfigParser.ConfigParser()
settings.read('config.ini')

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Raspi Volumio Alarm Clock'




try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None




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
                                   'calendar-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print 'Storing credentials to ' + credential_path
    return credentials

def main():
    """Fetches 10 upcoming events and plays spotify playlist if 1 occurs right now.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print 'Fetch the next 10 upcoming events'
    eventsResult = service.events().list(
        calendarId=settings.get('Calendar', 'GOOGLE_CALENDAR_ID'), timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print 'No upcoming events found.'
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        upcoming_event_start = time.strftime('%d-%m-%Y %H:%M',time.localtime(tf_from_timestamp(start)))
        print upcoming_event_start, event['summary']
        current_time = time.strftime('%d-%m-%Y %H:%M')
        if  upcoming_event_start == current_time:
            spop_play.play_music()


if __name__ == '__main__':
    main()