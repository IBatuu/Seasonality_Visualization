import sqlite3
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
from datetime import datetime
from plotly.subplots import make_subplots

def get_data_from_db(db_path, table_name, limit=None, offset=None):
    conn = sqlite3.connect(db_path)
    if not limit and not offset:
        data = pd.read_sql(f"SELECT * FROM {table_name} ORDER BY close_time DESC", conn)
    elif limit and not offset:
        data = pd.read_sql(f"SELECT * FROM {table_name} ORDER BY close_time DESC LIMIT {limit}", conn)
    else:
        data = pd.read_sql(f"SELECT * FROM {table_name} ORDER BY close_time DESC LIMIT {limit} OFFSET {offset}", conn)
    data.sort_values(by='close_time', ascending=True, inplace=True)
    data.reset_index(drop=True, inplace=True)
    return data

db_path = "" #Db Path
table_name = 'BTCUSDT_1w'
limit = 0
offset = 0

data = get_data_from_db(db_path, table_name, limit, offset)
data['close_time'] = pd.to_datetime(data['close_time'], unit='ms')

# Calculate daily returns
data['daily_returns'] = (data['close'] - data['open']) / data['open']

# Group by week of month and accumulate returns
data['week_of_month'] = data['close_time'].apply(lambda x: (x.day - 1) // 7)
cumulative_returns = data.groupby('week_of_month')['daily_returns'].cumsum()

# Calculate average daily return for each week of month
average_daily_returns = data.groupby('week_of_month')['daily_returns'].mean()

# Print average daily returns
weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
for i, week in enumerate(weeks):
    print(f"{week}: {average_daily_returns[i]:.4f}")

today = datetime.today()
first_day_of_month = datetime(today.year, today.month, 1)
current_weekday = today.weekday()

# Calculate the number of days between the first day of the month and today
days_since_first_day = (today - first_day_of_month).days

# Calculate the current week of the month
current_week_of_month = (days_since_first_day + first_day_of_month.weekday()) // 7

if first_day_of_month.weekday() <= current_weekday:
    current_week_of_month += 1

# Create a line chart for cumulative daily returns
fig = go.Figure()

colors = ['rgba(255, 0, 0', 'rgba(0, 0, 255', 'rgba(0, 255, 0', 'rgba(255, 255, 0']

# Create a subplot with the line chart on top 
fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                    subplot_titles=())

# Add the line chart traces to the top subplot
for i, week in enumerate(weeks):
    print(i, week)
    if current_week_of_month - 1 == i:
        fig.add_trace(go.Scatter(x=data.loc[data['week_of_month'] == i, 'close_time'],
                             y=cumulative_returns[data['week_of_month'] == i],
                             mode='lines',
                             name=week,
                             line=dict(color=f"{colors[i]}, 3)", width=3)),
                  row=1, col=1)
    else:
        fig.add_trace(go.Scatter(x=data.loc[data['week_of_month'] == i, 'close_time'],
                             y=cumulative_returns[data['week_of_month'] == i],
                             mode='lines',
                             name=week,
                             line=dict(color=f"{colors[i]}, 0.4)", width=1)),
                  row=1, col=1)

fig.update_layout(
    title="BTC Cumulative by Week of a Month",
    xaxis_title="Date",
    yaxis_title="Cumulative Returns",
    plot_bgcolor="black",
    paper_bgcolor="black",
    xaxis_rangeslider_visible=False,
    xaxis=dict(
        type="date",
        tickformat="%Y-%m-%d",
        tickmode="auto",
        nticks=30,
        gridcolor="rgba(0, 0, 0, 0)",
        zerolinecolor="rgba(0, 0, 0, 1)",
        tickfont=dict(color="white")
    ),
    yaxis=dict(
        type="linear",
        gridcolor="rgba(0, 0, 0, 0)",
        zerolinecolor="rgba(0, 0, 0, 1)",
        tickfont=dict(color="white")
    ),
    title_font=dict(color="grey"),
    legend=dict(font=dict(color="grey")),
    margin=dict(t=50, b=50, l=50, r=50)
)

# Save the chart as an HTML file with a black background
pio.write_html(fig, file="cumulative_daily_returns_by_week_of_month.html", full_html=True, include_plotlyjs='cdn', auto_open=True, config={'scrollZoom': True})

