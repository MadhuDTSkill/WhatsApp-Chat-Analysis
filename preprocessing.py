import re
import pandas as pd
import numpy as np



def preprocess_data(data):
    data.replace('\u202f', ' ')
    initial_pattern = r"\d{1,2}/\d{1,2}/\d{1,2},\s\d{1,2}:\d{1,2}\s[PA]M\s-\s"

    messages = re.split(initial_pattern, data)[1:]
    messages = [message.replace('\n', '') if message.endswith('\n') else message for message in messages]
    
    dates = re.findall(initial_pattern, data)
    dates = [date.replace('\u202f', ' ')[:-3] for date in dates]

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    
    df['message_date'] = pd.to_datetime(df['message_date'], format='%m/%d/%y, %I:%M %p')

    users = []
    messages = []
    for message in df['user_message']:
        pattern = r'^([^\n:]+):\s([^\n:][\W\w]+)'
        match = re.match(pattern, message)
        if match:
            users.append(match.group(1))
            messages.append(match.group(2))
        else:
            users.append('Whatsapp')
            messages.append(message)

    df['user'] = users
    df['message'] = messages

    df['date'] = df['message_date'].dt.date
    df['year'] = df['message_date'].dt.year
    df['month'] = df['message_date'].dt.month_name()
    df['day'] = df['message_date'].dt.day
    df['day_name'] = df['message_date'].dt.day_name()
    df['hour'] = df['message_date'].dt.hour
    df['minute'] = df['message_date'].dt.minute
    df['meridiem'] = df['message_date'].dt.strftime('%p')
    
    df.drop(columns=['user_message', 'message_date', ], inplace=True)
    return df