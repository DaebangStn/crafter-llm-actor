import chromadb
from chromadb.config import Settings


client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="dummy",
))
collection = client.get_or_create_collection('test')
collection.add(
    documents=["This is a document", "This is another document"],
    metadatas=[{"source": "my_source"}, {"source": "my_source"}],
    ids=["id3", "id4"]
)

client.persist()
