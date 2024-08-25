from typing import Dict, List
from neo4j import GraphDatabase, TRUST_ALL_CERTIFICATES
import streamlit as st
from langchain_community.graphs import Neo4jGraph

graph = Neo4jGraph(
    url=st.secrets["NEO4J_URI"],
    username=st.secrets["NEO4J_USERNAME"],
    password=st.secrets["NEO4J_PASSWORD"],
    database="neo4j",
    driver_config={"encrypted": True, "trust": TRUST_ALL_CERTIFICATES}
)

print(graph.query("Match (n) return n limit 10"))
