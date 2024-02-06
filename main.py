import requests
from icalendar import Calendar
import pandas as pd
import json
import streamlit as st
from streamlit_timeline import timeline
from datetime import datetime

class CalendarFetcher:
    def __init__(self, calendar_url, calendar_name):
        self.calendar_url = calendar_url
        self.calendar_name = calendar_name

    def fetch_calendar(self):
        # Implementing P_FetchCalendar
        try:
            with open(f"{self.calendar_name}.ics", "rb") as f:
                return Calendar.from_ical(f.read())
        except FileNotFoundError:
            pass
        response = requests.get(self.calendar_url)
        cal = Calendar.from_ical(response.text)
        self.cache_calendar(response.content)
        return cal

    def cache_calendar(self, calendar_data):
        # Implementing P_CacheCalendar
        with open(f"{self.calendar_name}.ics", "wb") as f:
            f.write(calendar_data)
        return "Cache successful"

class CalendarParser:
    def parse_calendar(self, cal):
        """
        Parses the iCalendar data and extracts relevant event details.

        Args:
            cal (Calendar): An iCalendar object.

        Returns:
            list of dict: A list of events, each represented as a dictionary.
        """
        events = []
        for component in cal.walk():
            if component.name == "VEVENT":
                event = {
                    "summary": str(component.get("summary")),
                    "description": str(component.get("description", "")),
                    "start": component.get("dtstart").dt,
                    "end": component.get("dtend").dt,
                    "location": str(component.get("location", "")),
                    # Additional fields can be extracted as needed
                }

                # Handling the case where summary might include session information
                if "Ses. " in event["summary"]:
                    event["session"] = self.extract_session_number(event["summary"])
                else:
                    event["session"] = None

                print(event)
                events.append(event)

        return events

    @staticmethod
    def extract_session_number(summary):
        """
        Extracts the session number from the event summary.

        Args:
            summary (str): The summary of the event.

        Returns:
            str or None: The extracted session number, or None if not found.
        """
        try:
            session_part = summary.split("Ses. ")[-1].split(" ")[0]
            session_number = session_part.replace("(", "").replace(")", "").strip()
            return session_number
        except IndexError:
            return None

import json

class EventProcessor:
    def __init__(self, course_data):
        """
        Initializes the EventProcessor with course data.

        Args:
            course_data (dict): A dictionary containing course names and their exam session numbers.
        """
        self.course_data = course_data

    def identify_sessions_exams(self, events):
        """
        Identifies sessions and exams from a list of events, using course data.

        Args:
            events (list of dict): A list of events, each represented as a dictionary.

        Returns:
            dict: A dictionary with two keys, 'sessions' and 'exams', each containing a list of respective events.
        """
        sessions = []
        exams = []

        for event in events:
            if self.is_exam(event):
                exams.append(event)
            else:
                sessions.append(event)

        sessions_exams = {
            'sessions': sessions,
            'exams': exams
        }

        return sessions_exams

    def is_exam(self, event):
        """
        Determines whether an event is an exam based on the course data.

        Args:
            event (dict): A dictionary representing an event.

        Returns:
            bool: True if the event is an exam, False otherwise.
        """
        for course, exam_info in self.course_data.items():
            if course in event['summary']:
                session = event.get('session')
                if session and int(session) in exam_info.values():
                    print(event['summary'])
                    return True
        return False

class TimelineGenerator:
    def generate_timeline(self, sessions_exams):
        """
        Generates timeline data from sessions and exams.

        Args:
            sessions_exams (dict): A dictionary with 'sessions' and 'exams' keys, each containing a list of events.

        Returns:
            list: A list of timeline events, each represented as a dictionary.
        """
        timeline_data = []

        for exam in sessions_exams['exams']:
            timeline_event = self.create_timeline_event(exam, event_type='exam')
            timeline_data.append(timeline_event)

        return timeline_data

    def create_timeline_event(self, event, event_type):
        """
        Creates a timeline event dictionary from an event.

        Args:
            event (dict): A dictionary representing an event.
            event_type (str): A string indicating the type of event ('session' or 'exam').

        Returns:
            dict: A dictionary representing a timeline event.
        """
        return {
            'start_date': {
                'year': event['start'].year,
                'month': event['start'].month,
                'day': event['start'].day
            },
            'end_date': {
                'year': event['end'].year,
                'month': event['end'].month,
                'day': event['end'].day
            },
            'text': {
                'headline': f"{event_type.title()}: {event['summary']}",
                'text': event.get('description', '')
            },
            # Additional fields or styling based on event type can be added here
        }


import streamlit as st
from streamlit_timeline import timeline

class Interface:
    def display_timeline(self, timeline_data):
        """
        Displays the timeline using Streamlit.

        Args:
            timeline_data (list): A list of timeline events, each represented as a dictionary.
        """
        # Initialize Streamlit app
        st.title("IE Exam Calendar Timeline")

        # Timeline configuration
        timeline_config = {
            "title": {
                "media": {
                    "url": "",  # URL to an image or logo if desired
                    "caption": "IE University",
                    "credit": "IE Exam Calendar Assistant"
                },
                "text": {
                    "headline": "IE University Exam and Session Timeline",
                    "text": "<p>Interactive timeline of exams and sessions.</p>"
                }
            },
            "events": timeline_data
        }

        # Display the timeline
        timeline(timeline_config)



def main():
    calendar_url = "https://blackboard.ie.edu/webapps/calendar/calendarFeed/61199f0ad9ef4b47a9decae464e474e9/learn.ics"
    calendar_name = "IE University"

    calendar_fetcher = CalendarFetcher(calendar_url, calendar_name)
    calendar = calendar_fetcher.fetch_calendar()

    calendar_parser = CalendarParser()
    events = calendar_parser.parse_calendar(calendar)


    event_data = {
    "MATRICES & LINEAR TRANSFORMATIONS": {
        "final": 30,
        "midterm": 14
    },
    "PROBABILITY FOR COMPUTING SCIENCE": {
        "final": 15,
        "midterm": 9
    },
    "COMPUTER ARCHITECTURE, NETWORK TECHNOLOGY & OPERATING": {
        "final": 30,
        "midterm": 19
    },
    "AI: MACHINE LEARNING FOUNDATIONS": {
        "final": 30,
        "midterm": 23
    },
    "AI: PERSONALITY AND EMOTION FOR AI DESIGN": {
        "final": 15
    }

}

    event_processor = EventProcessor(event_data)
    sessions_exams = event_processor.identify_sessions_exams(events)

    timeline_generator = TimelineGenerator()
    timeline_data = timeline_generator.generate_timeline(sessions_exams)

    interface = Interface()
    interface.display_timeline(timeline_data)

if __name__ == "__main__":
    main()
