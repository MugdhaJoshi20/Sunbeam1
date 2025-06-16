import streamlit as st
from langchain_ollama import OllamaEmbeddings,ChatOllama
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader


#chat template to be used
template=""" You are an recipe assistant bot.Answer user's question using the context provided.
If the question can not be answered using context,return "I don't know".
Question: {question}
Context: {context}
Answer:
"""

#create a model
model = ChatOllama(model="mistral")

st.title("Chat with BOT")
st.header("Recipe ChatBot app")

def create_embeddings_for_pdf_file():

    loader = TextLoader("recipes.txt", encoding="utf-8")
    documents = loader.load()
    #collect the documents
    docs=[]
    id=1
    for page in documents:
        contents = page.page_content
        docs.append(Document(id=id,page_content=contents))
        id+=1

    #spilt the documents using splitter 
    splitter=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = splitter.split_documents(docs)

    #create the chroma vector store
    vector_store = Chroma(embedding_function=OllamaEmbeddings(model="nomic-embed-text"), persist_directory="chroma_db",collection_name="pdf_collection")
    #add the documents
    vector_store.add_documents(docs)

    #store vector store in session state
    st.session_state.vector_store = vector_store

def get_answer_of_user_question(question):

    #get the context
    context=st.session_state.vector_store.search(question,search_type="similarity", k=5)
    
    #create the prompt
    prompt_template = ChatPromptTemplate.from_template(template=template)
    prompt = prompt_template.invoke({"question": question, "context": context})

    #get the answer
    response = model.invoke(prompt)
    st.write(response.content)
    
create_embeddings_for_pdf_file()


#get the question from user
question =  st.chat_input("Ask your question about pdf file")

if question:
    #get the answer
    get_answer_of_user_question(question)
        

