from langchain_astradb import AstraDBVectorStore
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os
from ecombot.data_converter import convert_data

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

embedding = OpenAIEmbeddings()

def ingest_data(status):
    vector_store = AstraDBVectorStore(
        embedding=embedding,
        collection_name="ecomchatbot_vector_store",
        api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
        token= os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
        namespace=os.getenv("ASTRA_DB_KEYSPACE")
    )

    if status == None:
        docs = convert_data()
        inserted_ids = vector_store.add_documents(docs)
    else:
        return vector_store
    
    return vector_store,inserted_ids

if __name__ == "__main__":
    vector_store,inserted_ids = ingest_data(None)

    print(f"\nInserted {len(inserted_ids)} documents.")

    results = vector_store.similarity_search("can you tell me the low budget sound basshead?")

    for res in results:
        print(f"* {res.page_content} [{res.metadata}]")