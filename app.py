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
            value=[],    # Valore vuoto iniziale
            inline=True
        ),
        dcc.Graph(
            id='grafico',
            style={
                'flex': '1',
                'width': '100%',
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

# Funzione helper per impostare customdata e hovertemplate
def update_hover(fig, df, cols):
    # Per ogni traccia, settiamo customdata con i valori di tutte le colonne
    # e costruiamo un hovertemplate che mostra Time e ogni colonna con il suo valore.
    for trace in fig.data:
        trace.customdata = df[cols].values
        trace.hovertemplate = (
                "Time: %{x}<br>" +
                "<br>".join([f"{col}: %{{customdata[{i}]}}" for i, col in enumerate(cols)]) +
                "<extra></extra>"
        )
    return fig

@app.callback(
    [Output('selezione-dati', 'options'),
     Output('selezione-dati', 'value'),
     Output('grafico', 'figure')],
    [Input('upload-data', 'contents'),
     Input('toggle-button', 'n_clicks'),
     Input('selezione-dati', 'value')],
    [State('selezione-dati', 'options')]
)
def aggiorna_dati(contents, n_clicks, colonne_selezionate, colonne_attuali):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    # Caso: Caricamento del file CSV
    if trigger_id == 'upload-data' and contents:
        df = process_csv(contents)
        y_columns = df.columns[1:]
        fig = px.line(df, x='Time', y=list(y_columns))
        fig = update_hover(fig, df, list(y_columns))
        return [{'label': col, 'value': col} for col in y_columns], list(y_columns), fig

    # Caso: Pulsante "Seleziona/Deseleziona Tutte"
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
            # Altrimenti, ricarica i dati e seleziona tutte le colonne
            df = process_csv(contents)
            y_columns = df.columns[1:]
            fig = px.line(df, x='Time', y=list(y_columns))
            fig = update_hover(fig, df, list(y_columns))
            return [{'label': col, 'value': col} for col in y_columns], list(y_columns), fig

    # Caso: Selezione manuale delle colonne
    if trigger_id == 'selezione-dati':
        df = process_csv(contents) if contents else pd.DataFrame()
        if not df.empty:
            if not colonne_selezionate:
                return colonne_attuali, [], {
                    'data': [],
                    'layout': {
                        'title': 'Nessuna colonna selezionata',
                        'xaxis': {'title': 'Time'},
                        'yaxis': {'title': 'Valore'}
                    }
                }
            fig = px.line(df, x='Time', y=colonne_selezionate)
            fig = update_hover(fig, df, colonne_selezionate)
            return colonne_attuali, colonne_selezionate, fig

    raise dash.exceptions.PreventUpdate

if __name__ == '__main__':
    app.run_server(debug=True)
