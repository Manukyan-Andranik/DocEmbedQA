import uuid
from text_splitter import TextSplitter
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from openai import OpenAI
from util import print_centered_text

# Define the class for database operations
class DataBase:
    # Initialize the database class with necessary parameters
    def __init__(self, spliter, api_key, embedding_size=1536, chunk_size=500):
        self.spliter = spliter
        self.flan = 1
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)
        self.embedding_size = embedding_size
        self.chunk_size = chunk_size
        self.collection_chunk = None
          
    # Method to setup the database
    def setup(self, clear_db):
        print_centered_text("start setup!")
        # If specified, clear the database
        if clear_db:
            try:
                self.clear()
                print_centered_text("Database deleted succesfuly")
            except Exception as e:
                print_centered_text(f"Donte deleted: Error is |{e}|")
        
        # Connect to Milvus server
        connections.connect(host='127.0.0.1', port="19530")
        # Define fields for chunk collection
        fields_chunk = [
            FieldSchema(name='document_id', dtype=DataType.VARCHAR, max_length=128, description="document_id"),
            FieldSchema(name='chunk_id', dtype=DataType.VARCHAR, description="chunk_id", max_length=128, primary_key=True),
            FieldSchema(name='chunk_text', dtype=DataType.VARCHAR, description="chunk_text", max_length=2*self.chunk_size),
            FieldSchema(name='embedings', dtype=DataType.FLOAT_VECTOR, description="", dim=self.embedding_size, is_index=True),
        ]
        # Define fields for chunk collection
        schema_chunk = CollectionSchema(
            fields=fields_chunk, 
            description="", 
            enable_dynamic_field=True, 
            primary_field="chunk_id" 
        )
        # Create chunk collection
        self.collection_chunk = Collection(name='collection_chunk', schema=schema_chunk)
        # Create index for chunk collection
        self.collection_chunk.create_index(
            field_name='embedings', 
            index_params={
                "metric_type": "COSINE", 
                "index_type": "IVF_FLAT", 
                "params": {"nlist": 128}
            }, 
            name='vector_idx'
        )
        print_centered_text("Setupe seccussfuly!")
        
    # Method to load a document into the database
    def load_document(self, file_path):
        # Load the chunk collection
        self.collection_chunk.load()
        try:
            # Split the document into chunks
            splited_doc = self.spliter.read_splitted(file_path)
            # Prepare data for insertion into the chunk collection
            data = [{
                "chunk_text": text,
                "chunk_id": self._get_uuid(),
                "document_id": file_path,
                "embedings": self._get_embedding(text)
            } for text in splited_doc]
            # Insert data into the chunk collection
            self.collection_chunk.insert(data)
            print_centered_text("Inserted successfully!")
            return 1
        except Exception as e:
            # Print error message if insertion fails
            print(e)
            return 0
    # Method to search for text in the database
    def search(self, text):
        # Get embedding for the input text
        embedding = self._get_embedding(text)
        # Search for similar embeddings in the chunk collection
        result = self.collection_chunk.search(
            data=[embedding], 
            anns_field='embedings', 
            param={"metric_type": "COSINE", "params": {}}, 
            limit=3,         
            output_fields=["chunk_text"]
        )
        # Extract chunk texts from search results
        search_result = [hit.chunk_text for hit in result[0]]
        return ", ".join(search_result)
    # Method to clear the database
    def clear(self):
        utility.drop_collection(collection_name="collection_chunk")
        print_centered_text("Database cleared!")
    
    # Method to generate UUID
    def _get_uuid(self):
        return str(uuid.uuid4()) 
    
    # Method to get embedding for text using OpenAI
    def _get_embedding(self, text):
        response = self.client.embeddings.create(model="text-embedding-3-small", input=[text])
        return response.data[0].embedding