import dash
from dash import dcc
from dash import html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import pandas as pd
import graphics


# Load your salary data (assuming it's a DataFrame called salary_db)
salary_db = pd.read_sql_table("clean_df", "sqlite:///jobs.db")

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

avg_salary_non_remote, avg_salary_remote, perc_jobs_non_remote, perc_jobs_remote = graphics.calculate_salary_stats(salary_db)

app.layout = html.Div([

    html.Div([
        html.H1("Salary Dashboard: Data Analysis From Glassdoor Perspective")
    ], className='div-title'),

    # Create sections for different graphs
    html.Div([

        # Section-Left
        html.Div([
            # Numbers grid
            html.Div([
                # Non-remote average salary
                html.Div([
                    html.Div([
                        html.Span("Average Salary", className='salary-line'),
                        html.Span("(In-Place)", className='salary-line')  # Class to control spacing
                    ], className='salary-label'),
                    html.Div(f"${avg_salary_non_remote / 1000:.1f}k", className='big-number'),
                ], className='section section-numbers numbers-1'),

                # Remote average salary
                html.Div([
                    html.Div([
                        html.Span("Average Salary", className='salary-line'),
                        html.Span("(Remote)", className='salary-line')  # Class to control spacing
                    ], className='salary-label'),
                    html.Div(f"${avg_salary_remote / 1000:.1f}k", className='big-number'),
                ], className='section section-numbers numbers-2'),
            ], className='numbers-grid'),

            # Salary by State Boxplot
            html.Div([
                html.H2("Salary by State"),
                dcc.Graph(figure=graphics.salary_boxplot(salary_db), config={'responsive': True}, className="titled-graph graph"),
            ], className='graph-container boxplot'),
        ], className="section-left section-side"),

        # Section-Center
        html.Div([

            # Geographical Distribution Map
            html.Div([
                dcc.Graph(figure=graphics.geographical_distribution(salary_db), config={'responsive': False}, className="untitled-graph graph"),
            ], className='graph-container map'),

            # Filtering buttons
            html.Div([
                html.Button("Both", id="both-button", n_clicks=0, className="filter-button active"),
                html.Button("Remote", id="remote-button", n_clicks=0, className="filter-button"),
                html.Button("In-Place", id="inplace-button", n_clicks=0, className="filter-button")
            ], className="button-container"),

            html.Div([

                # Salary by Company Size Bar Plot
                html.Div([
                    dcc.Graph(id='company-size-bar', config={'responsive': True}, className="untitled-graph graph"),
                ], className='graph-container bar'),

                # Salary by Revenue Bar Plot
                html.Div([
                    dcc.Graph(id='revenue-bar', config={'responsive': True}, className="untitled-graph graph"),
                ], className='graph-container bar'),

                # Salary by Rating Bar Plot
                html.Div([
                    dcc.Graph(id='rating-bar', config={'responsive': True}, className="untitled-graph graph"),
                ], className='graph-container bar'),

            ], className="section-bars"),
            
        ], className="section-center"),
        
        # Section-Right
        html.Div([

            # Average Salary by Sector
            html.Div([
                html.H2("What sector is paying more?"),
                dcc.Graph(id='avg-salary-graph', config={'responsive': True}, className="titled-graph graph"),
            ], className='graph-container dotplot'),

        ], className="section-right section-side"),

    ], className='dashboard-grid'),

], className="div-main")


@app.callback(
    [Output("both-button", "className"),
     Output("remote-button", "className"),
     Output("inplace-button", "className"),
     Output("avg-salary-graph", "figure"),
     Output("company-size-bar", "figure"),
     Output("revenue-bar", "figure"),
     Output("rating-bar", "figure")],
    [Input("both-button", "n_clicks"),
     Input("remote-button", "n_clicks"),
     Input("inplace-button", "n_clicks")]
)
def update_filter_and_graphs(both_clicks, remote_clicks, inplace_clicks):
    # Determine which button was clicked
    ctx = dash.callback_context
    if not ctx.triggered:
        selected_filter = "both"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == "both-button":
            selected_filter = "both"
        elif button_id == "remote-button":
            selected_filter = "remote"
        elif button_id == "inplace-button":
            selected_filter = "in-place"

    # Apply the filter to the data
    if selected_filter == "remote":
        filtered_data = salary_db[salary_db["city"] == "Remote"]
    elif selected_filter == "in-place":
        filtered_data = salary_db[salary_db["city"] != "Remote"]
    else:
        filtered_data = salary_db  # No filter, use the entire dataset
    
    # Safety check for empty or small datasets
    if filtered_data.empty:
        return (
            "filter-button active", "filter-button", "filter-button",  # Button classes
            go.Figure(),  # Empty figure for avg_salary_graph
            go.Figure(),  # Empty figure for company_size_bar
            go.Figure(),  # Empty figure for revenue_bar
            go.Figure()   # Empty figure for rating_bar
        )

    # Now generate the figures with the filtered data
    avg_salary_fig = graphics.avg_salary(filtered_data, "sector", city_filter=selected_filter)
    company_size_fig = graphics.avg_salary_bar(filtered_data, "size_str")
    revenue_fig = graphics.avg_salary_bar(filtered_data, "revenue_str")
    rating_fig = graphics.avg_salary_bar(filtered_data, "rating")

    # Determine button classes based on the selected filter
    if selected_filter == "both":
        return "filter-button active", "filter-button", "filter-button", avg_salary_fig, company_size_fig, revenue_fig, rating_fig
    elif selected_filter == "remote":
        return "filter-button", "filter-button active", "filter-button", avg_salary_fig, company_size_fig, revenue_fig, rating_fig
    elif selected_filter == "in-place":
        return "filter-button", "filter-button", "filter-button active", avg_salary_fig, company_size_fig, revenue_fig, rating_fig
# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)