import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

# Load datasets
day_df = pd.read_csv('day.csv')
hour_df = pd.read_csv('hour.csv')

# Convert the date columns to datetime format
day_df['dteday'] = pd.to_datetime(day_df['dteday'])
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

# Filter data using date input from the user
min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

with st.sidebar:
    #st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Date range filter
    start_date, end_date = st.date_input(
        'Rentang Waktu', min_value=min_date.to_pydatetime().date(),
        max_value=max_date.to_pydatetime().date(), value=[min_date.to_pydatetime().date(), max_date.to_pydatetime().date()]
    )

    # Weather filter
    weather_filter = st.multiselect('Filter by Weather Situation', options=['Clear', 'Misty', 'Light Rain', 'Heavy Rain'])

    # Season filter
    season_filter = st.multiselect('Filter by Season', options=['Spring', 'Summer', 'Fall', 'Winter'])

# Convert start_date and end_date to pandas datetime for comparison
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter the data based on the date range selected
filtered_day_df = day_df[(day_df['dteday'] >= start_date) & (day_df['dteday'] <= end_date)]
filtered_hour_df = hour_df[(hour_df['dteday'] >= start_date) & (hour_df['dteday'] <= end_date)]

# Additional filters (weather and season)
if weather_filter:
    weather_map = {'Clear': 1, 'Misty': 2, 'Light Rain': 3, 'Heavy Rain': 4}
    filtered_hour_df = filtered_hour_df[filtered_hour_df['weathersit'].isin([weather_map[w] for w in weather_filter])]

if season_filter:
    season_map = {'Spring': 1, 'Summer': 2, 'Fall': 3, 'Winter': 4}
    filtered_day_df = filtered_day_df[filtered_day_df['season'].isin([season_map[s] for s in season_filter])]

# Metrics Calculation
total_rides = filtered_day_df['cnt'].sum()
avg_daily_rides = filtered_day_df['cnt'].mean()
total_registered = filtered_day_df['registered'].sum()
total_casual = filtered_day_df['casual'].sum()

# Display main metrics with dynamic subtitle
st.header('Bike Sharing Dashboard :bike:')
st.subheader(f'Summary Metrics')

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Rides", total_rides)
col2.metric("Avg Daily Rides", round(avg_daily_rides, 2))
col3.metric("Total Registered", total_registered)
col4.metric("Total Casual", total_casual)

# Plot Daily Rides over time
st.subheader('Daily Rides Over Time')

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(filtered_day_df['dteday'], filtered_day_df['cnt'], marker='o', color='#90CAF9')
ax.set_title('Daily Rides Over Time', fontsize=20)
ax.set_xlabel('Date', fontsize=15)
ax.set_ylabel('Number of Rides', fontsize=15)

st.pyplot(fig)

# Analyze weather impact
st.subheader('Weather Impact on Bike Usage')

if weather_filter:
    weather_labels = ['Clear', 'Misty', 'Light Rain', 'Heavy Rain']
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='weathersit', y='cnt', data=filtered_hour_df, ax=ax, ci=None, palette='viridis')
    ax.set_title('Rides by Weather Situation', fontsize=20)
    ax.set_xlabel('Weather Situation', fontsize=15)
    ax.set_xticklabels(weather_labels)
    ax.set_ylabel('Number of Rides', fontsize=15)
    st.pyplot(fig)
else:
    st.write("No weather filter selected.")

# Hourly analysis (heatmap)
st.subheader('Hourly Bike Usage')

weekday_labels = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
hourly_data = filtered_hour_df.groupby(['hr', 'weekday'])['cnt'].mean().unstack()
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(hourly_data, cmap='Blues', ax=ax)
ax.set_title('Average Hourly Usage by Weekday', fontsize=20)
ax.set_xlabel('Weekday', fontsize=15)
ax.set_xticklabels(weekday_labels)
ax.set_ylabel('Hour of Day', fontsize=15)

st.pyplot(fig)

# Impact of season on Bike Rentals
st.subheader('Impact of Season on Rentals')

season_labels = ['Spring', 'Summer', 'Fall', 'Winter']
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x='season', y='cnt', data=filtered_day_df, ax=ax, ci=None, palette='coolwarm')
ax.set_title('Rides by Season', fontsize=20)
ax.set_xlabel('Season', fontsize=15)
ax.set_xticklabels(season_labels)
ax.set_ylabel('Number of Rides', fontsize=15)

st.pyplot(fig)

# Additional insights or key takeaways
st.subheader("Key Takeaways")
if total_rides > 10000:
    st.write("Bike sharing usage is high in the selected period. Consider deploying more bikes during peak hours.")
else:
    st.write("Bike sharing usage is moderate. Keep monitoring trends to optimize operations.")

# Menambahkan analisis dan insight yang lebih mendalam
st.subheader("Analisis dan Insight")

# Analisis Tren Jumlah Perjalanan dari Waktu ke Waktu
st.write("### Analisis Tren Penggunaan Sepeda")
if total_rides > avg_daily_rides * len(filtered_day_df):
    st.write(f"Dalam periode yang dipilih ({start_date.date()} - {end_date.date()}), total penggunaan sepeda lebih tinggi dari perkiraan rata-rata harian.")
else:
    st.write(f"Dalam periode yang dipilih ({start_date.date()} - {end_date.date()}), total penggunaan sepeda lebih rendah dari rata-rata harian.")

# Analisis Dampak Cuaca pada Penggunaan Sepeda
st.write("### Analisis Dampak Cuaca")
if weather_filter:
    for weather in weather_filter:
        st.write(f"Kondisi cuaca {weather} cenderung mempengaruhi penggunaan sepeda dengan rata-rata {filtered_hour_df[filtered_hour_df['weathersit'] == weather_map[weather]]['cnt'].mean():.2f} perjalanan per jam.")
else:
    st.write("Tidak ada filter cuaca yang dipilih. Anda bisa memilih cuaca pada sidebar untuk melihat dampaknya pada penggunaan sepeda.")

# Analisis Penggunaan per Jam
st.write("### Analisis Pola Penggunaan per Jam")
peak_hours = hourly_data.idxmax(axis=0)
peak_usage = hourly_data.max().mean()
st.write(f"Penggunaan sepeda tertinggi rata-rata terjadi pada pukul {peak_hours.mode()[0]} dengan rata-rata {peak_usage:.2f} perjalanan per jam.")

# Analisis Variasi Musiman
st.write("### Analisis Penggunaan Berdasarkan Musim")
if season_filter:
    for season in season_filter:
        avg_rides_season = filtered_day_df[filtered_day_df['season'] == season_map[season]]['cnt'].mean()
        st.write(f"Selama musim {season}, rata-rata penggunaan sepeda adalah {avg_rides_season:.2f} perjalanan per hari.")
else:
    st.write("Tidak ada filter musim yang dipilih. Anda bisa memilih musim pada sidebar untuk melihat pengaruhnya terhadap penggunaan sepeda.")

# Perbandingan Pengguna Terdaftar vs Pengguna Kasual
st.write("### Perbandingan Pengguna Terdaftar dan Kasual")
if total_registered > total_casual:
    st.write(f"Pengguna terdaftar jauh lebih banyak ({total_registered} perjalanan) dibandingkan pengguna kasual ({total_casual} perjalanan). Ini menunjukkan ketergantungan lebih tinggi pada langganan sepeda.")
else:
    st.write(f"Pengguna kasual ({total_casual} perjalanan) lebih banyak dibandingkan pengguna terdaftar ({total_registered} perjalanan). Ini mungkin mengindikasikan banyaknya wisatawan atau pengguna non-rutin.")


st.caption('Copyright © 2024')
