import grpc
from concurrent import futures
import re
from tika import parser
import extract_sentences_pb2
import extract_sentences_pb2_grpc
import threading
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import hashlib
import ollama
from pinecone import Pinecone, ServerlessSpec


pc = Pinecone(api_key="858ccd6d-530a-4430-a4c5-a374f612972a")
index_name = "my-vector-index-llama"

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=4096,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

index = pc.Index(index_name)

app = FastAPI()

class UserInput(BaseModel):
    text: str
    pdf_path: str

def embed_text(text):
    try:
        embeddings = ollama.embeddings(model='llama3.1', prompt=text)
    except Exception as e:
        raise RuntimeError(f"Error during embedding: {e}")
    
    if 'embedding' not in embeddings:
        raise RuntimeError("No 'embedding' key found in model response.")

    return embeddings['embedding']

def calculate_file_hash(file_path):
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def split_text_into_sentences(text):
    cleaned_text = re.sub(r'\n+', ' ', text).strip()
    sentences = re.split(r'(?<=[.!?]) +', cleaned_text)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    return sentences

class PdfProcessor:
    def __init__(self, index, embedder, parser, splitter):
        self.index = index
        self.embed_text = embedder
        self.parse_pdf = parser
        self.split_text = splitter

    def process(self, file_path):
        file_hash = calculate_file_hash(file_path)
        namespace = f"namespace-{file_hash[:10]}"  

        results = self.index.query(
            vector=[0]*4096, 
            top_k=1, 
            include_metadata=True, 
            filter={"hash": file_hash},
            namespace=namespace
        )
        
        if results["matches"]:
            print(f"File already processed. Retrieving from database...")
            sentences = [match['metadata']['text'] for match in results['matches']]
        else:
            print(f"File not processed. Embedding and saving...")
            try:
                raw = self.parse_pdf(file_path)
                text = raw['content'].strip()
                sentences = self.split_text(text)

                for i, sentence in enumerate(sentences):
                    embed = self.embed_text(sentence)
                    unique_id = f"{file_hash[:10]}-sentence-{i}"
                    self.index.upsert(vectors=[{
                        'id': unique_id,
                        'values': embed,
                        'metadata': {'text': sentence, 'hash': file_hash}
                    }], namespace=namespace)
                print(f"Sentences successfully saved.")

            except FileNotFoundError:
                print(f"{file_path} not found. Please check the file path.")
                raise
            except Exception as e:
                print(f"Error occurred: {e}")
                raise

        return sentences, namespace

def query_similar_texts(user_text, threshold=0.5, namespace=None):
    user_embedding = embed_text(user_text)
    results = index.query(
        vector=user_embedding, 
        top_k=10,
        include_values=True,
        include_metadata=True,
        namespace=namespace
    )

    print(f"Raw results from query: {results}")

    filtered_results = []
    for match in results['matches']:
        similarity = match['score']
        if similarity >= threshold:
            filtered_results.append({
                "id": match['id'],
                "similarity": similarity,
                "text": match['metadata']['text']
            })
    
    return filtered_results


pdf_processor = PdfProcessor(
    index=index,
    embedder=embed_text,
    parser=parser.from_file,
    splitter=split_text_into_sentences
)

@app.post("/process")
async def process_request(user_input: UserInput):
    try:
        sentences, namespace = pdf_processor.process(user_input.pdf_path)
    
        results = query_similar_texts(user_input.text, namespace=namespace)
        
        return {"message": "PDF processing and querying complete.", "results": results}
    except Exception as e:
        return {"error": str(e)}

# gRPC service
class PdfService(extract_sentences_pb2_grpc.PdfServiceServicer):
    def ExtractSentences(self, request, context):
        pdf_path = request.pdf_path
        try:
            sentences, _ = pdf_processor.process(pdf_path)
            print(f"Sentences extracted: {sentences}")

            response = extract_sentences_pb2.SentenceResponse()
            response.sentences.extend(sentences)
            return response
        except Exception as e:
            context.set_details(f'Error processing PDF: {str(e)}')
            context.set_code(grpc.StatusCode.INTERNAL)
            return extract_sentences_pb2.SentenceResponse()

def serve_grpc():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    extract_sentences_pb2_grpc.add_PdfServiceServicer_to_server(PdfService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server is running...")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down gRPC server...")
        server.stop(0)

def serve_fastapi():
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":

    grpc_thread = threading.Thread(target=serve_grpc)
    grpc_thread.start()

    fastapi_thread = threading.Thread(target=serve_fastapi)
    fastapi_thread.start()

    grpc_thread.join()
    fastapi_thread.join()
