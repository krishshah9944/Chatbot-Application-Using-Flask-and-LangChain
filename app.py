

import requests
import streamlit as st

def get_chatbot_response(query):
    # Prepare the JSON body for the POST request
    json_body = {"query": query}

    try:
        # Make a POST request to the Flask API
        response = requests.post("http://127.0.0.1:5000/chat", json=json_body)
        

        # Check if the response is successful
        if response.status_code == 200:
            response_json=response.json()
            print(response_json)
            return response_json["answer"]
        else:
            st.write("else inside")
            return f"Error: {response.status_code} - {response.json().get('error', 'Unknown error')}"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {str(e)}"

## Streamlit app
st.title("Chatbot Application Using Flask and LangChain")

    

# User input
query = st.text_input("Enter your query:")

if query:
    
    chatbot_response = get_chatbot_response(query)
    

    
    st.write("Chatbot Response:")
    st.write(chatbot_response)
