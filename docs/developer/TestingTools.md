# Things to test
This is a reference for testing the tools in the assistant.  It is a work in progress and will be updated as new tools are added.
Currently this cost ~$25 to execute a full test

## Agent as a Tool
- Enable Tools: `AgentTools`
- Persona: 'Default'
- Requirements: None
- Prompt: Use your agent as a tool equipped with weathertools to find the weather for Columbus, Ohio
- Response:
  - assistant used simplified_agent-initialize_agent
  - assistant used simplified_agent-perform_task
  - ```text
    The current weather in Columbus, Ohio is 70 degrees Fahrenheit and overcast. It feels like 70 degrees Fahrenheit.
    Here's the forecast for the next few days:
    - Today, September 26, 2024: High of 75 degrees, Low of 67 degrees
    - Tomorrow, September 27, 2024: High of 70 degrees, Low of 66 degrees
    - September 28, 2024: High of 68 degrees, Low of 64 degrees

## Dall-E Tool
- Enable Tools: `DallETools`
- Persona: 'Default'
- Requirements: Folder set in .env
- Prompt: Create an image of a tornado in farmland, mid afternoon, with rolling hills of corn
- Response:
  - assistant is using: dalle-create_image
  - image created and stored in your .env folder location and displayed in gradio client

## FeedbackTools
- Enable Tools: `FeedbackTools`
- Persona: 'Default'
- Requirements: None
- Prompt: Give me the latest information stored from the feedbacktools
- Response:
  - assistant used feedback-get_user_feedback
  - If feedback has been collected, will see it, otherwise will be told there isn't any feedback

## GoogleTrendsTools
- Enable Tools: `GoogleSearchTrends`
- Persona: 'Default'
- Requirements: None
- Prompt: What is the top search trend on google?
- Response:
  - assistant used googletrends-get_google_trending_searches
  - Top 10-20 search keywords is displayed

## HackerNewsSearch
- Enable Tools: `HackerNews`
- Persona: 'Default'
- Requirements: None
- Prompt: What is the top news story?
- Response:
  - assistant used hacker_news-get_top_stories
  - Top topic is displayed

## MermaidChartTools
- Enable Tools: `MermaidTools`
- Persona: 'Default'
- Requirements: None
- Prompt: Create a flow diagram for making a peanut butter and jelly sandwich
- Response:
  - From mermaid_chart
  - assistant used mermaidchart-render_graph
  - Mermaid visual is displayed as well as the code used to generate it

## NewsTools
- Enable Tools: `NewsTools`
- Persona: 'Default'
- Requirements: None
- Prompt: What is the top news story?
- Response:
  - assistant used newsapiorg-get_top_headlines
  - Answer is displayed


## O1AgentAsTool
- Enable Tools: `o1AgentTools`
- Persona: 'Default'
- Requirements: Need an o1 agent key in the local environment .env file.  See tool .md for details
- Prompt: Use your O1AgentTool and ask it to create a strategy for a new consulting services around AI Governance launch
- Response:
  - assistant used o1_chat-chat
  - Answer is displayed
- Notes: Warning, this tool is long running


## OneShotTool


## RSSTools
- Enable Tools: `RSSTools`
- Persona: 'Default'
- Requirements: None
- Prompt: Get me the RSS feed from Centric Consulting
- Response:
  - assistant used rss-fetch_rss_feed
  - Latest blog posts are displayed from centric

## TavilyTools
- Enable Tools: `TavilyTools`
- Persona: 'Default'
- Requirements: None
- Prompt: Search Tavily for information on AI Agents
- Response:
  - assistant used tavily-search_tavily
  - Information is displayed from Tavily

## UserBioTools
- Enable Tools: `UserBioTools`
- Persona: 'Default'
- Requirements: None
- Prompt: Update my name to John
- Response:
  - assistant used userbio-update_name
  - Name updated

## WeatherTools
- Enable Tools: `WeatherTools`
- Persona: 'Default'
- Requirements: None
- Prompt: What is the weather in Columbus, Ohio?
- Response:
  - assistant used weather-get_current_weather
  - Weather is displayed
 
## WebTools
- Enable Tools: `WebTools`
- Persona: 'Default'
- Requirements: None
- Prompt: Use webtools and summarize https://centricconsulting.com/news-and-events/insights-from-joseph-ours-navigating-artificial-intelligence/
- Response:
  - assistant used web-fetch_webpage
  - Summary is displayed 

## WikipediaSearch
- Enable Tools: `WikipediaSearch`
- Persona: 'Default'
- Requirements: None
- Prompt: Get information from wikipedia on Miss Meyers
- Response:
  - assistant used wikipedia-search_wiki
  - Summary is displayed or a list of search terms matching miss meyers is displayed

## YouTubeTools
- Enable Tools: `YouTubeTools`
- Persona: 'Default'
- Requirements: None
- Prompt: Summarize the transcript from youtube video at https://www.youtube.com/watch?v=blCcoAuDnRo&t=2s
- Response:
  - assistant used youtube-retrieve_and_save_transcript
  - Summary is displayed


# Cascade Testing with Dataframe Tools
## Cascade # 1 - Dataframe, DataVisualization, Database, Dynamics
### 1) Dataframe Tools
- Enable Tools: `DataframeTools`
- Persona: 'Default'
- Requirements: Have the `golden_list_opps.xlsx` file available in project root with basic columns/rows
- Prompt: Load the excel file `golden_list_opps.xlsx` in you project root into a dataframe and display the first 5 rows
- Response:
  - assistant used dataframe-load_data, dataframe-display_records
  - First 5 records displayed
  
### 2) DataVisualizationTools
- Enable Tools: `Dataframe`, `DataVisualizationTools`
- Persona: 'Default'
- Requirements: Have an excel file available in project root with basic columns/rows - preferablly golden opportu
- Prompt: Load the excel file `golden_list_opps.xlsx` in you project root into a dataframe and create a piechart of the sum of estimated revenue by step
- Response:
  - assistant used dataframe-load_data, dataframe-group_by_and_agg, dataframe-store_dataframe_to_cache
  - assistant used data_visualization-create_pie_chart
  - Valid piechart is displayed

### 3) Database tools
- Enable Tools: `DataframeTools`, `DatabaseTools`
- Persona: 'Default'
- Requirements: Requires Chinook.sqlite database setup in data_demo folder
- Prompt: Can you tell me what tables exists in the database?
- Response:
  - assistant used database_query-get_tables
  - List of tables

### 4) Dynamics Tools  
- Enable Tools: `DataframeTools`, `DynamicsTools`
- Persona: 'Default'
- Requirements: Requires Chinook.sqlite database setup in data_demo folder
- Prompt: Can you tell me what tables exists in the database?
- Response:
  - assistant used database_query-get_tables
  - List of tables

### 5) Dynamics
- Enable Tools: `DataframeTools`, `DynamicsTools`
- Persona: 'Default'
- Requirements: Must have tasks in Dynamics
- Prompt: Can you get me all my open tasks in dyanmics?
- Response:
  - assistant used dynamics_crm-dynamics_user_id
  - assistant used dynamics_crm-get_entities
  - List of tasks is displayed

## Cascade #2 - Salesforce, LinkedIn, SerpAPI
### LinkedInTools
- Enable Tools: `LinkedInTools`
- Persona: 'Default'
- Requirements: Must have logged into LinkedIN in the gradio browser prior to running.  Must use valid profile url name
- Prompt: Get me key profile information from linkedin for josephours
- Response:
  - assistant used linkedin-get_profile
  - LinkedIn profile information is displayed

### SerpAPITools
- Enable Tools: `SerpAPITools`
- Persona: 'Default'
- Requirements: None
- Prompt: Search for Centric's Address
- Response:
  - assistant used google_search-get_search_results
  - Information returned

### SalesforceTools
- Enable Tools: `LinkedInTools`, `SerpAPITools`, `SalesforceTools`
- Persona: 'salesforce'
- Requirements: Salesforce Dev Environment
- Prompt: Create a contact for Joseph Ours by using information from his josephours linkedin profile. Create an account record for his employer.  Use Google to look up the employer address to include in the record. Also add an opportunity implementing AI Agents with Salesforce expected to close in 2 weeks for his company. 
- Response:
  - assistant used linkedin-get_profile
  - assistant used google_search-get_search_results
  - assistant used salesforce-create_record, salesforce-create_record, salesforce-create_record
  - Records are created in salesforce instance using data from linkedin and google search



## Cascade #3 - Stock Analysis

### SeekingAlphaTools
- Enable Tools: `SeekingAlphaTools`, `SECTools`
- Persona: 'Default'
- Requirements: None
- Prompt: What are the top news stories?
- Response:
  - assistant used seekingalpha-get_topk_trending_news
  - Top 5 headlines displayed

### FAISSVectorStore and SECTool
- Enable Tools: `FAISSVectorStore`, `SECTools`
- Persona: 'stock_analyzer'
- Requirements: None
- Prompt: Download the latest NVDA 10-k Report
- Response:
  - assistant used secfilings-download_filing
  - I have successfully downloaded the latest 10-K report for NVIDIA (NVDA). How would you like to proceed with the analysis?

### Query FAISSVectorStore
- Enable Tools: `FAISSVectorStore`
- Persona: 'stock_analyzer'
- Requirements: None
- Prompt: Search the sec_filings index for financial risk for NVDA?
- Response:
  - assistant used secfilings-query_filing OR
  - I have successfully downloaded the latest 10-K report for NVIDIA (NVDA). How would you like to proceed with the analysis?


### Grand Stock Analysis
- Enable Tools: `FAISSVectorStore`, `SECTools`, `StockAnalysisTools`, `SeekingAlphaTools`
- Persona: 'stock_analyzer'
- Requirements: Salesforce Dev Environment
- Prompt: Can you analyze the Stock for Nvidia?
- Response:
  - assistant used stockanalysis-perform_stock_analysis
  - It is important that the analysis contains the following:
    - Key metrics - these are tool calculated (Beta/Dividend) (uses yfinance via stockanalysis tool)
    - SEC Filings - Must mention what is in the 10-k report (implicitly uses FAISSVectorStore, SECTools)
    - News - Must mention the top news stories (uses SeekingAlphaTools)