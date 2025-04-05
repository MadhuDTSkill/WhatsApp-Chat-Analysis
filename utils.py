import pandas as pd
from urlextract import URLExtract

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
