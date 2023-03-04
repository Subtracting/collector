from datetime import date
from dash import Dash, html, dcc, Input, Output, State, dash_table, ctx
import plotly.express as px
import pandas as pd
import sqlite3
import dash_bootstrap_components as dbc
from logstats import logger
from weather import *
from newscrape import get_news
from styling import *
from datetime import timedelta

graph_style = 'ggplot2'


def previous_dates():
    dates = []
    today = date.today()
    for i in range(0, 7):
        dates.append(today - timedelta(days=i))
    return dates


def get_data():
    conn = sqlite3.connect("stats.sqlite")

    stats_df = pd.read_sql_query("SELECT * from stats", conn)

    conn.close()

    agg_subject_df = stats_df.groupby('subject').agg(avg=('stat', 'mean'),
                                                     logs=('subject', 'count')).reset_index()
    agg_subject_df = agg_subject_df.round({'avg': 1})

    stats_df['date'] = pd.to_datetime(stats_df['date'])
    stats_df['weekday'] = stats_df['date'].dt.dayofweek
    days = {0: 'Mon', 1: 'Tue', 2: 'Wed',
            3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
    stats_df['weekday'] = stats_df['weekday'].apply(lambda x: days[x])
    stats_df = stats_df.sort_values('date')

    return stats_df, agg_subject_df


stats_df, agg_subject_df = get_data()
news_titles = get_news()
unique = stats_df['subject'].unique()
dates = previous_dates()

app = Dash(external_stylesheets=[dbc.themes.DARKLY])

options = {"Reading": "pages", "Sleep": "hours", "Euler": "# solved", "Drawing": "hours",
           "Mood": "rating (1/10)", "Running": "km", "Planking": "seconds", "Movies": "rating (1/10)"}

stat_table = dash_table.DataTable(agg_subject_df.to_dict(
    'records'), [{"name": i, "id": i} for i in agg_subject_df.columns],
    style_cell_conditional=[
        {'if': {'column_id': 'subject'},
         'width': '30%'}],
    style_header={
        'backgroundColor': '#404258',
        'color': 'white',
        'border': '1px solid #292829'},
    style_data={
        'color': 'grey',
        'backgroundColor': '#292829',
        'border': '1px solid #292829'},
    style_as_list_view=True
)

stat_input = dbc.Row(
    [
        dbc.Label("Result", html_for="result-row", width=1),
        dbc.Col(
            dbc.Input(id='stat', type='text', placeholder="Enter result",
                      style={'color': 'white', 'background-color': '#292829'}),
            width=2,
        ),
    ],
    className="mb-3",
)

comment_input = dbc.Row(
    [
        dbc.Label("Comment", html_for="comment-row", width=1),
        dbc.Col(
            dbc.Input(id='comment', type='text', placeholder="Enter comment",
                      style={'color': 'white', 'background-color': '#292829'}),
            width=2,
        ),
    ],
    className="mb-3",
)

submit_button = dbc.Button("Submit", id='submit-val', n_clicks=0,
                           color="dark", className="me-1")

dropdown = dbc.Row(
    [
        dbc.Label("Subject", html_for="subject-row", width=1),
        dbc.Col(
            dcc.Dropdown(
                id='subject-input',
                options=list(options),
                value='',
                clearable=False),
            width=2
        ),
    ],
    className="mb-3",
)

date_dropdown = dbc.Row(
    [
        dbc.Label("Date", html_for="subject-row", width=1),
        dbc.Col(
            dcc.Dropdown(
                id='date-input',
                options=dates,
                value=str(date.today()),
                clearable=False),
            width=2
        ),
    ],
    className="mb-3",
)

stat_graph = html.Div([
    html.Br(),
    dcc.Graph(id='bar-chart',
              config={'displayModeBar': False})],
    style={"margin": "20px"},
    className="card")

header = html.Div([

    html.Div([
        html.Div('Live Laugh Log', className="head1"),
        html.Br()
    ], style=head_style),


    html.Div(
        [
            html.H5("Bergen op Zoom weather"),
            html.Div(id='weather'),
            html.Div(id='humidity'),
            html.Div(id='wind'),
            dcc.Interval(
                id='interval-weather',
                interval=60*1000,
                n_intervals=0
            ),
            html.Br()], style=head_weather)
])

app.layout = html.Div(dbc.Container(
    [header,
     dcc.Tabs([
         #  first tab
         dcc.Tab(label='Dashboard', style=tab_style, selected_style=tab_selected_style, children=[
             html.Div([
                 dbc.Row([
                     dbc.Col([
                         stat_graph,

                     ], width=7),
                     dbc.Col([
                         # scatter
                         dbc.Row(html.Div(dcc.Graph(id='strip-chart',
                                 config={'displayModeBar': False}),
                             className="card", style={"margin": "20px", "padding": "0px"}))], width=4)
                 ]),
                 #  second row
                 dbc.Row([
                     dbc.Col([
                         #  buttons
                         dbc.Row(
                             dbc.Col(html.Div(children=[dbc.Button(subject, className="card", style={
                                 'margin-left': '3px', 'float': 'right', 'background-color': '#292828'},
                                 id=f'button-{subject}', n_clicks=0) for subject in stats_df['subject'].unique()]), style={"margin-right": "20px", "padding": "0px"}),
                         ),
                         dbc.Row(id='stat-boxes',
                                 style={"margin": "20px", "padding": "0px"})

                     ], width=7),
                     dbc.Col([
                         # table
                         dbc.Row(html.Div(stat_table,
                                 className="card", style={"margin": "20px", "padding": "0px"}))], width=4)
                 ]),

                 html.Div([
                     html.Div('Log-A-Stat', className="head1"),
                     html.Br(),
                     dropdown,
                     date_dropdown,
                     stat_input,
                     comment_input,
                     submit_button,
                     html.Div([], id='subject-output',
                              style={'display': 'none'}),
                     html.Br(),
                     html.Br()
                 ])

             ])

         ]),
         # second tab
         dcc.Tab(label='News feed', style=tab_style, selected_style=tab_selected_style, children=[
             html.Br(),
             html.H3("Headlines"),
             dbc.Row([

                 html.Div(dbc.Col(children=[html.Li(title, style={'list-style-type': 'None'}) for title in news_titles]),
                          className="head1", style={"margin": "20px", "padding-left": "20px", 'font-size': '20px', 'line-height': '200%'})

             ])
         ])
     ], style=tabs_styles)
     ], fluid=True), style={'padding-left': '30px', 'padding-right': '30px', 'padding-top': '20px'})


# callbacks

def stat_boxes(stats_df):
    children = []
    for i in range(1, 4):
        children.append(dbc.Col([html.H3(f"{stats_df['subject'].values[-i]}"), html.H4(f"{stats_df['date'].dt.date.values[-i]}"), html.Div(f"{stats_df['stat'].values[-i]} {options[str(stats_df['subject'].values[-i])]}")],
                                className="stat-box card"))

    return children


@ app.callback(
    [Output('bar-chart', 'figure'),
     Output('strip-chart', 'figure'),
     Output('stat-boxes', 'children')],
    [Input('subject-output', 'children')], [Input(f'button-{subject}', 'n_clicks')
                                            for subject in stats_df['subject'].unique()]
)
def update_figures(*args):

    if 'button' in str(ctx.triggered_id):
        selected_subject = str(ctx.triggered_id).split('-')[1]
    elif args[0] != '':
        selected_subject = args[0]
    else:
        selected_subject = "Sleep"

    stats_df, agg_subject_df = get_data()
    filtered_stats = stats_df[stats_df['subject'] == selected_subject]

    fig_line = px.line(filtered_stats, x="date", y="stat",
                       title=f"{selected_subject} ({options[selected_subject]})",
                       labels={'stat': options[selected_subject]},
                       template=f"{graph_style}",
                       markers=True
                       )

    fig_line.add_scatter(x=[fig_line.data[0].x[-1]],  # type: ignore
                         y=[fig_line.data[0].y[-1]],  # type: ignore
                         mode='markers + text',
                         marker={'color': 'salmon', 'size': 10},
                         showlegend=False,
                         text=[fig_line.data[0].y[-1]],  # type: ignore
                         textposition='middle right')

    fig_line.update_layout(
        xaxis=dict(
            title_font_color="grey",
            showgrid=False,
            tickformat='%d-%m'),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            visible=False,
            rangemode="tozero",
            ticklen=0))

    fig_line.update_layout(plot_bgcolor="#292829",
                           paper_bgcolor="#292829", font_color="white")

    fig_strip = update_box(selected_subject, filtered_stats)

    stat_boxes_output = stat_boxes(stats_df)

    return fig_line, fig_strip, stat_boxes_output


def update_box(selected_subject, filtered_stats):

    fig = px.box(filtered_stats, x="weekday", y="stat",
                 title=f"{selected_subject} by weekday",
                 color_discrete_sequence=px.colors.qualitative.T10)

    fig.update_layout(showlegend=False, template=f"{graph_style}", xaxis=dict(
        showgrid=False, title=None), yaxis=dict(showgrid=False, ticklen=0, title=None))

    fig.update_layout(plot_bgcolor="#292829",
                      paper_bgcolor="#292829", font_color="white")

    fig.update_yaxes(visible=False)

    return fig


@ app.callback(
    [Output('stat', 'value'),
     Output('comment', 'value'),
     Output('subject-output', 'children')
     ],
    Input('submit-val', 'n_clicks'),
    [State('subject-input', 'value'),
     State('date-input', 'value'),
     State('stat', 'value'),
     State('comment', 'value')])
def update_output(n_clicks, subject, date, stat, comment):
    if n_clicks > 0 and None not in [subject, stat]:
        logger(subject, date, stat, comment)
    return [None, None, subject]


weather_callback(app)


if __name__ == '__main__':
    app.run_server(debug=True)
