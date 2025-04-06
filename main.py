import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
import preprocessing as pre
import utils

sns.set_style("whitegrid")
plt.rcParams.update({'font.family': 'sans-serif'})
plt.style.use('dark_background')

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
        with st.spinner("Analyzing Stats..."):
            (
                total_messages, total_words, total_media_messages, total_links,
                total_characters, average_words, longest_message_length, shortest_message_length,
                most_active_day, active_days, longest_streak, max_gap
            ) = utils.stats(df, selected_user)

            st.markdown("### 🔢 Chat Summary Statistics")

            # Basic Message Stats
            st.markdown("#### ✉️ Message Overview")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Messages", total_messages)
            col2.metric("Total Words", total_words)
            col3.metric("Media Shared", total_media_messages)
            col4.metric("Links Shared", total_links)

            st.markdown("---")

            # Message Details
            st.markdown("#### 📏 Message Details")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Characters", total_characters)
            col2.metric("Avg. Words per Msg", f"{average_words}")
            col3.metric("Longest Msg Length", longest_message_length)
            col4.metric("Shortest Msg Length", shortest_message_length)

            st.markdown("---")

            # Activity Details
            st.markdown("#### 📅 Activity Insights")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Most Active Day", most_active_day)
            col2.metric("Active Days", active_days)
            col3.metric("Longest Streak", f"{longest_streak} days")
            col4.metric("Longest Inactive Gap", f"{max_gap} days")
            
            st.markdown("---")
            
            ################################################################################
            ############################### Line Chart For Messages History#################
            ################################################################################
        with st.spinner("Calculating Avarages..."):
            st.markdown("### 📊 Avarages")
            month, day, week, hour = utils.get_averages(df, selected_user)
            
            col1, col2 = st.columns(2)

            col1.markdown("##### Average Messages per Month")
            with col1:
                st.markdown(f"#### **{month}**")

            col2.markdown("##### Average Messages per Day")
            with col2:
                st.markdown(f"#### **{day}**")

            col1, col2 = st.columns(2)
            
            st.markdown('---')

            col1.markdown("##### Average Messages per Week")
            with col1:
                st.markdown(f"#### **{week}**")
                
            col2.markdown("##### Average Messages per Hour")
            with col2:
                st.markdown(f"#### **{hour}**") 

            ################################################################################
            ############################### Line Chart For Messages History#################
            ################################################################################
            
        with st.spinner("Loading Line Chart For Messages History..."):
            
            line_chart_data = utils.get_line_chat_of_message_history(df, selected_user)        
            st.markdown("### 📈 Message History - Growth")
            st.markdown("This line chart shows the number of messages sent over time.")
            st.line_chart(data = line_chart_data, x='date', y = 'count', use_container_width=True, x_label="Date", y_label="Number of Messages")   
            
                
            
            ################################################################################
            ############################### Most Busy Users ################################
            ################################################################################

        with st.spinner("Finding Most Busy Users..."):
                    
            busy_user_df = utils.most_busy_user(df, selected_user)
            colors = sns.color_palette("coolwarm", len(busy_user_df[:10]))
            
            fig, ax = plt.subplots()
            
            users = list(reversed(busy_user_df['user'][:10]))
            counts = list(reversed(busy_user_df['count'][:10]))
            
            bars = ax.barh(users, counts, color=colors)
            
            for bar in bars:
                width = bar.get_width()
                ax.text(width + 1, bar.get_y() + bar.get_height() / 2, f'{width}', va='center', fontsize=10, color='black')

            ax.set_xlabel("Number of Messages", fontsize=12, labelpad=10)
            ax.set_ylabel("Users", fontsize=12, labelpad=10)
            ax.set_title("Most Active Users", fontsize=14, weight='bold', color='#fff')

            sns.despine(left=False, bottom=False)

            ax.set_xlim([0, max(counts) + max(counts) * 0.2])

            plt.tight_layout()
            
            col1, col2 = st.columns(2)
            col1.markdown("### 🧑‍💻 Most Busy User")            
            with col1:
                st.pyplot(fig)
                
            with col2:
                col2.markdown("### 📈 User Message Count")
                st.dataframe(busy_user_df, use_container_width=True)
                
                
            st.markdown("---")
            
            ################################################################################
            ############################### Wordcloud ######################################
            ################################################################################
        with st.spinner("Creating Wordcloud..."):

            st.markdown("### 🗣️ Wordcloud")
            st.markdown("This wordcloud shows the most frequently used words in the chat. The larger the word, the more frequently it appears.")
            
            wordcloud = utils.create_wordcloud(df, selected_user)
            
            fig, ax = plt.subplots()
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            plt.tight_layout()
            st.pyplot(fig)
            
            
            ################################################################################
            ############################### Most Busy Month & Day ######################################
            ################################################################################
        with st.spinner("Finding Most Busy Month & Day..."):

            st.markdown("### 📅 Most Busy Month & Day")
            st.markdown("This shows the months & day with the most messages sent.")

            busy_month_df = utils.most_busy_month(df, selected_user)

            # Layout for chart and user table
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 👥 Top Most Active Months")
                st.bar_chart(busy_month_df[:10], x='busy_month', y='message', use_container_width=True, x_label="Month", y_label="Number of Messages")
                
            
            busy_day_df = utils.most_busy_day(df, selected_user)
            
            with col2:
                st.markdown("### 👥 Most Active Days")
                st.bar_chart(busy_day_df[:10], x='day_name', y='count', use_container_width=True, x_label="Day", y_label="Number of Messages")
                
                
            ################################################################################
            ############################### Most Busy Week & Hour ################################
            ################################################################################
        with st.spinner("Finding Most Busy Week & Hour..."):
                
                st.markdown("### ⏰ Most Busy Week & Hour")
                st.markdown("This shows the Weeks & hours with the most messages sent.")
    
                busy_week_df = utils.most_busy_week(df, selected_user)
                
                # Prepare plot
                fig, ax = plt.subplots(figsize=(10, 5))
                colors = sns.color_palette("Spectral", len(busy_week_df))
    
                busy_weeks = list(reversed(busy_week_df['week']))
                message_counts = list(reversed(busy_week_df['count']))
    
                bars = ax.bar(busy_weeks, message_counts, color=colors)
    
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2, height + 2, f'{height}', 
                            ha='center', va='bottom', fontsize=10)
    
                ax.set_xlabel("Week", fontsize=12, labelpad=10)
                ax.set_ylabel("Number of Messages", fontsize=12, labelpad=10)
                ax.set_title("🕒 Messages per Week", fontsize=14, weight='bold', color='#fff')
    
                sns.despine()
                plt.xticks(rotation=45)
                plt.tight_layout()
    
                # Layout for chart and user table
                col1, col2 = st.columns(2)
    
                with col1:
                    st.markdown("### Top Weeks")
                    st.pyplot(fig)
                
                
                busy_hour_df = utils.most_busy_hour(df, selected_user)
                
                # Prepare plot
                fig, ax = plt.subplots(figsize=(10, 5))
                colors = sns.color_palette("Spectral", len(busy_hour_df))
                
                busy_hours = list(reversed(busy_hour_df['busy_hour']))
                message_counts = list(reversed(busy_hour_df['message']))
                
                bars = ax.bar(busy_hours, message_counts, color=colors)
                
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2, height + 2, f'{height}', 
                            ha='center', va='bottom', fontsize=10)
                    
                ax.set_xlabel("Hour", fontsize=12, labelpad=10)
                ax.set_ylabel("Number of Messages", fontsize=12, labelpad=10)
                
                ax.set_title("🕒 Messages per Hour", fontsize=14, weight='bold', color='#fff')
                
                sns.despine()
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                with col2:
                    st.markdown("### Top Hours")
                    st.pyplot(fig)
                    
        st.markdown("---")
                    
            ################################################################################
            ############################### User Activity ################################
            ################################################################################
        with st.spinner("Finding User Activity..."):
                
            heatmap_data = utils.heatmap_activity(df, selected_user)
            
            st.markdown("### 📊 User Activity Heatmap")
            st.markdown("This heatmap shows the activity of the user over the hours.")
            
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.heatmap(
                heatmap_data, 
                linewidths=0.5, 
                linecolor='gray',
                annot=True,          
                fmt='.0f',           
                annot_kws={"size": 8}, 
                ax=ax
            )
            ax.set_xlabel("Hour", fontsize=10)
            ax.set_ylabel("Day", fontsize=10)
            ax.set_title("User Activity Heatmap", fontsize=14, weight='bold', color='#fff')
            
            ax.set_xticks([i + 0.5 for i in range(len(heatmap_data.columns))])  
            ax.set_xticklabels([column[1] for column in heatmap_data.columns], rotation=0, fontsize=9)

            ax.set_yticks([i + 0.5 for i in range(len(heatmap_data.index))])    
            ax.set_yticklabels([index[:3] for index in heatmap_data.index], rotation=0, fontsize=9)
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            st.pyplot(fig)
            
        st.markdown("---")
                    
                