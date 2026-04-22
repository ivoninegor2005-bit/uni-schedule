#!/bin/bash

URL="https://uspu.ru/education/eios/schedule/calendar/calendar_filter/calendar_БХ-2331_22.04.2026%2012%3A00%3A00_13.05.2026%2012%3A00%3A00.ics"

echo "Downloading ICS..."

curl --http1.1 \
     --retry 5 \
     --retry-delay 3 \
     --fail \
     -L "$URL" -o calendar.ics

echo "Done"