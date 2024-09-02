Projeyi çalıştırabilmek için ilk olarak Ollama'yı indirin.
https://ollama.com/download


Ollama llama3.1 modülünü indirin
'''bash
ollama pull llama3.1

Gerekli kütüphaneleri indirin.
'''bash
pip install -r requirements.txt

server'ı çalıştırın
'''bash
python server.py

client'ı çalıştırın ve pdf yolunu ve aranacak metni girin
'''bash
python client.py
