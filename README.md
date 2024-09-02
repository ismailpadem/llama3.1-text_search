# llama3.1-text_search

## This project processes PDF files to extract sentences, embeds them using a language model, and stores them in a Pinecone index.

*To run the project, first download Ollama from*:<br/>
`https://ollama.com/download`

Download the Ollama llama3.1 module:<br/>
`ollama pull llama3.1`

Install the required packages:<br/>
`pip install -r requirements.txt`

Start the server:<br/>
`python server.py`

Run the client and enter the path to the PDF and the text to search:<br/>
`python client.py`
