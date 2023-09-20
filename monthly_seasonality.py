import sqlite3
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
from datetime import datetime
from plotly.subplots import make_subplots

def print_stats(data, months, measure):
    for i, month in enumerate(months):
        print(f"{month}: {data[i]:.4f}")

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
table_name = 'BTCUSDT_1M'
limit = 0
offset = 0

data = get_data_from_db(db_path, table_name, limit, offset)
data['close_time'] = pd.to_datetime(data['close_time'], unit='ms')

# Calculate daily returns
data['daily_returns'] = (data['close'] - data['open']) / data['open']

# Group by month and accumulate returns
data['month'] = data['close_time'].dt.month
cumulative_returns = data.groupby('month')['daily_returns'].cumsum()

# Calculate average daily return for each month
average_daily_returns = data.groupby('month')['daily_returns'].mean()

# Print average daily returns
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
for i, month in enumerate(months):
    print(f"{month}: {average_daily_returns[i+1]:.4f}")

today = datetime.today()
current_month = today.month

# Create a line chart for cumulative daily returns
fig = go.Figure()

colors = ['rgba(255, 0, 0', 'rgba(0, 0, 255', 'rgba(0, 255, 0', 'rgba(255, 255, 0', 'rgba(255, 183, 176', 'rgba(255, 145, 0', 'rgba(0, 255, 255', 'rgba(255, 51, 153', 'rgba(153, 51, 255', 'rgba(0, 204, 204', 'rgba(204, 102, 0', 'rgba(102, 102, 255']

fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                    subplot_titles=(""))

# Add the line chart traces to the top subplot
for i, month in enumerate(months):
    if current_month - 1 == i:
        fig.add_trace(go.Scatter(x=data.loc[data['month'] == i+1, 'close_time'],
                                y=cumulative_returns[data['month'] == i+1],
                                mode='lines',
                                name=month,
                                line=dict(color=f"{colors[i]}, 1)", width=3)),
                    row=1, col=1)
    else:
        fig.add_trace(go.Scatter(x=data.loc[data['month'] == i+1, 'close_time'],
                                y=cumulative_returns[data['month'] == i+1],
                                mode='lines',
                                name=month,
                                line=dict(color=f"{colors[i]}, 0.4)", width=1)),
                    row=1, col=1)
fig.update_layout(
    title="BTC Cumulative Daily Returns by Month",
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
pio.write_html(fig, file="cumulative_monthly_returns.html", full_html=True, include_plotlyjs='cdn', auto_open=True, config={'scrollZoom': True})
