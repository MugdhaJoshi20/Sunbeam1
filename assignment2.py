import sqlite3
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

#open database connection
connection = sqlite3.connect('./college.db')

#create a model
model = ChatOllama(model="llama3")

#template to create query
query_template = """You are sqlite3 eveloper,writing sqlite3 queries.
    Use the given schema and answer users question.
    Question: {question}
    Schema: {schema}
    Query:

    Generate only query nothing else.
    """
#template to format result
result_template = """ You are database assistant.
given users question,generated query and results found, you need to format result accordingly.4

# following are some examples:
# Question:what is topper's name?
# Query: SELECT name FROM students ORDER BY marks DESC LIMIT 1;
# results: [('John Doe',)]
# Formatted result: The topper's name is John Doe.

    Question: {question}
    Query: {query}
    results: {results}
    
    Print only fromatted results nothing else.
    """


#define the schema
schema = """
    CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    student_id INTEGER,
    department TEXT NOT NULL,
    year REAL
    );


    CREATE TABLE professors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    );


    CREATE TABLE courses(
    id INTEGER PRIMARY KEY,
    course_code INTEGER,
    course_name TEXT NOT NULL,
    professor_id INTEGER,
    FOREIGN KEY (professor_id) REFERENCES professors(id)
    );

    CREATE TABLE grades(
    id INTEGER PRIMARY KEY,
    student_id INTEGER,
    course_id INTEGER,
    grade TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
    );

    CREATE TABLE attendence(
    id INTEGER PRIMARY KEY,
    student_id INTEGER,
    course_id INTEGER,
    date INTEGER,
    present INTEGER,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
    );

    """



def execute_query(query):
    print(f"query={query}")
    #create a cursor object
    cursor=connection.cursor()

    #execute the query
    cursor.execute(query)

    #get all results
    rows= cursor.fetchall()

    #commit the database
    # connection.commit()
    
    return rows

def generate_query(question):
    #create a prompt template
    prompt_template = ChatPromptTemplate.from_template(template=query_template)
    prompt= prompt_template.invoke({"question":question,"schema":schema})

    #invoke the prompt and get the result
    result = model.invoke(prompt)
    query=result.content
    print(f"query={query}")

    return query

def format_results(results,query, question):
    prompt_template = ChatPromptTemplate.from_template(template=result_template)
    prompt = prompt_template.invoke({"question": question, "query": query, "results": results})

    #invoke the prompt and get the result
    final_result = model.invoke(prompt)
    print(final_result.content)

while True:
    #get the question from user
    question = input("enter your question:")

    if question=="exit":
        break

    #generate the query using model
    query=generate_query(question)

    #answer the user's question
    results = execute_query(query)
    
    #format the results
    format_results(results, query, question)

#close the conection
connection.close()