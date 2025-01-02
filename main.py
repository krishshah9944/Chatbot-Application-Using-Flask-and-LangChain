from flask import Flask, request,jsonify,Response
from flask_restful import Api, Resource
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
os.environ["GOOGLE_API_KEY"]=os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
llm=ChatGoogleGenerativeAI(model='gemini-1.5-flash')
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.load import dumps
import json




urls=["https://brainlox.com/courses/category/technical"]
loader = UnstructuredURLLoader(urls=urls)
data=loader.load()



embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")

vectorstoredb=FAISS.from_documents(data,embeddings)


text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
splits=text_splitter.split_documents(data)
vectorstoredb=FAISS.from_documents(data,embeddings)
retriever=vectorstoredb.as_retriever()
retriever

system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use three sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

question_answer_chain=create_stuff_documents_chain(llm,prompt)
rag_chain=create_retrieval_chain(retriever,question_answer_chain)






app = Flask(__name__)
api = Api(app)

class Chat(Resource):
    def post(self):
        # Parse user input
        data = request.get_json()
        user_input = data.get("query", "")
        print(data)
        print(user_input)

        if not user_input:
            return {"error": "Query is required"}, 400

        
        try:
            response = rag_chain.invoke({"input": user_input})
            print(response)
            print(type(response))
           
            if isinstance(response, dict):
                print("hello")
                # If response is a dictionary, return it as JSON
                json_str = dumps(response)
                print(json_str)
                print(type(json_str))
                return Response(json_str, content_type='application/json')
                
            else:
                
                print("else hello")
                return {"error": "Unexpected response format"}, 500
        except Exception as e:
            return {"error": str(e)}, 500

api.add_resource(Chat, "/chat")




if __name__ == "__main__":
    app.run(debug=True)










