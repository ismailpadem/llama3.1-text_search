**llama3.1-text_search**

*This project processes PDF files to extract sentences, embeds them using a language model, and stores them in a Pinecone index. It provides both gRPC and FastAPI interfaces to query for similar sentences.**

*To run the project, first download Ollama from*: 
`https://ollama.com/download`

Download the Ollama llama3.1 module:
`ollama pull llama3.1`

Install the required packages:
`pip install -r requirements.txt`

Start the server:
`python server.py`

Run the client and enter the path to the PDF and the text to search:
`python client.py`
