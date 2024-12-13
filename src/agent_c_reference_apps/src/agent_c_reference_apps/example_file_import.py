import argparse
import os
import logging
import weaviate
from dotenv import load_dotenv

# Note: we load the env file here so that it's loaded when we start loading the libs that depend on API KEYs.   I'm looking at you Eleven Labs
load_dotenv(override=True)

from weaviate import WeaviateClient
from weaviate.classes.config import Configure, Property, DataType, Tokenization

from agent_c_rag import SegmentRepo, StructuredParagraphSegmenter, DocumentLoader, TextSegment, ContextFormatter, SourceChronoFormatter
from weaviate.auth import AuthApiKey
from agent_c import TikTokenTokenCounter


class SimpleIndexer:
    def __init__(self, client: WeaviateClient, collection_name):
        self.client = client
        self.collection_name = collection_name
        self.collection = self.create_collection()
        self.loader = DocumentLoader()
        self.repo = SegmentRepo(client)

    @property
    def collection_object(self):
        return [
            {'name': "created", 'description': "The timestamp of the segment creation", 'data_type': DataType.DATE, 'index_filterable': True, 'index_searchable': False, "vectorize_property_name": True},
            {'name': "content", 'description': "The content of the segment to be displayed to the model", 'data_type': DataType.TEXT, 'index_filterable': False, 'index_searchable': False},
            {'name': "index_content", 'description': "The content of the segment to be indexed for search", 'data_type': DataType.TEXT, 'index_filterable': False, 'index_searchable': True, "vectorize_property_name": False},
            {'name': "sequence", 'description': "The sequence number of the segment", 'data_type': DataType.INT, 'index_filterable': True, 'index_searchable': False, "vectorize_property_name": False},
            {'name': "token_count", 'description': "The number of tokens in the content property", 'data_type': DataType.INT, 'index_filterable': True, 'index_searchable': False, "vectorize_property_name": False},
            {'name': "citation", 'description': "The citation of the segment, should be a URI/filename or other unique human readable ID for the model to cite.", 'data_type': DataType.TEXT, 'index_filterable': True, 'index_searchable': True, "vectorize_property_name": True},
            {'name': "categories", 'description': "One or more categories for the segment", 'data_type': DataType.TEXT_ARRAY, 'index_filterable': True, 'index_searchable': True, "vectorize_property_name": True},
            {'name': "keywords", 'description': "One or more keywords for the segment", 'data_type': DataType.TEXT_ARRAY, 'index_filterable': True, 'index_searchable': True, "vectorize_property_name": True},
            {'name': "parent_segment", 'description': "A UUID pointing to a larger, parent segment.", 'data_type': DataType.UUID, 'index_filterable': True, 'index_searchable': False, "vectorize_property_name": False}
        ]


    def create_collection(self):
        try:
            collection = self.client.collections.get(self.collection_name)
            if collection.shards() == 0:
                collection = self.client.collections.create(self.collection_name, properties=self.collection_object, vectorizer_config=Configure.Vectorizer.text2vec_openai())
        except Exception as e:
            logging.info(f"Creating collection {self.collection_name}")
            collection = self.client.collections.create(self.collection_name, properties=self.collection_object, vectorizer_config=Configure.Vectorizer.text2vec_openai())

        return collection

    def load_files(self, files: list[str], chunk_size: int = 500):
        for filename in files:
            self.load_file(filename, chunk_size)


    def load_file(self, filename, chunk_size: int = 500):
        logging.info(f"Loading {filename}")
        elements = self.loader.load_document(filename)

        logging.info(f"Segmenting {filename}")
        segmenter = StructuredParagraphSegmenter(chunk_size=chunk_size, token_counter=TikTokenTokenCounter())
        segments = segmenter.segment_elements(elements, filename)

        logging.info(f"Indexing {filename}")
        self.repo.batch_load_segments(self.collection_name, segments)

        logging.info(f"Indexed {len(segments)} segments from {filename}")



def main():
    parser = argparse.ArgumentParser(description="Example Indexer")
    parser.add_argument('--collection', '-c', type=str, help='The Weaviate collection name to populate', default='default')
    parser.add_argument('--file', '-f', type=str, help='A path to a file, or folder of files')

    args = parser.parse_args()

    client = weaviate.connect_to_local(headers={"X-Openai-Api-Key": os.getenv("OPENAI_APIKEY")})

    loader = SimpleIndexer(client, args.collection_name)


    if os.path.isdir(args.file):
        files = [os.path.join(args.file, f) for f in os.listdir(args.file)]
    else:
        files = [args.file]

    loader.load_files(files)

if __name__ == "__main__":
    main()