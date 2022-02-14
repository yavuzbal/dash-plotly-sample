import dash
from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
import dash_daq as daq
import plotly.express as px
from dash.exceptions import PreventUpdate
import pandas as pd

# reading csv files into DataFrames with pandas
df1 = pd.read_csv('data/transactions-season_1.csv')
df2 = pd.read_csv('data/transactions-season_2.csv')
df3 = pd.read_csv('data/transactions-season_3.csv')
df4 = pd.read_csv('data/transactions-season_4.csv')
df5 = pd.read_csv('data/products-season_1.csv')
df6 = pd.read_csv('data/products-season_2.csv')
df7 = pd.read_csv('data/products-season_3.csv')
df8 = pd.read_csv('data/products-season_4.csv')

# Merging Dataframes into one Dataframe
frames2 = [df5,df6,df7,df8]
products = pd.concat(frames2)

frames1 = [df1,df2,df3,df4]
transactions = pd.concat(frames1)

pd.options.display.float_format = "{:,.2f}".format

# Creating MONTHS column from 'DATE' column in dataframe
transactions['DATE'] = pd.to_datetime(transactions['DATE'])
transactions['MONTHS'] = transactions['DATE'].apply(lambda x:x.strftime('%B'))
transactions['DATE'] = pd.to_datetime(transactions['DATE'], format='%Y-%m-%d')

# Filtering the data for last one month
last_one_month = transactions[transactions['DATE'].dt.month == 1]

#Calculating revenue for each teansaction
transactions["REVENUE"] = transactions["UNIT"] * transactions["PROFIT"]

# Calculating revenue for each month
monthly_revenue = transactions.groupby('MONTHS')['REVENUE'].sum()
monthly_revenue= monthly_revenue.reset_index()

# unique costomer in last one month
unique_customer_id = last_one_month['CUSTOMER_ID'].value_counts()

# Calculating revenue for last month
one_mount_revenue = last_one_month['PROFIT'] * last_one_month['UNIT']
product_id=last_one_month['PRODUCT_ID'].value_counts()
lr_group=last_one_month['PRODUCT_ID']


# Renaming ID column for merging product and transaction Dataframes
products = products.rename(columns = {'ID':'PRODUCT_ID'})

# Filtering product that is used in last month
unique_id=list(product_id)
i1 = products.set_index('PRODUCT_ID').index
i2 = last_one_month.set_index('PRODUCT_ID').index
last1=products[~i1.isin(unique_id)]

# Filtering the Dataframe columns to not waste the memory. These columns are enough for tha graphs
product_group=products.loc[:, ['PRODUCT_ID','PRODUCT_GROUP_NAME']]
product_group_transaction= transactions.loc[:,['PRODUCT_ID','REVENUE','MONTHS','CUSTOMER_ID','SEASON','PROFIT']]
monthy_revenue =product_group_transaction.merge(product_group, how='inner', on='PRODUCT_ID')


app = dash.Dash(__name__)
server = app.server

app.config.suppress_callback_exceptions = False

# Web API
app.layout = html.Div(
    [
        html.Div(
            [
                html.Img(src="assets/images.png", className="app__logo"),
            ],
            className="app__header",
        ),
        html.Div(
            [
                dcc.Tabs(
                    id="tabs",
                    value="data-entry",
                    children=[
                        dcc.Tab(
                            id="tab1",
                            className="custom-tabs",
                            label="Overview",
                            value="data-entry",
                            children=[
                                html.Div(
                                            id="card-1",
                                            children=[

                                                html.Div( daq.LEDDisplay(
                                                    label="Last Month Active Customer",
                                                    id="operator-led",
                                                    value=len(unique_customer_id),
                                                    color="#FFBF00",
                                                    backgroundColor="#1C2833",
                                                    size=37,
                                                ),),
                                                html.Div( daq.LEDDisplay(
                                                    label="Last Month Revenue",
                                                    id="operator-led1",
                                                    value="{:.2f}".format(one_mount_revenue.sum()),
                                                    color="#FFBF00",
                                                    backgroundColor="#1C2833",
                                                    size=37,

                                                ),),
                                                html.Div(daq.LEDDisplay(
                                                    label="Last Month Average Discount(%)",
                                                    id="operator-led2",
                                                    value="{:.2f}".format(last1['PRODUCT_DISCOUNT_GROUP_PERCENTAGE'].mean()),
                                                    color="#FFBF00",
                                                    backgroundColor="#1C2833",
                                                    size=37,
                                                ),),
                                                html.Div(daq.LEDDisplay(
                                                    label="Average Product in Transactions",
                                                    id="operator-led3",
                                                    value="{:.2f}".format(transactions['UNIT'].mean()),
                                                    color="#FFBF00",
                                                    backgroundColor="#1C2833",
                                                    size=37,
                                                ),),
                                            ],

                                        ),
                                html.Div(
                                    id="month_bar",
                                    children=[
                                        dcc.Graph(
                                            figure={
                                                "data": [
                                                    {
                                                        "x": monthly_revenue["MONTHS"],
                                                        "y": monthly_revenue["REVENUE"],
                                                        "type": "bar",
                                                        'marker' : { "color" : '#A93226'}
                                                    },
                                                ],
                                                "layout": {"title": "Monthly Revenue"},
                                            },style={'width': '90%', 'height': '40vh'}
,
                                        ),
                                    ]
                                )

                            ],
                        ),
                        dcc.Tab(
                            label="Customer Analysis",
                            value="view-entry",
                            children=[
                            html.Div(
                                id='graph-3',
                                children=[]),
                                html.Div([
                                    html.Div([
                                        html.H3(children='Season Revenue and Profit', style={'text-align': 'center'}),
                                        dcc.Dropdown(
                                            id='dropdown_product_group',
                                            options=[{'label': p, 'value': p} for p in monthy_revenue['PRODUCT_GROUP_NAME'].unique()],
                                            value=['Product Group 1','Product Group 2'],
                                            multi=True,
                                        ),
                                        dcc.Dropdown(
                                            id='dropdown_customer',
                                            options=[{'label': p, 'value': p} for p in sorted(transactions['CUSTOMER_ID'].unique())],
                                            value=[1,2,3],
                                            multi=True,
                                        ),

                                        dcc.Graph(id='graph_profit')],
                                        style={'width': '48%', 'align': 'left','display': 'inline-block','vertical-align': 'bottom'}),

                                    html.Div([

                                        html.H3(children='Product Group Revenue', style={'text-align': 'center'}),
                                        dcc.Dropdown(
                                            id='dropdown_month',
                                            options=[{'label': p, 'value': p} for p in transactions['MONTHS'].unique()],
                                            value='January',style={'width': '85%', 'align': 'center'}),

                                        dcc.Graph(id='graph_month_revenue')],
                                        style={'width': '48%', 'align': 'right', 'display': 'inline-block'})
                                ]),

                            ],
                        ),
                    ],
                )
            ],
            className="tabs__container",
        ),
    ],
    className="app__container",
)


@app.callback(
    Output('graph_month_revenue', 'figure'),
    [Input(component_id='dropdown_month', component_property='value')]
)
def select_graph(value_month, monthy_revenue=monthy_revenue):
    # if there is no value in the dropbox the graph shows the last value excepted
    if not value_month:
        raise PreventUpdate

    else:
        # grouping dataframe by 'PRODUCT_GROUP_NAME', 'MONTHS' columns and calculatinf REVENUE columns for each group
        monthy_revenue = monthy_revenue.groupby(['PRODUCT_GROUP_NAME', 'MONTHS']).agg({'REVENUE': 'sum'}).reset_index()
        monthy_revenue = monthy_revenue[(monthy_revenue['MONTHS'] == value_month)]
        monthy_revenue['PRODUCT_GROUP_NAME'] = monthy_revenue['PRODUCT_GROUP_NAME'].map(lambda x: str(x)[14:])

        # creating the bar chart on filtered dataframe
        fig = px.bar(monthy_revenue, x='PRODUCT_GROUP_NAME', y='REVENUE')
        fig.update_traces(marker_color='#A93226')
        fig.update_layout(transition_duration=500,xaxis_title='Product Group', yaxis_title='Revenue')

        return fig



@app.callback(
    Output('graph_profit', 'figure'),
    [Input(component_id='dropdown_product_group', component_property='value'),
     Input(component_id='dropdown_customer', component_property='value')
    ]
)
def select_profit_revenue(value_product_group, value_customer_id, monthy_revenue=monthy_revenue):
    # if there is no value in the dropbox the graph shows the last value excepted
    if not value_product_group and value_customer_id:
        raise PreventUpdate
    else:
        # filtering dataframe by multiple dropdown values
        monthy_revenue2 = monthy_revenue[(monthy_revenue.CUSTOMER_ID.isin(value_customer_id)) & (monthy_revenue['PRODUCT_GROUP_NAME'].isin(value_product_group))]
        monthy_revenue2 = monthy_revenue2.groupby(['SEASON']).agg({'REVENUE': 'sum', 'PROFIT': 'sum'}).reset_index()

        # creating the bar chart on filtered dataframe
        fig = px.bar(monthy_revenue2, x='SEASON', y=["REVENUE", "PROFIT"],barmode = 'group')
        fig.update_layout(transition_duration=500,xaxis_title='Season', yaxis_title='Values')
        return fig


if __name__ == "__main__":
    app.run_server(debug=True)