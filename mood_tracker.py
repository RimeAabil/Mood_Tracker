import streamlit as st
import pandas as pd
from textblob import TextBlob
import datetime
import calendar
import plotly.express as px

# Set up the app title with custom styling
st.markdown(
    """
    <style>
    .title {
        font-size: 40px;
        font-weight: bold;
        color: #4A90E2;
        text-align: center;
        margin-bottom: 30px;
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    .stButton button {
        background-color: #4A90E2;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .stButton button:hover {
        background-color: #357ABD;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="title">Mood Tracker & Sentiment Analysis</div>', unsafe_allow_html=True)

# Initialize session state to store mood logs
if 'mood_logs' not in st.session_state:
    st.session_state.mood_logs = pd.DataFrame(columns=["Date", "Mood", "Thoughts", "Sentiment"])

# Function to analyze sentiment using TextBlob
def analyze_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity  # Returns a polarity score between -1 (negative) and 1 (positive)

# Map moods to numerical values for plotting
mood_mapping = {
    "😊 Happy": 3,
    "🤩 Excited": 2,
    "😐 Neutral": 1,
    "😢 Sad": -1,
    "😡 Angry": -2,
    "😨 Anxious": -3
}

# Sidebar for user input
with st.sidebar:
    st.header("Log Your Mood")
    date = st.date_input("Date", datetime.date.today())
    mood = st.selectbox("Mood", ["😊 Happy", "😐 Neutral", "😢 Sad", "😡 Angry", "😨 Anxious", "🤩 Excited"])
    thoughts = st.text_area("Jot down your thoughts")
    submit = st.button("Log Mood")

# Log mood and thoughts
if submit:
    sentiment = analyze_sentiment(thoughts)
    new_entry = pd.DataFrame({
        "Date": [datetime.datetime.combine(date, datetime.datetime.min.time())],  # Convert date to datetime
        "Mood": [mood],
        "Thoughts": [thoughts],
        "Sentiment": [sentiment]
    })
    st.session_state.mood_logs = pd.concat([st.session_state.mood_logs, new_entry], ignore_index=True)
    st.success("Mood logged successfully!")

# Display mood logs with enhanced styling
st.header("Your Mood Logs")
if not st.session_state.mood_logs.empty:
    # Convert Date column to string for display
    display_logs = st.session_state.mood_logs.copy()
    display_logs["Date"] = display_logs["Date"].dt.strftime("%Y-%m-%d")  # Format as string
    st.dataframe(display_logs.style.applymap(lambda x: 'background-color: #e6f3ff' if x == "😊 Happy" else ''))
else:
    st.write("No mood logs available yet.")

# Mood Calendar with enhanced styling
st.header("Mood Calendar")
st.write("Visualize your mood over time.")

# Create a calendar view with enhanced styling
def create_mood_calendar(year, month, mood_logs):
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    st.subheader(f"{month_name} {year}")
    
    # Create a grid for the calendar
    cols = st.columns(7)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i, day in enumerate(days):
        cols[i].markdown(f"**{day}**", unsafe_allow_html=True)
    
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("")
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                mood_entry = mood_logs[mood_logs["Date"].dt.strftime("%Y-%m-%d") == date_str]
                if not mood_entry.empty:
                    mood = mood_entry.iloc[0]["Mood"]
                    sentiment = mood_entry.iloc[0]["Sentiment"]
                    # Color code based on sentiment
                    if sentiment > 0.2:
                        cols[i].success(f"{day}\n{mood}")
                    elif sentiment < -0.2:
                        cols[i].error(f"{day}\n{mood}")
                    else:
                        cols[i].warning(f"{day}\n{mood}")
                else:
                    cols[i].write(day)

# Get current year and month
current_date = datetime.date.today()
current_year = current_date.year
current_month = current_date.month

# Display the calendar
create_mood_calendar(current_year, current_month, st.session_state.mood_logs)

# Sentiment Analysis Summary with enhanced styling
st.header("Sentiment Analysis Summary")
if not st.session_state.mood_logs.empty:
    avg_sentiment = st.session_state.mood_logs["Sentiment"].mean()
    st.write(f"Average Sentiment Score: {avg_sentiment:.2f}")
    if avg_sentiment > 0.2:
        st.success("Overall, your mood has been positive! 😊")
    elif avg_sentiment < -0.2:
        st.error("Overall, your mood has been negative. 😢")
    else:
        st.warning("Overall, your mood has been neutral. 😐")
else:
    st.write("No mood logs available yet.")

# Mood Line Graph Over Time
st.header("Mood Over Time")
if not st.session_state.mood_logs.empty:
    # Map moods to numerical values
    mood_logs_with_numeric = st.session_state.mood_logs.copy()
    mood_logs_with_numeric["Mood Numeric"] = mood_logs_with_numeric["Mood"].map(mood_mapping)
    
    # Plot mood over time
    fig = px.line(
        mood_logs_with_numeric,
        x="Date",
        y="Mood Numeric",
        title="Mood Over Time",
        labels={"Mood Numeric": "Mood", "Date": "Date"},
        line_shape="spline",
        markers=True,
    )
    fig.update_traces(line_color="#4A90E2", marker_color="#4A90E2")
    fig.update_yaxes(tickvals=list(mood_mapping.values()), ticktext=list(mood_mapping.keys()))
    st.plotly_chart(fig)
else:
    st.write("No mood logs available yet.")

# Sentiment Trend Over Time
st.header("Sentiment Trend Over Time")
if not st.session_state.mood_logs.empty:
    sentiment_trend = st.session_state.mood_logs.groupby('Date')['Sentiment'].mean().reset_index()
    fig = px.line(sentiment_trend, x='Date', y='Sentiment', title='Sentiment Trend Over Time', 
                  labels={'Sentiment': 'Sentiment Score', 'Date': 'Date'}, 
                  line_shape='spline', markers=True)
    fig.update_traces(line_color='#4A90E2', marker_color='#4A90E2')
    st.plotly_chart(fig)
else:
    st.write("No mood logs available yet.")

# Additional Insights
st.header("Additional Insights")
if not st.session_state.mood_logs.empty:
    st.subheader("Most Common Moods")
    mood_counts = st.session_state.mood_logs['Mood'].value_counts()
    st.bar_chart(mood_counts)
else:
    st.write("No mood logs available yet.")