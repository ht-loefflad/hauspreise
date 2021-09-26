# TODO: Load data from online source
# TODO: Add correct source for scraped prices
# TODO: Add radio_button for changing between house and flat prices per square meter

import json
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Load data
with open('data/landkreise_simplify200.geojson', encoding="utf-8") as response:
    counties = json.load(response)
#
df_hauspreis = pd.read_csv("data/price_test.csv", index_col=0, dtype={"RS": object})

df_hauspreis["Price"] = df_hauspreis["Price"].str.replace(" €", "")
df_hauspreis["Price"] = df_hauspreis["Price"].str.replace(".", "", regex=False)
df_hauspreis["Price"] = pd.to_numeric(df_hauspreis["Price"], downcast="float")
df = df_hauspreis.loc[(df_hauspreis["Quarter"] == "2020/Q3") & (df_hauspreis["Houseprice"] == 1)]

quarters_ = df_hauspreis["Quarter"].unique()

quarters = [
    dict(label=quarter, value=quarter)
    for quarter in quarters_]


radio_quarters_behaviour = dcc.RadioItems(
    id='Quarters',
    options=quarters,
    value=quarters_[0],
    labelStyle={'display': 'block', "text-align": "justify"}

)

layout = dict(
    autosize=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    mapbox=dict(
        style="light",
        center=dict(lon=-78.05, lat=42.54),
        zoom=7,
    ),
)

app = dash.Dash(__name__)

# Create app layout
app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H4(
                                    "House price characteristics of Germany",
                                    style={"font-weight": "bold"},
                                ),
                            ]
                        )
                    ],
                    className="column",
                    id="title",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H6("House prices by quarter",
                                style={"margin-top": "0", "font-weight": "bold", "text-align": "center"}),

                        html.P(
                            "The average house price across Germany differ widely."
                            " The map on the right explores the square meter prices across Germany.",
                            className="control_label", style={"text-align": "justify"}
                        ),
                        html.P(),
                        html.P("Select a quarter", className="control_label",
                               style={"text-align": "center", "font-weight": "bold"}),
                        radio_quarters_behaviour,

                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                    style={"text-align": "justify"},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.P(id="gasText"),
                                     html.P("Minimum", style={"text-align": "center", "font-weight": "bold"}),
                                     html.P(id="min_name", style={"text-align": "center"}),
                                     html.P(id="min_value", style={"text-align": "center"}),
                                     ],
                                    className="mini_container",
                                    id="gas"
                                ),
                                html.Div(
                                    [html.P(id="oilText"),
                                     html.P("Mean", style={"text-align": "center", "font-weight": "bold"}),
                                     html.P(id="mean", style={"text-align": "center"}),
                                     html.P("Standard deviation",
                                            style={"text-align": "center", "font-weight": "bold"}),
                                     html.P(id="st_dev", style={"text-align": "center"})],
                                    className="mini_container",
                                    id="oil",
                                ),
                                html.Div(
                                    [
                                        html.P(id="well_text"),
                                        html.P("Maximum", style={"text-align": "center", "font-weight": "bold"}),
                                        html.P(id="max_name", style={"text-align": "center"}),
                                        html.P(id="max_value", style={"text-align": "center"}),
                                    ],
                                    className="mini_container",
                                    id="wells",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        html.Div(
                            [dcc.Graph(id="choropleth")],
                            className="pretty_container",
                        ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.H6("Author", style={"margin-top": "0", "font-weight": "bold", "text-align": "center"}),

                html.P(
                    "Hans Torben Löfflad",
                    style={"text-align": "center", "font-size": "10pt"}),

            ],
            className="row pretty_container",
        ),
        html.Div(
            [
                html.H6("Sources", style={"margin-top": "0", "font-weight": "bold", "text-align": "center"}),
                dcc.Markdown(
                    """\
                         - Geojson, Kreise: http://opendatalab.de/projects/geojson-utilities/
                         - Hauspreisdaten, gescrapted von: https://www.homeday.de/de/preisatlas
                         - Made use of this amazing template: https://github.com/FranzMichaelFrank/health_eu
                        """
                    , style={"font-size": "10pt"}),

            ],
            className="row pretty_container",
        ),

    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


@app.callback(
    Output("choropleth", "figure"),
    [Input("Quarters", "value")])
def display_choropleth(auswahl):
    df_auswahl = df_hauspreis.loc[(df_hauspreis["Quarter"] == auswahl) & (df_hauspreis["Houseprice"] == 1)]
    hauspreis_figure = px.choropleth_mapbox(df_auswahl
                                            , geojson=counties
                                            , locations='RS'
                                            , featureidkey="properties.RS"
                                            , hover_name='GEN'
                                            , color='Price'
                                            , color_continuous_scale="Viridis"
                                            , range_color=(600, 6000)
                                            , mapbox_style="white-bg"  # "carto-positron" gives a world map
                                            , zoom=4.6
                                            , center={"lat": 51.3, "lon": 9.3}
                                            , opacity=.9
                                            , animation_frame='Quarter'  # use with slider over quarters
                                            )
    hauspreis_figure.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return hauspreis_figure


@app.callback(
    [
        Output("max_name", "children"),
        Output("max_value", "children"),
        Output("min_name", "children"),
        Output("min_value", "children"),
        Output("mean", "children"),
        Output("st_dev", "children"),
    ],
    [
        Input("Quarters", "value"),
    ]
)
def indicator(auswahl):
    df_auswahl = df_hauspreis.loc[(df_hauspreis["Quarter"] == auswahl) & (df_hauspreis["Houseprice"] == 1)]
    max_id = df_auswahl["Price"].idxmax()
    min_id = df_auswahl["Price"].idxmin()
    print(max_id)

    max_value = df_auswahl["Price"].max()
    max_value = str(int(max_value))
    max_name = df_auswahl.loc[max_id, "GEN"]

    min_value = df_auswahl["Price"].min()
    min_value = str(int(min_value))
    min_name = df_auswahl.loc[min_id, "GEN"]

    mean = df_auswahl["Price"].mean()
    st_dev = df_auswahl["Price"].std()

    st_dev = round(st_dev, 0)
    st_dev = str(int(st_dev))
    mean = round(mean, 0)
    mean = str(int(mean))
    return "County: " + max_name, max_value + " € per square meter", \
           "County: " + min_name, min_value + " € per square meter", \
           mean + " € per square meter", \
           st_dev + " € per square meter",


server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
