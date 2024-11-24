import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats


MAIN_COLOR =  "aggrnyl"
PAPER_BG_COLOR = "#2a417d"
PLOT_BG_COLOR = "#2a417d"
FONT_COLOR = "white"
FONT_ACCENT_COLOR = "white"
FONT_COLORBAR = dict(color=FONT_COLOR, size=14, family="Arial", weight="bold")
FONT_TITLE = dict(
    family="Arial",
    size=18,
    color=FONT_COLOR,
)
FONT_TITLE_LITTLE = dict(
    family="Arial",
    size=16,
    color=FONT_COLOR,
)
FONT_LABEL_SIZE = 16,
FONT_LABEL_FAMILY ="Georgia",

def prepare_data(df, group):
    sector_data = df.groupby(group).agg(
        salary=("salary", "mean"),
        job_count=(group, "count")
    ).reset_index()

    total_jobs = sector_data[f"job_count"].sum()

    sector_data[f"{group}_percentage"] = (sector_data["job_count"] / total_jobs) * 100

    return sector_data

plt.switch_backend("Agg")

def salary_boxplot(df):
    df_non_remote = df[df["city"] != "Remote"]
    df_remote = df[df["city"] == "Remote"]

    box_trace_non_remote = go.Box(
        y=df_non_remote["salary"],
        x=["In-Place"] * len(df_non_remote),
        name="In-Place",
        marker_color="rgba(112, 198, 116, 0.5)",
        boxmean="sd",
        line=dict(color="rgba(112, 198, 116, 0.5)", width=3),
        fillcolor="rgba(112, 198, 116, 0.15)",
        whiskerwidth=0.5,
        boxpoints=False  # Remove individual data points (outliers)
    )

    box_trace_remote = go.Box(
        y=df_remote["salary"],
        x=["Remote"] * len(df_remote),
        name="Remote",
        marker_color="rgba(31,119,180,0.5)",
        boxmean="sd",
        line=dict(color="#edef5d", width=3),
        fillcolor="rgba(31,119,180,0.3)",
        whiskerwidth=0.5,
        boxpoints=False  # Remove individual data points (outliers)
    )

    fig = go.Figure(data=[box_trace_non_remote, box_trace_remote])

    fig.update_layout(
        width=None,
        height=None,
        margin={"r": 0, "t": 100, "l": 45, "b": 50},
        paper_bgcolor=PAPER_BG_COLOR,
        plot_bgcolor=PLOT_BG_COLOR,
        title="Salary Statistics by Type",
        title_font=FONT_TITLE,
        font=dict(size=12),
        xaxis=dict(
            showticklabels=True,
            showline=True,
            zeroline=False,
            zerolinecolor=FONT_COLOR,
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(color="white"),
            showline=True,
            zeroline=False,
            zerolinecolor=FONT_COLOR,
        ),
        hoverlabel=dict(
            font_size=16,
            font_family="Georgia",
            font_color="black",
        ),
        showlegend=True,
        legend=dict(
            font=dict(color=FONT_COLOR, size=14),
            orientation="v",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=0.95,
        ),
    )

    return fig

def avg_salary(df, group, city_filter='both'):
    df = df.rename(columns={"size": "company_size"})
    df = df[df[group] != "--"]

    if city_filter == 'remote':
        df = df[df['city'] == 'Remote']
    elif city_filter == 'in-place':
        df = df[df['city'] != 'Remote']
    elif city_filter == 'both':
        df = df
    else:
        raise ValueError("city_filter must be 'remote', 'in-place', or 'both'")

    group_data = df.groupby(group).agg(
        salary=("salary", "mean"),
        job_count=(group, "count")
    ).reset_index()

    total_jobs = group_data["job_count"].sum()
    group_data["group_percentage"] = (group_data["job_count"] / total_jobs) * 100
    group_data = group_data.sort_values(by="salary", ascending=True)

    group_data[group] = group_data[group].replace({
        "Energy, Mining & Utilities": "Energy/Mining",
        "Personal Consumer Services": "Personal svc",
        "Information Technology": "IT",
        "Human Resources & Staffing": "HR/Staffing",
        "Management & Consulting": "Consulting",
        "Media & Communication": "Media/Comm",
        "Telecommunications": "Telecomms",
        "Financial Services": "Financial",
        "Aerospace & Defense": "Aerospace",
        "Pharmaceutical & Biotechnology": "Pharma",
        "Transportation & Logistics": "Transport",
        "Construction, Repair & Maintenance Services": "Constr/Repair",
        "Retail & Wholesale": "Retail",
        "Nonprofit & NGO": "Nonprofil",
        "Government & Public Administration": "Government",
        "Arts, Entertainment & Recreation": "Arts",
        "Hotels & Travel Accommodation": "Hotels/Travel",
        "Restaurants & Food Service": "Food"
    })

    group_data['size'] = 15
    fig = px.scatter(
        group_data,
        x="salary",
        y=group,
        title=f"Salary by {group.capitalize()}<br>(Right = Higher Salary)",
        size="size",
        size_max=15,
        color="group_percentage",
        color_continuous_scale=MAIN_COLOR,
        labels={group: group.capitalize(), "group_percentage": "Percentage of jobs (%)"},
        custom_data=["group_percentage"]
    )

    fig.update_traces(
        hovertemplate=(
            f"<b>{group.capitalize()}:</b> %{{y}}<br>"
            "<b>Salary:</b> $%{x:,.0f}<br>"
            "<b>Job Percentage:</b> %{customdata[0]:.2f}%<extra></extra>"
        ),
    )

    fig.update_layout(
        height=None,
        width=None,
        paper_bgcolor=PAPER_BG_COLOR,
        plot_bgcolor=PLOT_BG_COLOR,
        margin=dict(l=0, r=0, t=60, b=10),
        title_font=FONT_TITLE,
        xaxis=dict(showgrid=False, title="", color=FONT_COLOR, showline=True, zerolinecolor=FONT_COLOR),
        yaxis=dict(showgrid=False, gridcolor=FONT_COLOR, title="", tickfont=dict(size=14, color=FONT_COLOR)),
        coloraxis_colorbar=dict(xanchor="left", title=dict(text="Job %", font=FONT_COLORBAR))
    )

    return fig

def geographical_distribution(df):
    # Group by state and calculate the average salary
    df_subset = df.groupby('state')['salary'].mean().reset_index()
    df_subset.columns = ['state', 'average_salary']

    # Format salary to 'k' with one decimal place
    df_subset["average_salary"] = df_subset["average_salary"] / 1000
    df_subset["average_salary"] = df_subset["average_salary"].round(1)

    # Create the choropleth map
    fig = px.choropleth(
        locations=df_subset["state"], 
        locationmode="USA-states", 
        color=df_subset["average_salary"], 
        scope="usa", 
        color_continuous_scale=MAIN_COLOR,
    )
    
    # Update hover template
    fig.update_traces(
        hovertemplate=(
            "<b>State:</b> %{location}<br>"
            "<b>Salary:</b> %{z:.1f}k USD<extra></extra>"
        )
    )
    
    fig.update_layout(
        width=None,
        height=None,
        margin={"r":0, "t":50, "l":0, "b":10},
        paper_bgcolor=PAPER_BG_COLOR,
        title_text="September 2024 USA Data Analyst Salaries",
        title_font=FONT_TITLE,
        coloraxis_colorbar=dict(
            title=dict(
                text="USD",
                font=FONT_COLORBAR,
            ),
        )
    )
    
    # Update the background of the map itself
    fig.update_geos(bgcolor=PLOT_BG_COLOR)
    
    return fig

def avg_salary_bar(df, group, city_filter="both"):
    df = df.rename(columns={"size": "company_size"})
    
    if city_filter == "remote":
        df = df[df["city"] == "Remote"]
    elif city_filter == "in-place":
        df = df[df["city"] != "Remote"]
    elif city_filter == "both":
        df = df
    else:
        raise ValueError("city_filter must be 'remote', 'in-place', or 'both'")

    df = df[~df[group].isin(["--", "Unknown", "Unknown / Non-Applicable"])]

    group_data = df.groupby(group).agg(
        salary=("salary", lambda x: x.mean() / 1000),  # Divide by 1000 to get salary in 'k'
        job_count=(group, "count")
    ).reset_index()

    total_jobs = group_data["job_count"].sum()
    group_data["group_percentage"] = (group_data["job_count"] / total_jobs) * 100
    
    if group == "size_str":
        group_data[group] = group_data[group].replace({
            "1 to 50 Employees": "1 to 50",
            "51 to 200 Employees": "51 to 200",
            "201 to 500 Employees": "201 to 500",
            "501 to 1000 Employees": "501 to 1k",
            "1001 to 5000 Employees": "1k to 5k",
            "5001 to 10000 Employees": "5k to 10k",
            "10000+ Employees": "10k+",
        })
        size_order = [
            "1 to 50",
            "51 to 200",
            "201 to 500",
            "501 to 1k",
            "1k to 5k",
            "5k to 10k",
            "10k+"
        ]
        group_data[group] = pd.Categorical(group_data[group], categories=size_order, ordered=True)

    elif group == "revenue_str":
        group_data[group] = group_data[group].replace({
            "Less than $1 million (USD)": "< 1M",
            "$1 to $5 million (USD)": "1 to 5M",
            "$5 to $25 million (USD)": "5 to 25M",
            "$25 to $100 million (USD)": "25 to 100M",
            "$100 to $500 million (USD)": "100 to 500M",
            "$500 million to $1 billion (USD)": "500M to 1B",
            "$1 to $5 billion (USD)": "1 to 5B",
            "$5 to $10 billion (USD)": "5 to 10B",
            "$10+ billion (USD)": "10B+"
        })
        revenue_order = [
            "< 1M", "1 to 5M", "5 to 25M", "25 to 100M", 
            "100 to 500M", "500M to 1B", "1 to 5B", "5 to 10B", "10B+"
        ]
        group_data[group] = pd.Categorical(group_data[group], categories=revenue_order, ordered=True)

    elif group == "rating":
        bins = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.1]
        labels = ["2.0 to 2.4", "2.5 to 2.9", "3.0 to 3.4", "3.5 to 3.9", "4.0 to 4.4", "4.5 to 4.9", "5.0"]
        df[group] = pd.cut(df[group], bins=bins, labels=labels, right=False, include_lowest=True)

        group_data = df.groupby(group).agg(
            salary=("salary", lambda x: x.mean() / 1000),  # Divide by 1000 to get salary in 'k'
            job_count=(group, "count")
        ).reset_index()

        total_jobs = group_data["job_count"].sum()
        group_data["group_percentage"] = (group_data["job_count"] / total_jobs) * 100

    fig = px.bar(
        group_data, 
        x=group, 
        y="salary", 
        color="group_percentage", 
        color_continuous_scale=MAIN_COLOR, 
        title=f"Salary by {group.replace('_str', '').capitalize()}",
    )

    fig.update_layout(
        height=None,
        width=None,
        paper_bgcolor=PAPER_BG_COLOR,
        plot_bgcolor=PLOT_BG_COLOR,
        margin=dict(l=0, r=0, t=50, b=0),
        title_font=FONT_TITLE_LITTLE,
        coloraxis_colorbar=dict(
            xanchor="left",
            thickness=10,
            len=1.2,
            title=dict(
                text="%", 
                font=FONT_COLORBAR,
            ),
        ),
        xaxis=dict(showgrid=False, title="", tickfont=dict(color=FONT_COLOR)),
        yaxis=dict(
            showgrid=False, 
            title="", 
            tickfont=dict(color=FONT_COLOR),
            tickprefix="$",
            ticksuffix="k",
            range=[60, 120]
        ),
    )
    
    fig.update_traces(
        hoverlabel=dict(
            font_size=16,
            font_family="Georgia",
        ),
        hovertemplate=(
            f"<b>{group.replace('_str', '').capitalize()}:</b> %{{x}}<br>"  # Group/category name
            "<b>Salary:</b> $%{y:.1f}k<br>"  # Display salary in 'k' (thousands)
            "<b>Percentage:</b> %{customdata[0]:.1f}%<extra></extra>"  # Percentage with 1 decimal place and %
        ),
        customdata=group_data[["group_percentage"]]  # Include percentage data for the hover
    )

    return fig

def salary_density(df):
    NO_RM_SCALE = 1
    RM_SCALE = 50

    # Filter salaries for non-remote jobs and remote jobs
    df_non_remote = df[(df['salary'] >= 20000) & (df['city'] != 'Remote')]
    df_remote = df[(df['salary'] >= 20000) & (df['city'] == 'Remote')]

    # Salary data
    sal_non_remote = df_non_remote['salary']
    sal_remote = df_remote['salary']

    # Number of jobs
    jobs_non_remote = len(sal_non_remote)
    jobs_remote = len(sal_remote)

    # Kernel density estimates (KDE)
    kde_non_remote = stats.gaussian_kde(sal_non_remote, bw_method=0.5)
    kde_remote = stats.gaussian_kde(sal_remote, bw_method=0.5)

    # Salary range
    sal_range_non_remote = np.linspace(sal_non_remote.min(), sal_non_remote.max(), 1000)
    sal_range_remote = np.linspace(sal_remote.min(), sal_remote.max(), 1000)

    # KDE values scaled by the number of jobs
    kde_non_remote_vals = kde_non_remote(sal_range_non_remote) * jobs_non_remote * NO_RM_SCALE
    kde_remote_vals = kde_remote(sal_range_remote) * jobs_remote * RM_SCALE

    # Create the figure
    fig = go.Figure()

    # Add KDE plot for non-remote jobs
    fig.add_trace(go.Scatter(
        x=sal_range_non_remote,
        y=kde_non_remote_vals,
        fill='tozeroy',  # Fill the area under the curve
        mode='lines',
        line=dict(color='blue'),
        name='Non-Remote Jobs'
    ))

    # Add KDE plot for remote jobs
    fig.add_trace(go.Scatter(
        x=sal_range_remote,
        y=kde_remote_vals,
        fill='tozeroy',  # Fill the area under the curve
        mode='lines',
        line=dict(color='red'),
        name='Remote Jobs'
    ))

    # Update layout
    fig.update_layout(
        title="Salary Distribution: Non-Remote vs Remote Jobs",
        xaxis_title="Salary (USD)",
        yaxis_title="Density (Higher = More jobs)",
        title_font_size=18,
        title_font_family='Arial',
        xaxis=dict(tickfont=dict(size=12), color=FONT_COLOR),
        plot_bgcolor=PLOT_BG_COLOR,
        paper_bgcolor=PAPER_BG_COLOR,
        height=None,
        width=None,
    )

    # Remove Y-axis ticks but keep the label
    fig.update_yaxes(showticklabels=False)

    # Add gridlines
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')

    return fig

def calculate_salary_stats(df):
    # Filter remote and non-remote jobs
    df_non_remote = df[df['city'] != 'Remote']
    df_remote = df[df['city'] == 'Remote']
    
    # Average salary
    avg_salary_non_remote = df_non_remote['salary'].mean()
    avg_salary_remote = df_remote['salary'].mean()
    
    # Job counts
    total_jobs = len(df)
    jobs_non_remote = len(df_non_remote)
    jobs_remote = len(df_remote)
    
    # Percentage of jobs
    perc_jobs_non_remote = (jobs_non_remote / total_jobs) * 100 if total_jobs > 0 else 0
    perc_jobs_remote = (jobs_remote / total_jobs) * 100 if total_jobs > 0 else 0
    
    return avg_salary_non_remote, avg_salary_remote, perc_jobs_non_remote, perc_jobs_remote
