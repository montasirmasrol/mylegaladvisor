import os
import json
from datetime import datetime, timedelta
import pickle
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def _get_credentials_and_token_paths():
	"""
	Resolve credentials and token storage paths in a portable way.
	Priority:
	1) Django settings: GOOGLE_CALENDAR_CREDENTIALS / GOOGLE_CALENDAR_TOKEN
	2) Environment variables: GOOGLE_CALENDAR_CREDENTIALS / GOOGLE_CALENDAR_TOKEN
	3) Project BASE_DIR fallback
	"""
	base_dir = getattr(settings, 'BASE_DIR', os.getcwd())
	cred_from_settings = getattr(settings, 'GOOGLE_CALENDAR_CREDENTIALS', None)
	token_from_settings = getattr(settings, 'GOOGLE_CALENDAR_TOKEN', None)
	cred_from_env = os.getenv('GOOGLE_CALENDAR_CREDENTIALS')
	token_from_env = os.getenv('GOOGLE_CALENDAR_TOKEN')

	credentials_file = cred_from_settings or cred_from_env or os.path.join(base_dir, 'credentials.json')
	token_file = token_from_settings or token_from_env or os.path.join(base_dir, 'token.pickle')
	return credentials_file, token_file


def _ensure_google_libs():
	"""
	Lazily import Google libraries. This prevents ModuleNotFoundError at module import time
	and lets us return a helpful message when dependencies are missing.
	"""
	try:
		# For development only (OAuth on localhost)
		os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', '1')
		os.environ.setdefault('OAUTHLIB_RELAX_TOKEN_SCOPE', '1')

		from google.oauth2.credentials import Credentials  # noqa: F401
		from google_auth_oauthlib.flow import InstalledAppFlow
		from google.auth.transport.requests import Request
		from googleapiclient.discovery import build
		from googleapiclient.errors import HttpError
		return InstalledAppFlow, Request, build, HttpError
	except ModuleNotFoundError as e:
		raise ImportError(
			"Google API libraries are not installed. "
			"Please install dependencies with: pip install -r requirements.txt"
		) from e

def get_credentials():
	"""Gets valid user credentials from storage.
	
	If nothing has been stored, or if the stored credentials are invalid,
	the OAuth2 flow is completed to obtain the new credentials.
	
	NOTE: For production, credentials should be stored per-user in the database.
	This is a simplified version using a single shared token file.
	"""
	InstalledAppFlow, Request, *_ = _ensure_google_libs()
	# Enable OAuth for development
	os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', '1')
	os.environ.setdefault('OAUTHLIB_RELAX_TOKEN_SCOPE', '1')
	
	creds = None
	CREDENTIALS_FILE, TOKEN_FILE = _get_credentials_and_token_paths()
	
	if not os.path.exists(CREDENTIALS_FILE):
		logger.error("credentials.json is missing. Please follow the setup guide in GOOGLE_CALENDAR_SETUP.md")
		raise FileNotFoundError(
			"credentials.json is missing. Please follow the setup guide in GOOGLE_CALENDAR_SETUP.md"
		)

	try:
		# Load saved token if it exists
		if os.path.exists(TOKEN_FILE):
			with open(TOKEN_FILE, 'rb') as token:
				creds = pickle.load(token)
				logger.info("Loaded existing credentials from token.pickle")
	except Exception as e:
		logger.warning(f"Error loading token file: {e}")
		creds = None
	
	try:
		# If no valid credentials available, let user log in
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				logger.info("Token expired, refreshing...")
				creds.refresh(Request())
			else:
				logger.info("No valid credentials found, initiating OAuth flow...")
				flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
				creds = flow.run_local_server(
					port=0,  # Use a random available port
					prompt='consent',
					authorization_prompt_message='Please visit this URL to authorize access:',
					success_message='Authorization successful! You can close this window.'
				)
			# Save the credentials for the next run
			with open(TOKEN_FILE, 'wb') as token:
				pickle.dump(creds, token)
				logger.info("Saved credentials to token.pickle")
	except Exception as e:
		logger.error(f"Error in OAuth flow: {e}")
		raise Exception(f"Failed to authenticate with Google Calendar: {str(e)}")
	
	return creds

def create_meet_link(appointment):
	"""Create a Google Meet link for the appointment"""
	# Ensure Google libraries are available (lazy import)
	_, _, build, HttpError = _ensure_google_libs()
	try:
		if not appointment.lawyer.email or not appointment.user.email:
			logger.error("Lawyer or user email is missing")
			raise ValueError("Both lawyer and user must have valid email addresses")

		creds = get_credentials()
		service = build('calendar', 'v3', credentials=creds)
		
		# Convert appointment time to datetime
		start_time = datetime.combine(appointment.appointment_date, appointment.appointment_time)
		end_time = start_time + timedelta(hours=1)  # Default 1-hour duration
		
		lawyer_name = appointment.lawyer.get_full_name() or appointment.lawyer.username
		user_name = appointment.user.get_full_name() or appointment.user.username
		
		# Create event
		event = {
			'summary': f'Legal Consultation: {lawyer_name} with {user_name}',
			'description': (
				f'Online legal consultation\n\n'
				f'Lawyer: {lawyer_name}\n'
				f'Client: {user_name}\n'
				f'Consultation Type: {appointment.get_consultation_type_display()}\n\n'
				f'Please join the meeting at the scheduled time using the Google Meet link.'
			),
			'start': {
				'dateTime': start_time.isoformat(),
				'timeZone': settings.TIME_ZONE,
			},
			'end': {
				'dateTime': end_time.isoformat(),
				'timeZone': settings.TIME_ZONE,
			},
			'conferenceData': {
				'createRequest': {
					'requestId': f'appointment-{appointment.id}-{start_time.strftime("%Y%m%d%H%M")}',
					'conferenceSolutionKey': {
						'type': 'hangoutsMeet'
					}
				}
			},
			'attendees': [
				{'email': appointment.lawyer.email},
				{'email': appointment.user.email},
			],
			'reminders': {
				'useDefault': False,
				'overrides': [
					{'method': 'email', 'minutes': 60},
					{'method': 'popup', 'minutes': 10},
				],
			},
		}
		
		try:
			event = service.events().insert(
				calendarId='primary',
				body=event,
				conferenceDataVersion=1,
				sendUpdates='all'  # Send email notifications to attendees
			).execute()
			
			logger.info(f"Created Google Calendar event with ID: {event.get('id')}")
			
			# Return the Meet link
			if 'conferenceData' in event and 'entryPoints' in event['conferenceData']:
				for entryPoint in event['conferenceData']['entryPoints']:
					if entryPoint['entryPointType'] == 'video':
						return entryPoint['uri'], event['id']
			
			logger.error("No conference data found in created event")
			raise Exception("Failed to get meeting link from created event")
			
		except HttpError as e:
			logger.error(f"Google Calendar API error: {e}")
			if hasattr(e, 'reason'):
				raise Exception(f"Google Calendar API error: {e.reason}")
			raise e
			
	except Exception as e:
		logger.error(f"Error creating Meet link: {str(e)}")
		raise Exception(f"Failed to create Google Meet link: {str(e)}")

def delete_meet_event(event_id):
	"""Delete a Google Calendar event"""
	# Ensure Google libraries are available (lazy import)
	_, _, build, _ = _ensure_google_libs()
	try:
		creds = get_credentials()
		service = build('calendar', 'v3', credentials=creds)
		service.events().delete(calendarId='primary', eventId=event_id).execute()
		return True
	except Exception as e:
		print(f"Error deleting event: {e}")
		return False