import streamlit as st
from pathlib import Path
from langchain_classic.agents import create_sql_agent
from langchain_classic.sql_database import SQLDatabase
from langchain_classic.agents.agent_types import AgentType
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_classic.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq

st.set_page_config(page_title="SQL Agent with Streamlit", page_icon="🦜")
st.title("🦜 LangChain: Chat with SQL DB")

INJECTION_WARNING = """ SQL Agent can be vulnerable to SQL injection if not used carefully. 
Use a DB role with limited permissions and avoid using user input directly in SQL queries.
"""

LOCALDB = "USE_LOCALDB"
MYSQL="USE_MYSQL"

radio_opt=["Use SQLite3 Database - Student.db", "Connect to you SQL Database"]

select_opt=st.sidebar.radio(label="Choose the DB you want to chat with", options=radio_opt)

if radio_opt.index(select_opt) == 1:
    db_uri=MYSQL
    mysql_host = st.sidebar.text_input("MySQL Host Name")
    mysql_user = st.sidebar.text_input("MySQL User Name")
    mysql_pass = st.sidebar.text_input("MySQL Password", type="password")
    mysql_db = st.sidebar.text_input("MySQL Database Name")
else:
    db_uri=LOCALDB
    st.sidebar.info("Using local SQLite database: student.db")

api_key = st.sidebar.text_input("Groq API Key", type="password")

if not db_uri or not api_key:
    st.warning("Please enter the database information and uri.")
    st.stop()

if not api_key:
    st.warning("Please enter your Groq API key.")
    st.stop()

## LLM Moidel
llm = ChatGroq(groq_api_key=api_key, model_name="llama-3.3-70b-versatile", streaming=True)

@st.cache_resource(ttl="2h")
def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_pass=None, mysql_db=None):
    if db_uri == LOCALDB:
        dbfilepath = (Path(__file__).parent / "student.db").absolute()
        print(dbfilepath)
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite://", creator=creator))
    elif db_uri == MYSQL:
        if not (mysql_host and mysql_user and mysql_pass and mysql_db):
            st.error("Please enter all MySQL connection details.")
            st.stop()
            return None
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_pass}@{mysql_host}/{mysql_db}"))
    else:
        st.warning("Invalid database selection.")
        return None
    
if db_uri==MYSQL:
    db = configure_db(db_uri, mysql_host, mysql_user, mysql_pass, mysql_db)
else:
    db = configure_db(db_uri)

## Toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent=create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)

if "messages" not in st.session_state or st.sidebar.button("Clear Conversation"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])
    
user_query = st.chat_input(placeholder="Ask a question about the database...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback = StreamlitCallbackHandler(st.container())
        response = agent.run(user_query, callbacks=[streamlit_callback])
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)
