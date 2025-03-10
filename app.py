import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Carica il file CSV
CSV_FILE = "actual-expected_2025-03-07_204227.csv"

# Crea l'app Dash
app = dash.Dash(__name__)

# Carica i dati dal CSV
df = pd.read_csv(CSV_FILE)

# Preprocessing per il formato del tempo
df['Time'] = df['Time'].str.replace(',', '.')  # Sostituisci la virgola con il punto nel tempo
df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S.%f')

# Sostituisci la virgola con il punto per tutte le colonne numeriche
df[df.columns[1:]] = df[df.columns[1:]].applymap(lambda x: str(x).replace(',', '.'))

# Converte tutte le colonne tranne 'Time' in numerico, ignorando eventuali errori
df[df.columns[1:]] = df[df.columns[1:]].apply(pd.to_numeric, errors='coerce')

# Gestione dei valori NaN (opzionale: rimuovere o sostituire NaN)
df = df.dropna()  # Rimuove le righe con valori NaN (puoi anche sostituirli con un valore specifico, se preferisci)

# Definisci le colonne (escludendo 'Time')
y_columns = df.columns[1:]

# Layout dell'app
app.layout = html.Div([
    html.H1("Grafico Interattivo con Dati CSV"),

    # Selettore per le checkbox delle colonne
    dcc.Checklist(
        id='selezione-dati',
        options=[{'label': col, 'value': col} for col in y_columns],
        value=list(y_columns),  # Mostra tutte le colonne di default
        inline=True
    ),

    # Grafico
    dcc.Graph(id='grafico')
])

@app.callback(
    Output('grafico', 'figure'),
    [Input('selezione-dati', 'value')]
)
def aggiorna_grafico(colonne_selezionate):
    if not colonne_selezionate:
        return px.line(title="Seleziona almeno una colonna da visualizzare")

    # Crea il grafico con le colonne selezionate
    fig = px.line(df, x='Time', y=colonne_selezionate, title="Dati CSV Interattivi")

    # Aggiungi hover_data per visualizzare i valori delle colonne selezionate
    fig.update_traces(
        hovertemplate="<br>".join([
            f"{col}: %{{customdata[{i}]}}" for i, col in enumerate(colonne_selezionate)
        ])
    )

    # Aggiungi customdata per legare i dati delle colonne selezionate
    fig.update_traces(customdata=df[colonne_selezionate].values)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
