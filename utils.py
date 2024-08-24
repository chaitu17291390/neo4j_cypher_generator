from typing import Dict, List
import streamlit as st
from langchain_community.graphs import Neo4jGraph

graph = Neo4jGraph(
    url=st.secrets["NEO4J_URI"],
    username=st.secrets["NEO4J_USERNAME"],
    password=st.secrets["NEO4J_PASSWORD"],
    database="supplychaindb"
)

print(graph.query("Match (n) return n limit 10"))