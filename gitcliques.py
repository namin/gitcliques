import streamlit as st
import requests
import networkx as nx
from itertools import combinations
import matplotlib.pyplot as plt

# Function to get the followers of a user
def get_followers(username, token=None):
    url = f"https://api.github.com/users/{username}/followers"
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return [user['login'] for user in response.json()]
    else:
        st.error(f"Failed to fetch followers for {username}. Status code: {response.status_code}")
        return []

# Function to create the graph
def create_follower_graph(usernames, token=None):
    G = nx.Graph()
    for username in usernames:
        G.add_node(username)
        followers = get_followers(username, token)
        for follower in followers:
            if follower in usernames:
                G.add_edge(username, follower)
    return G

# Function to find cliques
def find_cliques(G):
    return list(nx.find_cliques(G))

# Streamlit UI
st.title("GitHub Follower Clique Finder")

# Input: Set of GitHub usernames
usernames = st.text_area("Enter GitHub usernames (comma-separated)", "user1, user2, user3")
usernames = [u.strip() for u in usernames.split(",") if u.strip()]

# GitHub API Token (optional)
token = st.text_input("GitHub API Token (optional)")

if st.button("Find Cliques"):
    if not usernames:
        st.error("Please provide at least one GitHub username.")
    else:
        st.info("Fetching followers and creating graph...")
        G = create_follower_graph(usernames, token)
        
        st.info("Finding cliques...")
        cliques = find_cliques(G)
        
        if cliques:
            st.success(f"Found {len(cliques)} cliques.")
            for i, clique in enumerate(cliques):
                st.write(f"Clique {i+1}: {', '.join(clique)}")
        else:
            st.warning("No cliques found.")
        
        # Optionally visualize the graph
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="gray")
        plt.title("GitHub Follower Graph")
        st.pyplot(plt)

