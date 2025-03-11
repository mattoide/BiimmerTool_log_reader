import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px

# Carica il file CSV
# CSV_FILE = "actual-expected_2025-03-07_204227.csv"
CSV_FILE = "actual-expected_2025-03-10_193834.csv"
# CSV_FILE = "actual-expected_2025-03-10_195213.csv"

# Crea l'app Dash
app = dash.Dash(__name__)

# Carica i dati dal CSV
df = pd.read_csv(CSV_FILE)

# Preprocessing per il formato del tempo
df['Time'] = df['Time'].str.replace(',', '.')
df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S.%f')

# Sostituisce la virgola con il punto per le colonne numeriche
df[df.columns[1:]] = df[df.columns[1:]].applymap(lambda x: str(x).replace(',', '.'))

# Converte tutte le colonne tranne 'Time' in numerico
df[df.columns[1:]] = df[df.columns[1:]].apply(pd.to_numeric, errors='coerce')

# Rimuove eventuali righe con valori NaN
# df = df.dropna()

# Colonne Y (tutte tranne 'Time')
y_columns = df.columns[1:]

# Layout dell'app
app.layout = html.Div(
    style={
        'width': '100vw',
        'height': '100vh',
        'margin': '0',
        'padding': '0',
        'display': 'flex',
        'flexDirection': 'column'
    },
    children=[
        html.H1("Grafico Interattivo con Dati CSV", style={'textAlign': 'center'}),

        # Contenitore per il pulsante e la checklist
        html.Div(
            style={'padding': '10px', 'textAlign': 'center'},
            children=[
                html.Button("Seleziona/Deseleziona Tutte", id="toggle-button", n_clicks=0),
                html.Br(), html.Br(),

                # Contenitore per le checkbox con layout flessibile
                html.Div(
                    id='checklist-container',
                    style={
                        'display': 'flex',
                        'flexWrap': 'wrap',  # Le checkbox vanno a capo automaticamente
                        'gap': '10px',  # Spazio tra le checkbox
                        'justifyContent': 'center',
                        'padding': '5px'
                    },
                    children=[
                        dcc.Checklist(
                            id='selezione-dati',
                            options=[{'label': col, 'value': col} for col in y_columns],
                            value=[],  # Di default nessuna selezionata
                            inline=True  # Checkbox in riga, ma con wrapping
                        )
                    ]
                )
            ]
        ),

        # Grafico che occupa tutto lo spazio rimanente
        dcc.Graph(
            id='grafico',
            style={
                'flex': '1',        # Occupa tutto lo spazio disponibile
                'width': '100%',    # Usa tutta la larghezza
                'margin': '0',
                'padding': '0'
            }
        )
    ]
)

@app.callback(
    Output('selezione-dati', 'value'),
    Input('toggle-button', 'n_clicks'),
    State('selezione-dati', 'value')
)
def toggle_colonne(n_clicks, colonne_selezionate):
    """
    Se nessuna colonna è selezionata, seleziona tutte;
    altrimenti, deseleziona tutte.
    """
    if n_clicks == 0:
        raise dash.exceptions.PreventUpdate  # Non fare nulla al primo avvio

    return list(y_columns) if len(colonne_selezionate) == 0 else []

@app.callback(
    Output('grafico', 'figure'),
    Input('selezione-dati', 'value')
)
def aggiorna_grafico(colonne_selezionate):
    if not colonne_selezionate:
        return px.line(title="Seleziona almeno un parametro da visualizzare")

    fig = px.line(df, x='Time', y=colonne_selezionate, title="Dati CSV Interattivi")

    # Tooltip personalizzato che mostra tutti i valori selezionati
    hover_template = "<br>".join([f"{col}: %{{customdata[{i}]}}" for i, col in enumerate(colonne_selezionate)])
    fig.update_traces(customdata=df[colonne_selezionate].values, hovertemplate=hover_template)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
