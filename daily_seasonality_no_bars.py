import sqlite3
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
from datetime import datetime
from plotly.subplots import make_subplots

# Add other statistical measures
def print_stats(data, weekdays, measure):
    for i, weekday in enumerate(weekdays):
        print(f"{weekday}: {data[i]:.4f}")

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
table_name = 'BTCUSDT_1d'
limit = 0
offset = 0

data = get_data_from_db(db_path, table_name, limit, offset)
data['close_time'] = pd.to_datetime(data['close_time'], unit='ms')

# Calculate daily returns
data['daily_returns'] = (data['close'] - data['open']) / data['open']

# Group by weekday and accumulate returns
data['weekday'] = data['close_time'].dt.weekday
cumulative_returns = data.groupby('weekday')['daily_returns'].cumsum()

# Calculate average daily return for each weekday
average_daily_returns = data.groupby('weekday')['daily_returns'].mean()

# Print average daily returns
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
for i, weekday in enumerate(weekdays):
    print(f"{weekday}: {average_daily_returns[i]:.4f}")

# Calculate standard deviation of daily returns for each weekday
std_daily_returns = data.groupby('weekday')['daily_returns'].std()

# Calculate minimum daily return for each weekday
min_daily_returns = data.groupby('weekday')['daily_returns'].min()

# Calculate maximum daily return for each weekday
max_daily_returns = data.groupby('weekday')['daily_returns'].max()
# Print statistics
print("Average Daily Returns:")
print_stats(average_daily_returns, weekdays, "Average")
# Get the current weekday
current_weekday = datetime.today().weekday()

# Create a line chart for cumulative daily returns
fig = go.Figure()

colors = ['rgba(255, 0, 0', 'rgba(0, 0, 255', 'rgba(0, 255, 0', 'rgba(255, 255, 0', 'rgba(255, 183, 176', 'rgba(255, 145, 0', 'rgba(0, 255, 255']

# Create a subplot with the line chart on top 
fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                    subplot_titles=(""))

# Add the line chart traces to the top subplot
for i, weekday in enumerate(weekdays):
    print(i, weekday)
    if i == current_weekday:
        fig.add_trace(go.Scatter(x=data.loc[data['weekday'] == i, 'close_time'],
                                 y=cumulative_returns[data['weekday'] == i],
                                 mode='lines',
                                 name=weekday,
                                 line=dict(color=f"{colors[i]}, 1)", width=3)),
                      row=1, col=1)
    else:
        fig.add_trace(go.Scatter(x=data.loc[data['weekday'] == i, 'close_time'],
                                 y=cumulative_returns[data['weekday'] == i],
                                 mode='lines',
                                 name=weekday,
                                 line=dict(color=f"{colors[i]}, 0.5)", width=1)),
                      row=1, col=1)

fig.update_layout(
    title="BTC Cumulative Daily Returns by Weekday",
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
        zerolinecolor="rgba(0, 0, 0, 0)",
        tickfont=dict(color="white")
    ),
    yaxis=dict(
        type="linear",
        gridcolor="rgba(0, 0, 0, 0)",
        zerolinecolor="rgba(0, 0, 0, 0)",
        tickfont=dict(color="white")
    ),
    title_font=dict(color="grey"),
    legend=dict(font=dict(color="grey")),
    margin=dict(t=50, b=50, l=50, r=50)
)

# Save the chart as an HTML file with a black background
pio.write_html(fig, file="cumulative_daily_returns.html", full_html=True, include_plotlyjs='cdn', auto_open=True, config={'scrollZoom': True})
