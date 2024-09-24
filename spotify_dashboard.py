import pandas as pd
import json
import streamlit as st
import plotly.express as px


#################
##  FUNCTIONS  ##
#################

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

#printing top songs per month results
# print(f"\nTOP SONGS PER MONTH\n{top_songs_per_month}\n")

# Bar chart for top songs per month
fig_top_songs = px.bar(top_songs_per_month,
                       x='month_year',
                       y='msPlayed',
                       color='trackName',
                       title='Top Songs Per Month',
                       labels={'msPlayed': 'Total Listening Time (ms)', 'month_year': 'Month'},
                       text='listening_time')



###########################
## TOP ARTISTS PER MONTH ##
###########################

#sum each month's artist listening times together
monthly_artists = df_filtered.groupby(['month_year', 'artistName'], as_index=False)['msPlayed'].sum()

#create a df of top artists per month based on listening time
top_artists_per_month = monthly_artists.sort_values(['month_year', 'msPlayed'], ascending=[True, False]).groupby('month_year').head(1)

#making listening time easier to understand by grouping into minutes, seconds
top_artists_per_month['listening_time'] = top_artists_per_month['msPlayed'].apply(convert_ms_to_hr_min_sec)

# print(f"TOP ARTISTS PER MONTH\n{top_artists_per_month}\n")

# Bar chart for top artists per month
fig_top_artists = px.bar(top_artists_per_month,
                          x='month_year',
                          y='msPlayed',
                          color='artistName',
                          title='Top Artists Per Month',
                          labels={'msPlayed': 'Total Listening Time (ms)', 'month_year': 'Month'},
                          text='listening_time')



############################
## TOP SONGS IN PAST YEAR ##
############################

#sum the year's tracks' listening times together
yearly_songs = df_filtered.groupby(['artistName', 'trackName'], as_index=False)['msPlayed'].sum()

#create a df of top songs per month based on listening time
top_songs = yearly_songs.sort_values(['msPlayed'], ascending=[False]).head(25)

#making listening time easier to understand by grouping into minutes, seconds
top_songs['listening_time'] = top_songs['msPlayed'].apply(convert_ms_to_hr_min_sec)

#printing top songs per month results
# print(f"TOP SONGS IN PAST YEAR\n{top_songs}\n")




##############################
## TOP ARTISTS IN PAST YEAR ##
##############################

#sum artist listening times together
yearly_artists = df_filtered.groupby(['artistName'], as_index=False)['msPlayed'].sum()

#create a df of top artists per month based on listening time
top_artists = yearly_artists.sort_values(['msPlayed'], ascending=[False]).head(25)

#making listening time easier to understand by grouping into minutes, seconds
top_artists['listening_time'] = top_artists['msPlayed'].apply(convert_ms_to_hr_min_sec)

# print(f"TOP ARTISTS IN PAST YEAR\n{top_artists}\n")



############################
## MONTHLY LISTENING TIME ##
############################

#sum each month's listening times together
monthly_listening = df_filtered.groupby(['month_year'], as_index=False)['msPlayed'].sum()

#sort the values by month
monthly_listening = monthly_listening.sort_values(['month_year'], ascending=[True])

#making listening time easier to understand by grouping into minutes, seconds
monthly_listening['listening_time'] = monthly_listening['msPlayed'].apply(convert_ms_to_hr_min_sec)

# print(f"MONTHLY LISTENING TIME\n{monthly_listening}\n")

# Line chart for monthly listening time
fig_monthly_listening = px.line(monthly_listening,
                                 x='month_year',
                                 y='msPlayed',
                                 title='Monthly Listening Time',
                                 labels={'msPlayed': 'Total Listening Time (ms)', 'month_year': 'Month'},
                                 markers=True)



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

# print(f"DAILY LISTENING TIME\n{daily_listening}\n")

# Bar chart for daily listening time
fig_daily_listening = px.bar(daily_listening,
                              x='date',
                              y='msPlayed',
                              title='Daily Listening Time',
                              labels={'msPlayed': 'Total Listening Time (ms)', 'date': 'Date'},
                              text='listening_time')


#####################
## Streamlit Stuff ##
#####################

import streamlit as st

# Set up the Streamlit app
st.title('Spotify Dashboard')

# Top Songs Per Month
st.subheader('Top Songs Per Month')
st.plotly_chart(fig_top_songs)

# Top Artists Per Month
st.subheader('Top Artists Per Month')
st.plotly_chart(fig_top_artists)

# Monthly Listening Time
st.subheader('Monthly Listening Time')
st.plotly_chart(fig_monthly_listening)

# Daily Listening Time
st.subheader('Daily Listening Time')
st.plotly_chart(fig_daily_listening)
