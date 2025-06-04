import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


st.title("Career Guidance Chatbot")

systemContext={
    "Counselor": "You are a career counselor. Provide guidance on career choices, education paths, and job opportunities.",
    "Resume Advisor": "You are a resume advisor. Help users create and improve their resumes, providing tips on formatting and content.",
    "Interview Coach": "You are an interview coach. Offer advice on interview preparation, common questions, and how to present oneself effectively."
}
option = st.selectbox(
    "Select one option from the following:",
    ("Counselor", "Resume Advisor", "Interview Coach"),
    index=None,
    placeholder="Select..."
)

#create a new chatollama object

st.write("You selected:", option)

prompt = st.chat_input("Enter your prompt:")
if prompt:
    model = ChatOllama(model="llama3")

    messages=[
    #seeting the context of the conversation
        SystemMessage(content=systemContext[option]),    
        #sending the input from user
        HumanMessage(content=prompt),
        ]
    st.write(f"You entered:{prompt}")
    # get the response  from model
    response= model.invoke(messages)

    #write the response to the screen
    st.write(response.content)

