import pandas as pd
import json
import streamlit as st
import plotly.express as px


#################
##  FUNCTIONS  ##
#################

#function to convert to numerical hours
def convert_ms_to_hrs_num(ms):
    minutes = ms // 60000
    hours = round((minutes / 60), 2)
    return hours

#function to convert to numerical minutes
def convert_ms_to_min_num(ms):
    minutes = ms // 60000
    return minutes

#function to convert ms to a string with hours (optional), minutes, and seconds
def convert_ms_to_hr_min_sec(ms):
    hours = 0
    seconds = ms // 1000
    minutes = seconds // 60
    if minutes > 59:
        hours = minutes // 60
        minutes = minutes % 60
    seconds = seconds % 60
    if hours != 0:
        return f"{hours}h {minutes}m {seconds}s"
    else:
        return f"{minutes}m {seconds}s"

#function to convert ms to a string with minutes and seconds
def convert_ms_to_min_sec(ms):
    seconds = ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}m {seconds}s"

#function to convert ms to minutes
def convert_ms_to_min(ms):
    minutes = ms // 60000
    return minutes



####################################
## INITIAL DATA IMPORT & CLEANING ##
####################################

#import streaming history from 9/23 to 9/24
df = pd.read_json('StreamingHistory_music_0.json')

#print column names
# print(df.columns.values)

#convert endTime to datetime
df['endTime'] = pd.to_datetime(df['endTime'])

#create column month_year as a month period
df['month_year'] = df['endTime'].dt.to_period('M').astype(str)

#create column date as a day period
df['date'] = pd.to_datetime(df['endTime']).dt.date

#remove the one song from March 2023 and the 3 Hour White Noise track
df_filtered = df[~((df['month_year'].astype(str) == '2023-03') | (df['trackName'] == 'White Noise 3 Hour Long'))]



#########################
## TOP SONGS PER MONTH ##
#########################

#sum each month's tracks' listening times together
monthly_songs = df_filtered.groupby(['month_year', 'artistName', 'trackName'], as_index=False)['msPlayed'].sum()

#create a df of top songs per month based on listening time
top_songs_per_month = monthly_songs.sort_values(['month_year', 'msPlayed'], ascending=[True, False]).groupby('month_year').head(1)

#making listening time easier to understand by grouping into minutes, seconds
top_songs_per_month['listening_time'] = top_songs_per_month['msPlayed'].apply(convert_ms_to_min_sec)

#adding minutes listened to for better visability
top_songs_per_month['mins'] = top_songs_per_month['msPlayed'].apply(convert_ms_to_min_num)

# Add a short track name column for long names
top_songs_per_month['trackName_short'] = top_songs_per_month['trackName'].apply(lambda x: x if len(x) <= 30 else x[:27] + '...')


#printing top songs per month results
# print(f"\nTOP SONGS PER MONTH\n{top_songs_per_month}\n")

# Bar chart for top songs per month
fig_top_songs_month = px.bar(top_songs_per_month,
                       x='month_year',
                       y='mins',
                       color='trackName_short',
                       labels={'mins': 'Total Listening Time (minutes)', 'month_year': 'Month', 'trackName_short': 'Track'},
                       text='listening_time',
                       hover_data={'trackName': True, 'trackName_short': False}
                       )

fig_top_songs_month.update_layout(legend_title_text='Top Songs', showlegend=True)



###########################
## TOP ARTISTS PER MONTH ##
###########################

#sum each month's artist listening times together
monthly_artists = df_filtered.groupby(['month_year', 'artistName'], as_index=False)['msPlayed'].sum()

#create a df of top artists per month based on listening time
top_artists_per_month = monthly_artists.sort_values(['month_year', 'msPlayed'], ascending=[True, False]).groupby('month_year').head(1)

#making listening time easier to understand by grouping into minutes, seconds
top_artists_per_month['listening_time'] = top_artists_per_month['msPlayed'].apply(convert_ms_to_hr_min_sec)

#adding minutes listened to for better visability
top_artists_per_month['mins'] = top_artists_per_month['msPlayed'].apply(convert_ms_to_min_num)

# print(f"TOP ARTISTS PER MONTH\n{top_artists_per_month}\n")

# Bar chart for top artists per month
fig_top_artists_month = px.bar(top_artists_per_month,
                          x='month_year',
                          y='mins',
                          color='artistName',
                          labels={'mins': 'Total Listening Time (minutes)', 'month_year': 'Month'},
                          text='listening_time')


##!!
############################
## TOP SONGS IN PAST YEAR ##
############################

#sum the year's tracks' listening times together
yearly_songs = df_filtered.groupby(['artistName', 'trackName'], as_index=False)['msPlayed'].sum()

#create a df of top songs per month based on listening time
top_songs = yearly_songs.sort_values(['msPlayed'], ascending=[False]).head(15)

#making listening time easier to understand by grouping into minutes, seconds
top_songs['listening_time'] = top_songs['msPlayed'].apply(convert_ms_to_hr_min_sec)

#adding minutes listened to for better visability
top_songs['hrs'] = top_songs['msPlayed'].apply(convert_ms_to_hrs_num)

#printing top songs per month results
# print(f"TOP SONGS IN PAST YEAR\n{top_songs}\n")

# Create a horizontal bar chart for top artists in the past year
fig_top_songs = px.bar(
    top_songs,
    x='hrs',
    y='trackName',
    orientation='h',
    labels={'hrs': 'Total Listening Time (hrs)', 'artistName': 'Artist'},
    text='listening_time'
)

# Customize the layout and appearance
fig_top_songs.update_traces(
    textposition='inside',
    insidetextanchor='start',
    textfont=dict(color='white')
)

# Sort bars by listening time and adjust layout
fig_top_songs.update_layout(
    yaxis={'categoryorder': 'total ascending'},
    xaxis_title='Listening Time (hours)',
    yaxis_title='',
    margin=dict(l=0, r=0, t=40, b=40),
    height = 600
)


##!!
##############################
## TOP ARTISTS IN PAST YEAR ##
##############################

#sum artist listening times together
yearly_artists = df_filtered.groupby(['artistName'], as_index=False)['msPlayed'].sum()

#create a df of top artists per month based on listening time
top_artists = yearly_artists.sort_values(['msPlayed'], ascending=[False]).head(15)

#making listening time easier to understand by grouping into minutes, seconds
top_artists['listening_time'] = top_artists['msPlayed'].apply(convert_ms_to_hr_min_sec)

#adding minutes listened to for better visability
top_artists['hrs'] = top_artists['msPlayed'].apply(convert_ms_to_hrs_num)

# print(f"TOP ARTISTS IN PAST YEAR\n{top_artists}\n")

# Create a horizontal bar chart for top artists in the past year
fig_top_artists = px.bar(
    top_artists,
    x='hrs',
    y='artistName',
    orientation='h',
    labels={'hrs': 'Total Listening Time (hrs)', 'artistName': 'Artist'},
    text='listening_time'
)

# Customize the layout and appearance
fig_top_artists.update_traces(
    textposition='inside',
    insidetextanchor='start',
    textfont=dict(color='white')
)

# Sort bars by listening time and adjust layout
fig_top_artists.update_layout(
    yaxis={'categoryorder': 'total ascending'},
    xaxis_title='Listening Time (hours)',
    yaxis_title='',
    margin=dict(l=0, r=0, t=40, b=40),
    height = 600
)





############################
## MONTHLY LISTENING TIME ##
############################

#sum each month's listening times together
monthly_listening = df_filtered.groupby(['month_year'], as_index=False)['msPlayed'].sum()

#sort the values by month
monthly_listening = monthly_listening.sort_values(['month_year'], ascending=[True])

#making listening time easier to understand by grouping into minutes, seconds
monthly_listening['listening_time'] = monthly_listening['msPlayed'].apply(convert_ms_to_hr_min_sec)

#adding minutes listened to for better visability
monthly_listening['hrs'] = monthly_listening['msPlayed'].apply(convert_ms_to_hrs_num)

# print(f"MONTHLY LISTENING TIME\n{monthly_listening}\n")

# Line chart for monthly listening time
fig_monthly_listening = px.line(monthly_listening,
                                 x='month_year',
                                 y='hrs',
                                 labels={'hrs': 'Total Listening Time (hours)', 'month_year': 'Month'},
                                 markers=True)

# Update layout to set the y-axis range starting at 0
fig_monthly_listening.update_layout(
    yaxis=dict(range=[0, monthly_listening['hrs'].max() * 1.1])  # Setting the minimum value to 0 and max slightly above the max value
)



############################
## WEEKLY LISTENING TIME ##
############################

# Group by week and sum listening times
weekly_listening = df_filtered.groupby(pd.Grouper(key='endTime', freq='W')).agg({'msPlayed': 'sum'}).reset_index()

# Convert the week to a more readable format (start date of the week)
weekly_listening['week_start'] = weekly_listening['endTime'].dt.to_period('W').astype(str)
weekly_listening['week_start'] = weekly_listening['week_start'].str.split('/').str[0]

# Calculate total listening time in hours
weekly_listening['hrs'] = weekly_listening['msPlayed'].apply(convert_ms_to_hrs_num)

# Print the weekly listening time DataFrame for debugging
# print(f"WEEKLY LISTENING TIME\n{weekly_listening}\n")

# Create a line chart for weekly listening time
fig_weekly_listening = px.line(
    weekly_listening,
    x='week_start',
    y='hrs',
    labels={'hrs': 'Total Listening Time (hours)', 'week_start': 'Week Starting'},
    markers=True
)

# Update layout to set the y-axis range starting at 0
fig_weekly_listening.update_layout(
    yaxis=dict(range=[0, weekly_listening['hrs'].max() * 1.1]),  # Setting the minimum value to 0 and max slightly above the max value
)



##########################
## DAILY LISTENING TIME ##
##########################

#sum each day's listening times together
daily_listening = df_filtered.groupby(['date'], as_index=False)['msPlayed'].sum()
daily_listening['date'] = pd.to_datetime(daily_listening['date'])

### making sure that every day is accounted for (even when I didn't listen to music)
#creating a date range and assigning it to a df
date_range = pd.date_range(start='2023-09-14', end='2024-09-13', freq='D')
complete_dates = pd.DataFrame({'date': date_range})

#merge the df's
daily_listening = pd.merge(complete_dates, daily_listening, on='date', how='left')

#fill null values with 0's
daily_listening['msPlayed'] = daily_listening['msPlayed'].fillna(0)

#sort the values by day
daily_listening = daily_listening.sort_values(['date'], ascending=[True])

#making listening time easier to understand by reformatting
daily_listening['msPlayed'] = daily_listening['msPlayed'].astype(int)
daily_listening['listening_time'] = daily_listening['msPlayed'].apply(convert_ms_to_hr_min_sec)

#adding minutes listened to for better visability
daily_listening['mins'] = daily_listening['msPlayed'].apply(convert_ms_to_min_num)

# print(f"DAILY LISTENING TIME\n{daily_listening}\n")

# Bar chart for daily listening time
fig_daily_listening = px.bar(daily_listening,
                              x='date',
                              y='mins',
                              labels={'mins': 'Total Listening Time (minutes)', 'date': 'Date'},
                              text='listening_time')


#####################
## Streamlit Stuff ##
#####################

import streamlit as st

st.set_page_config(layout="wide")

# Set up the Streamlit app
st.title('Spotify Dashboard')

col1, col2 = st.columns(2)

# Display the top artists chart in the first column
with col1:
    st.subheader('Top Artists Sept 2023 - Sept 2024')
    st.plotly_chart(fig_top_artists, use_container_width=True)

# Display the top songs chart in the second column
with col2:
    st.subheader('Top Songs Sept 2023 - Sept 2024')
    st.plotly_chart(fig_top_songs, use_container_width=True)

col3, col4 = st.columns(2)

# Top Songs Per Month
with col3:
    st.subheader('Top Songs Per Month')
    st.plotly_chart(fig_top_songs_month, use_container_width=True)

# Top Artists Per Month
with col4:
    st.subheader('Top Artists Per Month')
    st.plotly_chart(fig_top_artists_month, use_container_width=True)

# Monthly Listening Time
st.subheader('Monthly Listening Time')
st.plotly_chart(fig_monthly_listening)

# Weekly Listening Time
st.subheader('Weekly Listening Time')
st.plotly_chart(fig_weekly_listening)

# Daily Listening Time
st.subheader('Daily Listening Time')
st.plotly_chart(fig_daily_listening)
