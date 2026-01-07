import os
import pandas as pd
import numpy as np
from dash import Dash, html, dcc, Input, Output, State, dash_table, ctx
import plotly.express as px
import plotly.graph_objects as go


# Configuration & File Setup
BASE_PATH = r"C:\Users\91866\Downloads\Cricket_Dashboard (1)\Cricket_Dashboard"
if not os.path.exists(BASE_PATH):
    BASE_PATH = os.getcwd()

csv_files = [f for f in os.listdir(BASE_PATH) if f.endswith('.csv')]
file_options = [{'label': f, 'value': os.path.join(BASE_PATH, f)} for f in csv_files]
default_file = file_options[0]['value'] if file_options else None

app = Dash(__name__)
app.title = "Cricket Stats Dashboard"


# Styles
COLORS = {
    'background': '#f5f7fa',
    'card': '#ffffff',
    'primary': '#2563eb',
    'secondary': '#64748b',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'text': '#1e293b',
    'subtext': '#64748b',
    'border': '#e2e8f0'
}

header_style = {
    'background': 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
    'padding': '40px 20px',
    'marginBottom': '30px',
    'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
}

card_style = {
    'backgroundColor': COLORS['card'],
    'padding': '25px',
    'borderRadius': '12px',
    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
    'marginBottom': '20px',
    'border': f'1px solid {COLORS["border"]}'
}

stat_card_style = {
    'backgroundColor': COLORS['card'],
    'padding': '20px',
    'borderRadius': '10px',
    'textAlign': 'center',
    'boxShadow': '0 2px 6px rgba(0,0,0,0.08)',
    'border': f'1px solid {COLORS["border"]}',
    'minWidth': '180px',
    'flex': '1'
}

button_style = {
    'backgroundColor': COLORS['primary'],
    'color': 'white',
    'border': 'none',
    'borderRadius': '8px',
    'padding': '12px 24px',
    'fontSize': '14px',
    'fontWeight': '600',
    'cursor': 'pointer',
    'marginRight': '10px',
    'boxShadow': '0 2px 4px rgba(37,99,235,0.2)',
    'transition': 'all 0.3s'
}


# Layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1('🏏 Cricket Performance Analytics', 
                style={'textAlign': 'center', 'color': 'white', 'margin': 0, 'fontSize': '42px', 'fontWeight': '700'}),
        html.P("Dynamic Dashboard for Batting, Bowling & Team Stats", 
               style={'textAlign': 'center', 'color': 'rgba(255,255,255,0.9)', 'fontSize': '18px', 'marginTop': '10px'})
    ], style=header_style),

    # Controls
    html.Div([
        html.H3('🎛️ Control Panel', style={'color': COLORS['text'], 'marginBottom': '20px'}),
        html.Div([
            html.Label("Select Dataset File:", style={'fontWeight': '600', 'color': COLORS['text'], 'marginBottom': '8px'}),
            dcc.Dropdown(
                options=file_options, value=default_file, id='file-selector', placeholder="Select CSV...", clearable=False,
                style={'backgroundColor': 'white', 'color': COLORS['text'], 'border': f'2px solid {COLORS["border"]}'}
            )
        ], style={'marginBottom': '20px'}),

        html.Div([
            html.Div([
                html.Label("Filter by Name:", style={'fontWeight': '600', 'color': COLORS['text'], 'marginBottom': '8px'}),
                dcc.Dropdown(options=[], value=None, id='player-filter', placeholder="Select...", style={'backgroundColor': 'white', 'color': COLORS['text'], 'border': f'2px solid {COLORS["border"]}'})
            ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '3%', 'verticalAlign': 'top'}),

            html.Div([
                html.Label("Min Metric Value:", style={'fontWeight': '600', 'color': COLORS['text'], 'marginBottom': '8px'}),
                dcc.Input(id='metric-input', type='number', value=0, min=0, style={'width': '100%', 'padding': '10px', 'borderRadius': '6px', 'border': f'2px solid {COLORS["border"]}'})
            ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '3%', 'verticalAlign': 'top'}),

            html.Div([
                html.Label("Theme:", style={'fontWeight': '600', 'color': COLORS['text'], 'marginBottom': '8px'}),
                dcc.RadioItems(id='theme-selector', options=[{'label': ' Light', 'value': 'plotly_white'}, {'label': ' Dark', 'value': 'plotly_dark'}], value='plotly_white', inline=True, style={'color': COLORS['text']})
            ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        ]),

        html.Div([
            html.Button('🔄 Reset', id='reset-btn', n_clicks=0, style=button_style),
            html.Button('📊 Top 10', id='top10-btn', n_clicks=0, style={**button_style, 'backgroundColor': COLORS['success']}),
            html.Button('🏆 Leaders', id='leaders-btn', n_clicks=0, style={**button_style, 'backgroundColor': COLORS['warning']}),
            html.Button('⚡ Impact', id='impact-btn', n_clicks=0, style={**button_style, 'backgroundColor': COLORS['danger']}),
            html.Button('📄 PDF', id='export-pdf-btn', n_clicks=0, style={**button_style, 'backgroundColor': COLORS['secondary']})
        ], style={'marginTop': '25px'}),
        html.Div(id='status-message', style={'marginTop': '15px', 'color': COLORS['success'], 'fontWeight': '500'})
    ], style={**card_style, 'width': '90%', 'margin': '0 auto 30px auto'}),

    # Key Metrics
    html.Div([html.Div(id='stat-cards', style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '15px'})], style={'width': '90%', 'margin': '0 auto 30px auto'}),

    # Dynamic Chart Container (Flexbox)
    html.Div(id='charts-container', style={'width': '90%', 'margin': 'auto', 'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px', 'justifyContent': 'space-between'}),

    # Data Table
    html.Div([
        html.H3('📋 Detailed Statistics', style={'color': COLORS['text'], 'marginBottom': '20px'}),
        html.Div(id='data-table')
    ], style={**card_style, 'width': '90%', 'margin': '30px auto'}),

    # Footer
    html.Hr(style={'borderColor': COLORS['border'], 'marginTop': '50px'}),
    html.P("🏏 Cricket Analytics Dashboard", style={'textAlign': 'center', 'color': COLORS['subtext'], 'paddingBottom': '30px'})

], style={'fontFamily': 'Inter, system-ui, sans-serif', 'backgroundColor': COLORS['background'], 'minHeight': '100vh'})


# Callbacks
app.clientside_callback(
    """function(n) { if (n > 0) window.print(); }""",
    Output('export-pdf-btn', 'n_clicks'), Input('export-pdf-btn', 'n_clicks')
)

@app.callback(
    [Output('stat-cards', 'children'),
     Output('charts-container', 'children'),
     Output('data-table', 'children'),
     Output('player-filter', 'options'),
     Output('player-filter', 'value'),
     Output('metric-input', 'value'),
     Output('status-message', 'children')],
    [Input('file-selector', 'value'),
     Input('player-filter', 'value'),
     Input('metric-input', 'value'),
     Input('theme-selector', 'value'),
     Input('reset-btn', 'n_clicks'),
     Input('top10-btn', 'n_clicks'),
     Input('leaders-btn', 'n_clicks'),
     Input('impact-btn', 'n_clicks')]
)
def update_everything(selected_file, selected_entity, min_val, theme, reset, top10, leaders, impact):
    ctx_id = ctx.triggered_id
    status_msg = ""
    
    # Reset Logic
    if ctx_id == 'reset-btn': selected_entity, min_val, status_msg = None, 0, '✅ Reset!'
    elif ctx_id == 'top10-btn': min_val, status_msg = 0, '✅ Top 10'
    elif ctx_id == 'leaders-btn': status_msg = '✅ Leaders'
    elif ctx_id == 'impact-btn': status_msg = '✅ Impact'

    if not selected_file or not os.path.exists(selected_file):
        return [], html.Div("No File Selected"), [], [], selected_entity, min_val, "❌ Select a file"

    try:
        df = pd.read_csv(selected_file)
        
        #  DATA CLEANING 
        # 1. Strip whitespace from headers
        df.columns = df.columns.str.strip()
        
        # 2. REMOVE BLANK COLUMNS: Drop any column starting with "Unnamed"
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        # Detect Type
        data_type = "unknown"
        if 'Wkts' in df.columns: data_type = "bowling"
        elif 'Runs' in df.columns and 'Winner' not in df.columns: data_type = "batting"
        elif 'Winner' in df.columns: data_type = "team"

        # Clean Numeric
        numeric_cols = ['Mat', 'Inns', 'NO', 'Runs', 'BF', 'Ave', 'SR', '100', '50', '0', '4s', '6s', 'Wkts', 'Econ', 'Balls', 'Overs', 'Mdns', '4', '5', '10']
        for col in numeric_cols:
            if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        if 'HS' in df.columns:
            df['HS_Num'] = pd.to_numeric(df['HS'].astype(str).str.replace('*','', regex=False), errors='coerce').fillna(0)

        # Filter Options
        filter_col = 'Player' if 'Player' in df.columns else ('Series/Tournament' if 'Series/Tournament' in df.columns else None)
        filter_options = [{'label': p, 'value': p} for p in sorted(df[filter_col].dropna().unique())] if filter_col else []
        
    except Exception as e:
        return [], html.Div(f"Error: {str(e)}"), [], [], selected_entity, min_val, "❌ File Error"

    # Filter Data
    dff = df.copy()
    if data_type == "batting" and min_val > 0: dff = dff[dff['Runs'] >= min_val]
    elif data_type == "bowling" and min_val > 0: dff = dff[dff['Wkts'] >= min_val]

    if ctx_id == 'top10-btn':
        sort_col = 'Runs' if data_type == 'batting' else ('Wkts' if data_type == 'bowling' else None)
        if sort_col: dff = dff.nlargest(10, sort_col)
    elif ctx_id == 'leaders-btn':
        if data_type == 'batting' and '100' in dff.columns: dff = dff[dff['100'] >= 5]
        elif data_type == 'bowling' and '5' in dff.columns: dff = dff[dff['5'] >= 1]
    elif ctx_id == 'impact-btn':
        if data_type == 'batting' and 'SR' in dff.columns: dff = dff[dff['SR'] >= 100]
        elif data_type == 'bowling' and 'Econ' in dff.columns: dff = dff[dff['Econ'] <= 4.5]

    if selected_entity and filter_col: dff = dff[dff[filter_col] == selected_entity]
    dff.insert(0, 'S.No', range(1, 1 + len(dff)))

    # Generate Charts
    layout_args = dict(template=theme, paper_bgcolor='white' if theme=='plotly_white' else '#111827', 
                       plot_bgcolor='white' if theme=='plotly_white' else '#111827', 
                       font=dict(color=COLORS['text'] if theme=='plotly_white' else 'white'))
    
    figs_to_show = []

    def make_fig_div(fig):
        fig.update_layout(**layout_args)
        return html.Div([dcc.Graph(figure=fig)], style={
            **card_style, 
            'flex': '1 1 45%',         
            'minWidth': '400px',       
            'marginBottom': '20px'
        })

    def create_card(icon, title, value, color):
        return html.Div([html.Div(icon, style={'fontSize':'32px'}), html.H3(value, style={'color':color, 'margin':0}), html.P(title, style={'color':COLORS['subtext']})], style=stat_card_style)

    # BATTING
    if data_type == "batting":
        stat_cards = [
            create_card('👥', 'Players', f"{len(dff):,}", COLORS['primary']),
            create_card('🏏', 'Runs', f"{dff['Runs'].sum():,.0f}", COLORS['success']),
            create_card('💯', '100s', f"{dff['100'].sum() if '100' in dff.columns else 0:,}", COLORS['warning']),
            create_card('📊', 'Avg', f"{dff['Ave'].mean():.2f}", COLORS['danger'])
        ]
        figs_to_show.append(make_fig_div(px.bar(dff.nlargest(15, 'Runs'), x='Player', y='Runs', title='🏆 Top Runs', color='Runs')))
        if '100' in dff.columns: figs_to_show.append(make_fig_div(px.scatter(dff, x='50', y='100', size='Runs', color='Ave', title='🎯 50s vs 100s')))
        figs_to_show.append(make_fig_div(px.histogram(dff, x='Ave', nbins=20, title='📊 Average Dist')))
        if 'SR' in dff.columns and dff['SR'].sum()>0: figs_to_show.append(make_fig_div(px.scatter(dff, x='SR', y='Ave', size='Runs', color='Runs', title='⚡ SR vs Avg')))
        if '6s' in dff.columns and dff['6s'].sum()>0: figs_to_show.append(make_fig_div(px.pie(dff.nlargest(10, '6s'), names='Player', values='6s', title='💥 Sixes')))
        
        # Heatmap
        top15 = dff.nlargest(15, 'Runs')
        if not top15.empty:
            cols = [c for c in ['Runs', 'Ave', 'SR', '100'] if c in dff.columns]
            z = top15[cols].values
            z_norm = (z - z.min(axis=0)) / (z.max(axis=0) - z.min(axis=0) + 1e-9)
            figs_to_show.append(make_fig_div(go.Figure(data=go.Heatmap(z=z_norm, x=cols, y=top15['Player'], colorscale='Viridis', customdata=z, hovertemplate='%{y}<br>%{x}: %{customdata:.0f}'), layout=dict(title='🔥 Performance'))))

    # BOWLING
    elif data_type == "bowling":
        stat_cards = [
            create_card('👥', 'Bowlers', f"{len(dff):,}", COLORS['primary']),
            create_card('🎯', 'Wkts', f"{dff['Wkts'].sum():,.0f}", COLORS['success']),
            create_card('📉', 'Econ', f"{dff['Econ'].mean():.2f}", COLORS['warning']),
            create_card('🖐️', '5-W', f"{dff['5'].sum() if '5' in dff.columns else 0:,}", COLORS['danger'])
        ]
        figs_to_show.append(make_fig_div(px.bar(dff.nlargest(15, 'Wkts'), x='Player', y='Wkts', title='🏆 Top Wickets', color='Wkts')))
        figs_to_show.append(make_fig_div(px.scatter(dff, x='Econ', y='Ave', size='Wkts', color='Wkts', title='🎯 Econ vs Avg')))
        figs_to_show.append(make_fig_div(px.histogram(dff, x='Econ', nbins=20, title='📉 Econ Dist')))
        if 'SR' in dff.columns: figs_to_show.append(make_fig_div(px.scatter(dff, x='SR', y='Wkts', color='Ave', title='⚡ SR vs Wkts')))
        if '5' in dff.columns and dff['5'].sum()>0: figs_to_show.append(make_fig_div(px.bar(dff.nlargest(10, '5'), x='Player', y='5', title='🖐️ 5-Wickets')))
        
        # Heatmap
        top15 = dff.nlargest(15, 'Wkts')
        if not top15.empty:
            cols = [c for c in ['Wkts', 'Ave', 'Econ', 'SR'] if c in dff.columns]
            z = top15[cols].values
            z_norm = (z - z.min(axis=0)) / (z.max(axis=0) - z.min(axis=0) + 1e-9)
            figs_to_show.append(make_fig_div(go.Figure(data=go.Heatmap(z=z_norm, x=cols, y=top15['Player'], colorscale='Teal', customdata=z, hovertemplate='%{y}<br>%{x}: %{customdata:.2f}'), layout=dict(title='🔥 Performance'))))

    # TEAM
    elif data_type == "team":
        stat_cards = [
            create_card('📅', 'Seasons', f"{dff['Season'].nunique() if 'Season' in dff.columns else 0}", COLORS['primary']),
            create_card('🏆', 'Winners', f"{dff['Winner'].nunique() if 'Winner' in dff.columns else 0}", COLORS['success']),
            create_card('🏟️', 'Matches', f"{len(dff)}", COLORS['warning']),
            create_card('🏁', 'Draws', f"{len(dff[dff['Winner'].str.lower().isin(['drawn', 'tied'])]) if 'Winner' in dff.columns else 0}", COLORS['danger'])
        ]
        
        if 'Winner' in dff.columns:
            wc = dff['Winner'].value_counts().reset_index()
            wc.columns = ['Team', 'Wins']
            figs_to_show.append(make_fig_div(px.bar(wc.head(10), x='Team', y='Wins', title='🏆 Most Wins', color='Wins')))
            figs_to_show.append(make_fig_div(px.pie(wc.head(8), names='Team', values='Wins', title='🍰 Win Share')))
            
        if 'Season' in dff.columns and 'Winner' in dff.columns:
            figs_to_show.append(make_fig_div(px.scatter(dff, x='Season', y='Winner', title='📅 Timeline', height=400)))
            
        if 'Season' in dff.columns:
            season_counts = dff['Season'].value_counts().sort_index().reset_index()
            season_counts.columns = ['Season', 'Matches']
            figs_to_show.append(make_fig_div(px.bar(season_counts, x='Season', y='Matches', title='📈 Matches/Season')))

    # Data Table
    table = dash_table.DataTable(data=dff.head(100).to_dict('records'), columns=[{'name': c, 'id': c} for c in dff.columns[:11]], 
                                 style_table={'overflowX': 'auto'}, style_header={'backgroundColor': COLORS['primary'], 'color': 'white', 'fontWeight': 'bold'},
                                 style_cell={'textAlign': 'left', 'padding': '12px'}, style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#f8fafc'}])

    return stat_cards, figs_to_show, table, filter_options, selected_entity, min_val, status_msg

if __name__ == '__main__':
    app.run(debug=True)