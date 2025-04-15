# DataFrame Tool

## What This Tool Does

The DataFrame Tool empowers agents to work with tabular data, allowing them to manipulate, analyze, and transform datasets on your behalf. This tool leverages the powerful pandas library to handle structured data efficiently.

## Key Capabilities

With the DataFrame Tool, agents can:

- **Load data** from various sources including CSV files, Excel spreadsheets, JSON data, and databases
- **Clean and transform data** by handling missing values, removing duplicates, and reformatting columns
- **Filter and sort data** based on specific conditions or criteria
- **Compute statistics** such as means, medians, correlations, and aggregations
- **Join and merge datasets** from multiple sources
- **Reshape data** between wide and long formats
- **Extract insights** from complex datasets
- **Save and export data** to various formats

## Practical Use Cases

- **Business Intelligence**: Analyze sales data, customer metrics, or operational KPIs
- **Financial Analysis**: Process transaction data, perform portfolio analysis, or calculate financial metrics
- **Research**: Analyze experimental data, survey results, or observational studies
- **Data Preparation**: Clean and transform data for machine learning models or other analytical tools
- **Reporting**: Generate summaries and extract key information from large datasets

## Example Interactions

### Basic Data Analysis

**User**: "Load this CSV file and show me the average sales by region for Q1 2025."

**Agent**: *Loads the CSV, calculates regional averages, and presents a concise summary table with insights about the highest and lowest performing regions.*

### Data Transformation

**User**: "Take this customer data and create a new column that categorizes customers as 'High Value' if they spent over $1000 in the last month."

**Agent**: *Processes the data, adds the requested categorization column, and provides a summary of how many customers fall into each category.*

### Multi-step Analysis

**User**: "Import these two Excel files containing product inventory and sales data. Then find which products are selling well but have low inventory levels."

**Agent**: *Loads both files, joins the datasets on product ID, calculates inventory-to-sales ratios, and identifies products that need attention.*

## Configuration Requirements

This tool uses pandas and related Python libraries that are included in the Agent C environment. No external API keys or additional configuration is required.

## Important Considerations

### Data Preparation

For best results:
- Ensure data files are properly formatted
- Inform the agent about any special formatting, missing values, or data types
- Provide context about what the data represents

### Performance

Processing very large datasets (millions of rows) may take additional time. For extremely large datasets, consider asking the agent to work with a sample of the data first.

### Privacy and Security

Any data processed using this tool stays within your Agent C environment and is not transmitted to external services. However, be mindful of sharing sensitive information in your datasets.

### Persistence

DataFrames created during a session can be saved to files for future use. Otherwise, they exist only for the duration of your conversation with the agent.