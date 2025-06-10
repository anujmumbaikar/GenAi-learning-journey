# flake8: noqa
from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path  # built-in library
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore

load_dotenv()

pdf_path = Path(__file__).parent / "WEB-PROGRAMMING.pdf"  # means current file's parent directory, then go to promptingGuide.txt file

loader = PyPDFLoader(pdf_path)
docs = loader.load()  # this will load the pdf file and return a list of documents
# docs is a list of Document objects, each containing the text of a page in the PDF in array format.
# print(docs[6])  # print the content of the a page index represents the page number


# chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000 , # 1000characters per chunk
    chunk_overlap = 200, # 200 characters overlap between chunks, why?? to get the context of previous and next chunk
)
split_docs = text_splitter.split_documents(docs)  # this will split the documents into chunks

#now we have to make vector embeddings.
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large",
)

#now using embedding model create embeddings for the split documents and store them in a vector databases.
vector_store = QdrantVectorStore.from_documents(
    documents=split_docs,
    url="http://vector_db:6333",
    collection_name = "doc_vector",
    embedding=embedding_model
)
print("Indexing complete. You can now query the vector store.")