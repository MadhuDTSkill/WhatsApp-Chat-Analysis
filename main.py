import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import preprocessing as pre
import utils


st.set_page_config(page_title="WhatsApp Data Analysis", layout="wide")
st.title("WhatsApp Data Analysis App")


st.sidebar.title("Upload WhatsApp Chat Data")
uploaded_file = st.sidebar.file_uploader("Upload a file", type=["txt"])

if uploaded_file is not None:
    st.write("File name:", uploaded_file.name)

    binary_file = uploaded_file.getvalue()
    data = binary_file.decode("utf-8")
    with st.spinner("Processing data..."):
        df = pre.preprocess_data(data)
    
    user_list = sorted(df['user'].unique().tolist())
    user_list.insert(0, "All")
    selected_user = st.sidebar.selectbox("Choose the User", options= user_list, key="user_select")

    if selected_user:
        with st.spinner("Analyzing data..."):
            (
                total_messages, total_words, total_media_messages, total_links,
                total_characters, average_words, longest_message_length, shortest_message_length,
                most_active_day, active_days, longest_streak, max_gap
            ) = utils.stats(df, selected_user)

            st.markdown("## 🔢 Chat Summary Statistics")

            # Basic Message Stats
            st.markdown("### ✉️ Message Overview")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Messages", total_messages)
            col2.metric("Total Words", total_words)
            col3.metric("Media Shared", total_media_messages)
            col4.metric("Links Shared", total_links)

            st.markdown("---")

            # Message Details
            st.markdown("### 📏 Message Details")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Characters", total_characters)
            col2.metric("Avg. Words per Msg", f"{average_words}")
            col3.metric("Longest Msg Length", longest_message_length)
            col4.metric("Shortest Msg Length", shortest_message_length)

            st.markdown("---")

            # Activity Details
            st.markdown("### 📅 Activity Insights")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Most Active Day", most_active_day)
            col2.metric("Active Days", active_days)
            col3.metric("Longest Streak", f"{longest_streak} days")
            col4.metric("Longest Inactive Gap", f"{max_gap} days")

                