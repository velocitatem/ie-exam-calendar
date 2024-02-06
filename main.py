calendar_url = "https://blackboard.ie.edu/webapps/calendar/calendarFeed/61199f0ad9ef4b47a9decae464e474e9/learn.ics"
calendar_name = "IE University"
from datetime import datetime
from icalendar import Calendar
import requests
import pandas as pd

def get_calendar(calendar_url):
    # return from cache if exists
    try:
        with open(f"{calendar_name}.ics", "rb") as f:
            return Calendar.from_ical(f.read())
    except FileNotFoundError:
        pass
    response = requests.get(calendar_url)
    cal = Calendar.from_ical(response.text)
    # cache the calendar
    with open(f"{calendar_name}.ics", "wb") as f:
        f.write(response.content)
    return cal

def get_events(cal):
    events = []
    for component in cal.walk():
        if component.name == "VEVENT":
            event = {
                "summary": component.get("summary"),
                "description": component.get("description"),
                "start": component.get("dtstart").dt,
                "end": component.get("dtend").dt,
                # extact from summary session number if exists (Ses. [nuber]) can also be (Ses. [number]-[number])
                "session": component.get("summary").split("Ses. ")[-1].split(" ")[0] if "Ses. " in component.get("summary") else None
            }
            event["session"] = event["session"].replace("(", "").replace(")", "").replace("Ses.", "").replace("Ses", "").strip() if event["session"] else None
            events.append(event)
    return events

def get_events_df(events):
    df = pd.DataFrame(events)
    df["start"] = pd.to_datetime(df["start"])
    df["end"] = pd.to_datetime(df["end"])
    return df

def get_session_date(session_number, course, df):
    return df.loc[df["summary"].str.contains(course) & df["session"].str.contains(str(session_number))]

import json
def get_course_data():
    return {
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

import streamlit as st
from streamlit_timeline import timeline
def main():
    cal = get_calendar(calendar_url)
    events = get_events(cal)
    df = get_events_df(events)
    finals = get_course_data()
    final_dates = {}
    timeline_config = {
        "title": {
            "media": {
                "url": "",
                "caption": " <a target=\"_blank\" href=''>credits</a>",
                "credit": ""
                },
            "text": {
                "headline": "Welcome to<br>IE BSCAI Year 2 Course Timeline",
                "text": "<p> This timeline shows the finals and midterms for the year 2 courses at IE University</p>"
                }
            },
        "events": []
    }

    for final in finals:
        course = final
        final = finals[final]
        if "midterm" in final:
            mid= get_session_date(final["midterm"], course, df)
        final = get_session_date(final["final"], course, df)
        print(final)
        if final.shape[0] > 0:
            timeline_config["events"].append({
                "media": {
                    "url": "",
                    "caption": f"Session {final['session']}",
                    "credit": ""
                },
                "start_date": {
                    "year": int(final["start"].dt.year),
                    "month": int(final["start"].dt.month),
                    "day": int(final["start"].dt.day)
                },
                "text": {
                    "headline": f"{course} Final",
                    # day of the week, just get value not object type or anything else
                    "text": final['start'].dt.day_name().values[0]

                }
            })
        if mid.shape[0] > 0:
            print(mid.shape)
            timeline_config["events"].append({
                "media": {
                    "url": "",
                    "caption": f"Session {mid['session']}",
                    "credit": ""
                },
                "start_date": {
                    "year": int(mid["start"].dt.year),
                    "month": int(mid["start"].dt.month),
                    "day": int(mid["start"].dt.day)
                },
                "text": {
                    "headline": f"{course} Midterm",
                    # day of the week, just get value not object type or anything else
                    "text": mid['start'].dt.day_name().values[0]
                }
            })


    print(timeline_config)
    # streamlit timeline:
    # turn to json
    timeline(timeline_config)




if __name__ == "__main__":
    main()
