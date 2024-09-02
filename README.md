#llama3.1-text_search

##This project processes PDF files to extract sentences, embeds them using a language model, and stores them in a Pinecone index. It provides both gRPC and FastAPI interfaces to query for similar sentences.


Projeyi çalıştırabilmek için ilk olarak Ollama'yı indirin.
https://ollama.com/download


Ollama llama3.1 modülünü indirin

`ollama pull llama3.1`

Gerekli kütüphaneleri indirin.

`pip install -r requirements.txt`

server'ı çalıştırın

`python server.py`

client'ı çalıştırın ve pdf yolunu ve aranacak metni girin

'python client.py'
