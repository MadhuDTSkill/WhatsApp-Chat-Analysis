import pandas as pd
import spacy.cli
import spacy.cli.download
from urlextract import URLExtract
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
import spacy

nlp = None

try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    spacy.cli.download("en_core_web_md")
    nlp = spacy.load("en_core_web_md")


def format_number_short(number):
    """
    Convert large numbers into human-readable short form.
    Examples:
        1500 -> '1.5K'
        1000000 -> '1M'
        23000000 -> '23M'
        1250000000 -> '1.25B'
    """
    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.2f}B"
    elif number >= 1_000_000:
        return f"{number / 1_000_000:.2f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.2f}K"
    else:
        return str(number)


def stats(df: pd.DataFrame, selected_user: str):
    if selected_user != 'All':
        df = df[df['user'] == selected_user]

    # Total Messages
    all_messages = df['message'].to_list()
    total_messages = len(all_messages)

    # Total Words
    total_words = sum(len(message.split()) for message in all_messages)

    # Total Media Messages
    total_media_messages = df[df['message'] == '<Media omitted>'].shape[0]

    # Total Links
    extractor = URLExtract()
    total_links = sum(len(extractor.find_urls(message)) for message in all_messages)

    # Total Characters
    total_characters = sum(len(message) for message in all_messages)

    # Average Words per Message
    average_words = total_words // total_messages if total_messages > 0 else 0

    # Longest Message Length
    longest_message_length = len(max(all_messages, key=len)) if all_messages else 0

    # Shortest Message Length
    shortest_message_length = len(min(all_messages, key=len)) if all_messages else 0

    # Most Active Day (and its count)
    most_active_day = df['day_name'].value_counts().idxmax()
    most_active_day_count = df['day_name'].value_counts().max()

    # Number of Days Active
    active_days = df['date'].nunique()

    # Longest Streak of Consecutive Active Days
    all_dates = pd.to_datetime(df['date'].unique())
    all_dates = pd.Series(sorted(all_dates))
    streaks = (all_dates.diff() != pd.Timedelta(days=1)).cumsum()
    longest_streak = streaks.value_counts().max()

    # Longest Inactive Gap (in days)
    max_gap = all_dates.diff().max().days if len(all_dates) > 1 else 0

    return (
        format_number_short(total_messages),
        format_number_short(total_words),
        format_number_short(total_media_messages),
        format_number_short(total_links),
        format_number_short(total_characters),
        format_number_short(average_words),
        format_number_short(longest_message_length),
        format_number_short(shortest_message_length),
        most_active_day,
        format_number_short(active_days),
        format_number_short(longest_streak),
        format_number_short(max_gap)
    )


def most_busy_user(df: pd.DataFrame, selected_user: str):
    if selected_user != 'All':
        df = df[df['user'] == selected_user]
    return df['user'].value_counts().reset_index()


def create_wordcloud(df: pd.DataFrame, selected_user: str):
    if selected_user != 'All':
        df = df[df['user'] == selected_user]
    all_messages = df[df['message'] != '<Media omitted>']['message'].to_list()
    all_messages = ' '.join(all_messages)
    
    
    doc = nlp(all_messages)
    all_messages = ' '.join([token.text for token in doc if not token.is_stop and not token.is_punct])

    wordcloud = WordCloud(width=800, height=400, background_color='black').generate(all_messages)

    return wordcloud


def most_busy_month(df: pd.DataFrame, selected_user: str):
    if selected_user != 'All':
        df = df[df['user'] == selected_user]
    most_busy_month_df = df.groupby(['year', 'month']).count()['message'].reset_index()
    most_busy_month_df['busy_month'] = most_busy_month_df['month'] + ' - ' + most_busy_month_df['year'].astype(str)
    most_busy_month_df = most_busy_month_df[['busy_month', 'message']]
    return most_busy_month_df

def most_busy_day(df: pd.DataFrame, selected_user: str):
    if selected_user != 'All':
        df = df[df['user'] == selected_user]
    return df['day_name'].value_counts().reset_index()


def most_busy_week(df: pd.DataFrame, selected_user: str):
    if selected_user != 'All':
        df = df[df['user'] == selected_user]
    return df['week'].value_counts().reset_index()


def most_busy_hour(df: pd.DataFrame, selected_user: str):
    if selected_user != 'All':
        df = df[df['user'] == selected_user]

    most_busy_hour = df.groupby(['hour', 'meridiem']).count()['message'].reset_index()
    most_busy_hour.sort_values('hour', inplace=True)
    most_busy_hour['busy_hour'] = most_busy_hour['hour'] + ' ' + most_busy_hour['meridiem']
    most_busy_hour = most_busy_hour[['busy_hour', 'message']]
    return most_busy_hour


def heatmap_activity(df: pd.DataFrame, selected_user: str = 'All'):
    if selected_user != 'All':
        df = df[df['user'] == selected_user]

    user_activity = df.groupby(['day_name', 'hour', 'meridiem']).count()['message'].reset_index()
    user_activity['hour'] = user_activity['hour'].astype(str) + " " + user_activity['meridiem']
    user_activity.drop(columns=['meridiem'], inplace=True)
    heatmap_data = user_activity.groupby(['day_name', 'hour']).aggregate({'message': 'sum'}).unstack().fillna(0)

    ordered_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data = heatmap_data.reindex(ordered_days)

    return heatmap_data


def get_line_chat_of_message_history(df: pd.DataFrame, selected_user: str):
    if selected_user != 'All':
        df = df[df['user'] == selected_user]

    return df['date'].value_counts().reset_index()


def get_averages(df: pd.DataFrame, selected_user: str):
    if selected_user != 'All':
        df = df[df['user'] == selected_user]

    # 1. Average Messages Per Month
    avg_messages_per_month = df.groupby('month')['message'].count().mean()

    # 2. Average Messages Per Day
    avg_messages_per_day = df.groupby('day')['message'].count().mean()

    # 3. Average Messages Per Week
    avg_messages_per_week = df.groupby('week')['message'].count().mean()

    # 4. Average Messages Per HOur
    avg_messages_per_hour = df.groupby('hour')['message'].count().mean()
    
    return format_number_short(round(avg_messages_per_month, 2)), format_number_short(round(avg_messages_per_day, 2)), format_number_short(round(avg_messages_per_week, 2)), format_number_short(round(avg_messages_per_hour, 2))