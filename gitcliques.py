import streamlit as st
import requests
import networkx as nx
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

# Function to get the users a person is following
def get_following(username, token=None):
    url = f"https://api.github.com/users/{username}/following"
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return [user['login'] for user in response.json()]
    else:
        st.error(f"Failed to fetch following for {username}. Status code: {response.status_code}")
        return []

# Function to create the directed graph based on followers and following
def create_follower_graph(usernames, token=None):
    G = nx.DiGraph()
    
    for username in usernames:
        G.add_node(username)
        
        # Get the users that this user follows
        following = get_following(username, token)
        
        # Get the users who follow this user
        followers = get_followers(username, token)
        
        for user in following:
            if user in usernames:
                G.add_edge(username, user)
                
        for user in followers:
            if user in usernames and not G.has_edge(user, username):
                G.add_edge(user, username)
    
    return G

# Function to find bidirectional and unidirectional edges
def find_bidirectional_unidirectional_edges(G):
    bidirectional_edges = []
    unidirectional_edges = []
    
    for u, v in G.edges():
        if G.has_edge(v, u):
            bidirectional_edges.append((u, v))
        else:
            unidirectional_edges.append((u, v))
    
    return bidirectional_edges, unidirectional_edges

# Streamlit UI
st.title("GitHub Follower Clique Finder with Directed Arrows and Edge Coloring")

# Using st.form to allow submission by pressing Enter
with st.form(key="github_form"):
    # Input: Set of GitHub usernames with a placeholder instead of default text
    usernames_input = st.text_input("Enter GitHub usernames (comma-separated)", placeholder="e.g., user1, user2, user3")
    
    # GitHub API Token (optional)
    token = st.text_input("GitHub API Token (optional)")
    
    # Submit button
    submit_button = st.form_submit_button(label="Find Cliques and Draw Graph")

# Only process when the form is submitted
if submit_button:
    # Process usernames input
    usernames = [u.strip() for u in usernames_input.split(",") if u.strip()]
    
    if not usernames:
        st.error("Please provide at least one GitHub username.")
    else:
        st.info("Fetching followers and following data, creating directed graph...")
        G = create_follower_graph(usernames, token)
        
        st.info("Finding bidirectional and unidirectional edges...")
        bidirectional_edges, unidirectional_edges = find_bidirectional_unidirectional_edges(G)
        
        # Visualization
        pos = nx.spring_layout(G)
        
        # Draw all nodes
        nx.draw_networkx_nodes(G, pos, node_color="lightblue", node_size=500)
        nx.draw_networkx_labels(G, pos)
        
        # Draw unidirectional edges in gray
        nx.draw_networkx_edges(G, pos, edgelist=unidirectional_edges, edge_color="gray", arrows=True, arrowstyle='-|>', arrowsize=15)
        
        # Draw bidirectional edges in a different color, say blue
        nx.draw_networkx_edges(G, pos, edgelist=bidirectional_edges, edge_color="blue", arrows=True, arrowstyle='-|>', arrowsize=15)
        
        plt.title("GitHub Follower Graph with Bidirectional (Blue) and Unidirectional (Gray) Arrows")
        st.pyplot(plt)
