from crewai.tools import tool
from crewai import Agent,Task,Process,Crew
import pandas as pd
import streamlit as st


###TOOLS
@tool("get weather data")
def get_weather_data(city: str):
    """
    This tool retrieves weather data for the specified city from a CSV file.
    """
    df = pd.read_csv("weather_data.csv")
    city_data = df[df['city'].str.lower() == city.lower()]
    if city_data.empty:
        return "No weather data found"
    return city_data.to_string(index=False)

@tool("get aqi data")
def get_aqi_data(city:str):
    """
    This tool retrieves AQI (Air Quality Index) data for the specified city from a CSV file.
    """
    df1 = pd.read_csv('aqi_data.csv')
    city_data1 = df1[df1['city'].str.lower() == city.lower()]
    if city_data1.empty:
        return "No AQI data found"
    return city_data1.to_string(index=False)

##AGENTS

#create an agent for getting weather data
weather_agent = Agent(
    llm="ollama/mistral",
    role="weather researcher",
    goal="perform in depth research on weather data",
    backstory="An junior weather researcher with a knack for gathering relevant, basic information about the weather of a given city.",
    tools=[get_weather_data],
    verbose=True,
    allow_delegation=False
)

aqi_agent = Agent(
    llm="ollama/mistral",
    role="aqi researcher",
    goal="perform in depth research on aqi data",
    backstory="An junior aqi researcher with a knack for gathering relevant, basic information about the aqi of a given city.",
    tools=[get_aqi_data],
    verbose=True,
    allow_delegation=False
)

both_agent = Agent(
    llm="ollama/mistral",
    role="weather and aqi researcher",
    goal="perform in depth research on weather and aqi data",
    backstory="An junior weather and aqi researcher with a knack for gathering relevant, basic information about the weather and aqi of a given city.",
    tools=[get_weather_data, get_aqi_data],
    verbose=True,
    allow_delegation=False
)

###TASKS

#get all the basic information about the weather
collect_weather_info = Task(
   description= """ 
This task will get fetch the latest information on weather data.
Conduct a thorough analysis of the weather data, tailored to the user's query and expertise level.
1.Use the get_weather_data tool as needed, based on the query's focus. E.g. If the query is about the weather of a city, then aqi info need not be present.
2. If the query is about the aqi of a city, then weather info need not be present.
3. If the query is about both weather and aqi of a city, then return both weather and aqi data.
In output it should include:
1.city name
2.AQI
3.main pollutant
4.health risk
User query: {query}.
""",
expected_output="A consise analysis of weather quality for the specified city as per specified response format only.Not your thought or anything else",
agent=weather_agent,
dependencies=[],
context=[]
)

perform_analysis = Task(
    description="""
This task will get fetch the latest information on aqi data.
Conduct a thorough analysis of the aqi data, tailored to the user's query and expertise level.
1.Use the get_weather_data and get_aqi_data tools as needed, based on the query's focus. E.g. If the query is about the weather of a city, then aqi info need not be present.
2. If the query is about the aqi of a city, then weather info need not be present.
3. If the query is about both weather and aqi of a city, then return both weather and aqi data.
In output it should include:
1.city name
2.AQI
3.main pollutant
4.health risk
User query: {query}.
""",
expected_output="A consise analysis of air quality for the specified city as per specified response format only.Not your thought or anything else",
    agent=aqi_agent,
    dependencies=[collect_weather_info],
    context=[collect_weather_info]
)

routing = Task(
    description = """
This task will route the user query to the appropriate agent based on the query.
Based on the users query determine if query is about:
1.weather
2.aqi
3.both weather and aqi
If the query is about weather, return the weather data.
If the query is about aqi, return the aqi data.
If the query is about both weather and aqi, return the weather data and aqi data.
In output it should include:
1.city name
2.AQI
3.main pollutant
4.health risk
User query: {query}.
""",
    expected_output="One word: 'weather' or 'aqi' or 'both'",
    agent=both_agent,
    dependencies=[],
    context=[]
)

###CREW
# create a crew
# crew = Crew(
#     agents=[weather_agent, aqi_agent],
#     tasks=[collect_weather_info, perform_analysis],
#     process=Process.sequential
# )




st.header("Weather Assistant")
st.write("This app helps you to analyze weather data")
question = st.chat_input("ask me anything about stocks")
if question:
    st.chat_message("user").markdown(question)
    with st.spinner("Analyzing..."):
        crew = Crew(
            agents=[weather_agent, aqi_agent, both_agent],
            tasks=[routing, collect_weather_info, perform_analysis],
            process=Process.sequential
        )
        #get the response from routing task
        result = crew.kickoff({"query": question})

        if result == "weather":
            agents= [weather_agent]
            tasks = [collect_weather_info]
        elif result == "aqi":
            agents = [aqi_agent]
            tasks = [perform_analysis]
        else:
            agents = [both_agent]
            tasks = [routing]

        crew = Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential
        )
        #run the crew
        response = crew.kickoff({"query":question})
    st.chat_message("ai").markdown(response)