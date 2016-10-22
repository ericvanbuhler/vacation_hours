# Vacation Hours Counter for Google Calendar

This python script securely connects to your Google Calendar and computes future accrued biweekly vacation hours.

## Google API Setup

Follow the instruction on this site to set up you Google API Authorization: https://developers.google.com/api-client-library/python/start/get_started

## Configuration Setup

Modify the configuration file with you vacation days per year that will accrue and the start and end date you'd like to run the script.

## Initial Calendar Setup

On the start day you chose, make an all-day event name "Vacation Hours: <insert starting hours>". The script uses this info as the starting point.

Any day which you'll be taking as vacation label with "Vacation Day" or "Half Vacation Day" and the script will either subtract 8 or 4 hours from the accrual, respectively.

Then just run the script!
