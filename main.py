import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt

def load_data():
    """
    Load the datasets into pandas DataFrames.
    """
    # Load the CSV files into DataFrames
    df_countries_cities = pd.read_csv('metro_countries_cities.csv')
    df_countries_total = pd.read_csv('metro_countries_total.csv')
    
    return df_countries_cities, df_countries_total

def analyze_data(df_countries_cities, df_countries_total):
    """
    Use SQL to join, aggregate, and derive insights from the data.
    """
    # Create a temporary database in memory
    conn = sqlite3.connect(':memory:')
    
    # Write the dataframes to SQL tables
    df_countries_cities.to_sql('countries_cities', conn, index=False)
    df_countries_total.to_sql('countries_total', conn, index=False)
    
    # Define the SQL query
    query = """
        SELECT 
            ct.country,
            MAX(cc.year_last_expansion) AS latest_expansion_year,
            SUM(ct.length) AS total_length_km,
            SUM(ct.lines) AS total_lines,
            SUM(ct.stations) AS total_stations,
            SUM(ct.annual_ridership_mill) AS total_annual_ridership_mill,
            AVG(ct.length/ct.systems) AS avg_length_per_system,
            AVG(ct.lines/ct.systems) AS avg_lines_per_system,
            AVG(ct.stations/ct.systems) AS avg_stations_per_system,
            AVG(ct.annual_ridership_mill/ct.systems) AS avg_ridership_per_system
        FROM 
            countries_cities cc
        JOIN 
            countries_total ct
        ON 
            cc.country = ct.country
        GROUP BY 
            ct.country
        ORDER BY 
            latest_expansion_year DESC, total_length_km DESC
        LIMIT 10
    """
    
    # Execute the query and fetch the results
    result = pd.read_sql_query(query, conn)
    
    return result

def visualize_data(result):
    """
    Generate the multi-faceted visualization to visually represent the insights.
    """
    # Set the style
    sns.set_style("whitegrid")
    
    # Create a figure with subplots
    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(18, 14))
    
    # Bar chart: Latest expansion vs Total Metro Length
    sns.barplot(x='latest_expansion_year', y='total_length_km', hue='country', data=result, ax=ax[0, 0], dodge=False)
    ax[0, 0].set_title('Latest Expansion Year vs Total Metro Length')
    ax[0, 0].set_xlabel('Latest Expansion Year')
    ax[0, 0].set_ylabel('Total Metro Length (km)')
    ax[0, 0].legend(loc='upper left')
    
    # Scatter plot: Avg Length/System vs Avg Ridership/System
    sns.scatterplot(x='avg_length_per_system', y='avg_ridership_per_system', hue='country', data=result, ax=ax[0, 1], s=100)
    ax[0, 1].set_title('Average Length per System vs Average Ridership per System')
    ax[0, 1].set_xlabel('Average Length per System (km)')
    ax[0, 1].set_ylabel('Average Ridership per System (in billions)')
    ax[0, 1].legend(loc='upper right')
    
    # Pie chart: Distribution of Latest Year of Expansion
    expansion_counts = result['latest_expansion_year'].value_counts()
    ax[1, 0].pie(expansion_counts, labels=expansion_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"))
    ax[1, 0].set_title('Distribution of Latest Year of Expansion')
    
    # Remove empty plot
    fig.delaxes(ax[1, 1])
    
    # Adjust layout and display the plot
    plt.tight_layout()
    plt.show()

# Main execution flow
df_countries_cities, df_countries_total = load_data()
result = analyze_data(df_countries_cities, df_countries_total)
visualize_data(result)
