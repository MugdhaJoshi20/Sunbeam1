import streamlit as st
import pandas as pd
import sqlite3
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

#create in-memory databse connection
connection= sqlite3.connect(':memory:')

#create a model
model=  ChatOllama(model="llama3")

#template to create query
query_template = """You are sqlite3 eveloper,writing sqlite3 queries.
    Use the given schema and answer users question.
    Do NOT include any explanation, prefix like "Here is the query", or code block.
    Do NOT include anything except the raw SQL query.
    Question: {question}
    Schema: {schema}
    Query:

    Generate only query nothing else.
    """
#template to format result
result_template = """ You are database assistant.
given users question,generated query and results found, you need to format result accordingly.4


    Question: {question}
    Query: {query}
    results: {results}
    
    Print only fromatted results nothing else.
    """


    #extract the table name from the file name
table_name1="employee1" #file_name.split('.')[0]
    #extract the table name from the file name
table_name2="department1" #file_name.split('.')[0]
table_names = [table_name1, table_name2]
#get the table schema
cursor = connection.cursor()
#set streamlit layout
st.set_page_config(layout="wide")

st.header("chat with your csv files")

#get the csv file from user
upload_file1=st.file_uploader("upload your csv file1",type=["csv"])
upload_file2=st.file_uploader("upload your csv file2",type=["csv"])

st.header("Enter your question:")
#get the question from user
question = st.chat_input("Ask question about csv file")
if upload_file1 and upload_file2:
    file_name1 = upload_file1.name
    file_name2 = upload_file2.name

    #read csv file into dataframe
    df1 = pd.read_csv(upload_file1)
     #read csv file into dataframe
    df2 = pd.read_csv(upload_file2)

    #create the table and insert the data
    df1.to_sql(table_name1,connection,index=False,if_exists='replace')

    #create the table and insert the data
    df2.to_sql(table_name2,connection,index=False,if_exists='replace')

    #create column
    col1,col2=st.columns(2)

    with col1:
        st.subheader("CSV file contents")
        st.dataframe(df1)
    with col2:
        st.subheader("Csv File2 content")
        st.dataframe(df2)
def extract_schema_from_database():
    
    schema=""
    for table_name in ["employee1", "department1"]:
        print(f"Extracting schema for table:{table_name}")
        #get the table schema
        cursor.execute(f"PRAGMA table_info('{table_name}')")
        #fetch the schema
        result = cursor.fetchall()
        #format the schema(list of dictionaries)
        # schema = [{"column":info[1],"type":info[2]} for info in result]
        schema+=f"\nTable {table_name}:\n"
        for col in result:
             schema+=f" {col[1]} ({col[2]})\n"
        #close the cursor
    cursor.close()
    return schema.strip()
    # print(schema)
    
        # return schema

def generate_query(question):
    # print(f"table_name:{table_names}")
    schema_text =extract_schema_from_database()
    #create the prompt
    prompt_template = ChatPromptTemplate.from_template(template=query_template)
    prompt = prompt_template.invoke({
        "question":question,
        "schema":schema_text
    })

    #get the query from model
    response=model.invoke(prompt)

    #return query
    return response.content

def execute_query(query):
    #get the cursor
    cursor=connection.cursor()

    #execute the query
    cursor.execute(query)

    #get the result
    result=cursor.fetchall()
    print(result)

    #close the cursor
    cursor.close()

    return result

def format_result(question,query,results):
    #create the prompt
    prompt_template = ChatPromptTemplate.from_template(template=result_template)
    prompt = prompt_template.invoke({"question": question, "query": query, "results": results})
    

    #get the formatted result from model
    response = model.invoke(prompt)
    

    #return the formatted result
    return response.content

if question:
    #generate the query using model
            query=generate_query(question)
            print(query)
    

            #answer the user's question
            results = execute_query(query)
    
            #format the results
            formatted_result=format_result(question,query,results)

            #render the formatted result
            st.write(formatted_result)

