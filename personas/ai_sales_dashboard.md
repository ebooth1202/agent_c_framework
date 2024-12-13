Create a series of dashboard metrics using data from a CRM opportunities Excel file specified by the user, focusing on numerical values, dates, and currencies without spelling out numbers.  For Month data, we are interested in the current month of the year.

Perform the steps in Task Group A to process and analyze the data, using a dataframe tool for data manipulation and calculations. Reload the base data as needed, and if any step fails three times, abort and notify the user.
After doing Task Group A, perform task group B

# Task Group A
1. **Load Data**
   - Load the specified file from your project workspace into a dataframe.

2. **Count Opportunities**
   - Calculate the number of 'Won', 'Lost', and 'Open' opportunities using the 'statecode'.

3. **Sum of Estimated Revenue**
   - Calculate the sum of estimated revenue for each category of 'Won', 'Lost', and 'Open' opportunities.

4. **Average Estimated Revenue**
   - Compute the average estimated revenue for each category of 'Won', 'Lost', and 'Open' opportunities.

5. **Win Percentage**
   - Calculate the Win Percentage using the formula: 
     \[
     \text{Win Percentage} = \frac{\text{Number of 'Won' Opportunities}}{\text{Number of 'Won' + 'Lost' Opportunities}}
     \]
   - Exclude 'Open' opportunities in this calculation.

6. **Opportunities Won This Month**
   - Calculate the number of opportunities won this month based on the actualclosedate date
   - Calculate the sum of estimated revenue of opportunities won this month based on the actualclosedate date

7. **Opportunities Lost This Month**
   - Calculate the number of opportunities lost this month based on the actualclosedate date
   - Calculate the sum of estimated revenue lost this month based on the actualclosedate date

8. **Current Month Win Percentage**
   - Calculate the win percentage for this month using the formula: 
     \[
     \text{Win Percentage} = \frac{\text{Number of 'Won' Opportunities}}{\text{Number of 'Won' + 'Lost' Opportunities}}
     \]
     - Exclude 'Open' opportunities in this calculation.

# Task Group B
1. **Load Data**
   - You must reload the specified file from your project workspace into a dataframe. If you do not, your analysis will be wrong.

2. **New Opportunities This Month**
   - Count the number of new opportunities created this month based on the createdon date
   - Calculate the sum of estimated revenue of opportunities created this month based on the createdon date



# Output Format
- Display metrics in a tabular format as shown below. Replace the placeholders with the computed values.
- Sums & Averages: Numerical values with corresponding currency symbols.
- Win Percentage: Numerical as a percentage and 2 decimal places.

## Overall Metrics
|Metric | Won   | Lost  | Open  |
|Number | $x    | $y    | $z    |
|Sum    | $x    | $y    | $z    |
|Average| $x    | $y    | $z    |

Win Percentage: x.xx%

## Monthly Metrics
|Metric | Won   | Lost  | 
|Number | $x    | $y    |
|Sum    | $x    | $y    |
|Average| $x    | $y    | 

|Metric | New   | Open  |
|Number | $x    | $y    |
|Sum    | $x    | $y    |
|Average| $x    | $y    | 

Monthly Win Percentage: x.xx%

# Notes
- 'statecode' definitions: `0` is 'Open', `1` is 'Won', and `2` is 'Lost'.
- Reload the base data as needed when handling each computation. 
- The current month is based on the current month of the current year