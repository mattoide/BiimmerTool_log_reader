import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import dash.exceptions
import base64
import io

# Crea l'app Dash
app = dash.Dash(__name__)
app.title = "Visualizzatore CSV"

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

        dcc.Upload(
            id='upload-data',
            children=html.Button("Carica un file CSV"),
            multiple=False,
            style={'textAlign': 'center', 'marginBottom': '10px'}
        ),

        html.Div(
            style={'textAlign': 'center', 'marginBottom': '10px'},
            children=[
                html.Button("Seleziona/Deseleziona Tutte", id="toggle-button", n_clicks=0)
            ]
        ),

        dcc.Checklist(
            id='selezione-dati',
            options=[],  # Inizialmente vuoto
            value=[],  # Valore vuoto iniziale
            inline=True
        ),

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

# Funzione per elaborare il CSV
def process_csv(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

    if 'Time' in df.columns:
        df['Time'] = df['Time'].astype(str).str.replace(',', '.')
        df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S.%f', errors='coerce')

    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

@app.callback(
    [Output('selezione-dati', 'options'), Output('selezione-dati', 'value'), Output('grafico', 'figure')],
    [Input('upload-data', 'contents'), Input('toggle-button', 'n_clicks'), Input('selezione-dati', 'value')],
    [State('selezione-dati', 'options')]
)
def aggiorna_dati(contents, n_clicks, colonne_selezionate, colonne_attuali):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    # Se i dati sono stati caricati
    if trigger_id == 'upload-data' and contents:
        df = process_csv(contents)
        y_columns = df.columns[1:]
        return [{'label': col, 'value': col} for col in y_columns], list(y_columns), px.line(df, x='Time', y=list(y_columns))

    # Se è stato premuto il pulsante "Seleziona/Deseleziona Tutte"
    if trigger_id == 'toggle-button':
        if colonne_selezionate and len(colonne_selezionate) == len(colonne_attuali):
            # Se tutte le colonne sono selezionate, deseleziona tutte
            return colonne_attuali, [], {
                'data': [],
                'layout': {
                    'title': 'Nessuna colonna selezionata',
                    'xaxis': {'title': 'Time'},
                    'yaxis': {'title': 'Valore'}
                }
            }
        else:
            # Se non tutte le colonne sono selezionate, ricarica i dati e seleziona tutte le colonne
            df = process_csv(contents)
            y_columns = df.columns[1:]
            return [{'label': col, 'value': col} for col in y_columns], list(y_columns), px.line(df, x='Time', y=list(y_columns))

    # Quando l'utente cambia la selezione delle colonne
    if trigger_id == 'selezione-dati':
        df = process_csv(contents) if contents else pd.DataFrame()
        if not df.empty:
            # Se non ci sono colonne selezionate, visualizza un grafico vuoto o messaggio
            if not colonne_selezionate:
                return colonne_attuali, [], {
                    'data': [],
                    'layout': {
                        'title': 'Nessuna colonna selezionata',
                        'xaxis': {'title': 'Time'},
                        'yaxis': {'title': 'Valore'}
                    }
                }
            # Crea il grafico con le colonne selezionate
            return colonne_attuali, colonne_selezionate, px.line(df, x='Time', y=colonne_selezionate)

    raise dash.exceptions.PreventUpdate

if __name__ == '__main__':
    app.run_server(debug=True)
