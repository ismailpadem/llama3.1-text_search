import grpc
import extract_sentences_pb2
import extract_sentences_pb2_grpc
import requests

def call_grpc(pdf_path):
    # gRPC setup
    channel = grpc.insecure_channel('localhost:50051')
    stub = extract_sentences_pb2_grpc.PdfServiceStub(channel)

    request = extract_sentences_pb2.PdfRequest(pdf_path=pdf_path)
    
"""    try:
        response = stub.ExtractSentences(request)
        print("gRPC Response: ", response.sentences)
        return response.sentences
    except grpc.RpcError as e:
        print(f"gRPC Error: {e.details()}")
        return []"""

def call_fastapi(user_text, pdf_path):
    url = "http://127.0.0.1:8000/process"
    data = {"text": user_text, "pdf_path": pdf_path}

    try:
        response = requests.post(url, json=data)
        response_data = response.json()
        print("FastAPI Response: ", response_data['message'])
        
        # Display the similarity results
        print("Similar texts found:")
        for result in response_data.get('results', []):
            print(f"ID: {result['id']}, Similarity: {result['similarity']}, Text: {result['text']}")
        
    except Exception as e:
        print(f"FastAPI Error: {str(e)}")


if __name__ == "__main__":
    pdf_path = input("Enter PDF path: ")
    extracted_sentences = call_grpc(pdf_path)

    user_text = input("Enter text to compare: ")
    
    call_fastapi(user_text, pdf_path)