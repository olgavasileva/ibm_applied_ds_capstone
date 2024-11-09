# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                    dcc.Dropdown(
                                        id='site-dropdown',
                                        options=[
                                            {'label': 'All Sites', 'value': 'ALL'},
                                            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                        ],
                                        value='ALL',  # Default value
                                        placeholder="Select a Launch Site here",
                                        searchable=True,
                                        style={'width': '50%'}
                                    ),
                                html.Br(),
                                #2
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),
                                #3
                                html.P("Payload range (Kg):"),
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    marks={i: str(i) for i in range(min_payload.astype(int), max_payload.astype(int)+1, 1000)},
                                    value=[min_payload, max_payload]
                                ),
                                #4
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2: Add a pie chart to show the total successful launches count for all sites
# If a specific launch site was selected, show the Success vs. Failed counts for the site                                    
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df.groupby('class').size().reset_index(name='counts')
    filtered_df['class'] = filtered_df['class'].map({0: 'Failure', 1: 'Success'})
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, values='counts', 
        names='class', 
        title='Launch Success vs. Failure')
        return fig
    else:
        df = spacex_df[spacex_df['Launch Site'] == entered_site]
        filtered_df = df.groupby('class').size().reset_index(name='counts')
        fig = px.pie(filtered_df, names='class', values='counts', title=f'{entered_site} Launch Success vs. Failure')
        return fig

        # return the outcomes piechart for a selected site

                                
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success



# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_plot(entered_site, payload_range):
    min_payload, max_payload = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= min_payload) & 
                            (spacex_df['Payload Mass (kg)'] <= max_payload)]

    if entered_site == 'ALL':
        df = filtered_df
        entered_site = 'All Sites'
    else:
        df = filtered_df[filtered_df['Launch Site'] == entered_site]

    df["class"] = df["class"].astype(str)

    fig = px.scatter(
        df, 
        x='Payload Mass (kg)', 
        y='class', 
        color='class',
        color_discrete_sequence=['red', 'blue'],  # Map 0 to red and 1 to blue
        labels={'class': 'Launch Success'},
        title=f'Payload vs. Launch Outcome for {entered_site}'
    )
    # Update y-axis to show only ticks at 0 and 1
    fig.update_yaxes(tickvals=[0, 1], ticktext=["Failure", "Success"], autorange="reversed")
    fig.update_layout(showlegend=False)
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
