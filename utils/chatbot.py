import openai
import re
from llama_index.core import VectorStoreIndex, Settings, SimpleDirectoryReader
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import SimpleNodeParser
from utils.config import OPENAI_API_KEY
from better_profanity import profanity

# function declaration
def get_bot_response(user_input: str) -> str: 
    """
    Generate a chatbot reply for Caro, a friendly guide on cyberbullying.
    Applies content filters before passing input to the LLM.
    """
    # Block code-related queries to prevent unwanted code execution
    if is_code_input(user_input):
        return "Sorry, I cannot run or answer questions about scripts or code."

    response = chat_engine.chat(user_input)

    return response.response

def load_and_chunk_docs(directory="data", chunk_size=256):
    """
    Loads and chunks all markdown files from the specified folder.
    Returns a list of nodes (text chunks).
    """
    # Load all documents from the folder
    documents = SimpleDirectoryReader(directory).load_data()

    # Create a parser to split documents into chunks
    parser = SimpleNodeParser.from_defaults(chunk_size=chunk_size)
    nodes = parser.get_nodes_from_documents(documents)

    # Print number of documents and chunks
    print(f"Loaded {len(documents)} documents")
    print(f"Parsed into {len(nodes)} chunks")

    return nodes

def is_code_input(text: str) -> bool:
    """
    Detects if the user is attempting to run or ask about code/script execution.
    """
    # Common code-related keywords
    code_patterns = [
        r"\bimport\b", r"\beval\b", r"\bexec\b", r"os\.system", r"subprocess", r"`.*?`", 
        r"\brun\b", r"\bcompile\b", r"\bscript\b", r"\bshell\b", r"\bcommand\b"
    ]

    # Lowercase input for case-insensitive matching
    text_lower = text.lower()

    # Return True if any pattern matches
    return any(re.search(pattern, text_lower) for pattern in code_patterns)

def contains_bad_words(text: str) -> bool:
    """
    Detects if the user input contains profanity or inappropriate language.
    Uses better_profanity's default filter list.
    """
    # Search if text contains any word in the better_profanity library's default filter list
    return profanity.contains_profanity(text)

# Set API key for OpenAI client
openai.api_key = OPENAI_API_KEY

# Load and chunk the knowledge base
documents = load_and_chunk_docs("data/")

# Define LLM settings
llm = OpenAI(
    model="gpt-4o",
    temperature=0.5,
    max_tokens=300
)

# Load embedding model
embed_model = OpenAIEmbedding(model="text-embedding-3-small")

# Set defined LLM and embedding models as global default
Settings.llm = llm
Settings.embed_model = embed_model

# Create RAG index
index = VectorStoreIndex.from_documents(documents)

# Create the retriever
retriever = index.as_retriever(similarity_top_k=2)

# Create session semory
memory = ChatMemoryBuffer(token_limit=1000)

# Create chat engine directly from index
chat_engine = index.as_chat_engine(
    chat_mode="best", # Use 'best' to select the most relevant chunks for answering
    memory=memory, # Pass the chat memory buffer to maintain conversation context
    system_prompt = (
        "You are Caro, a kind and supportive guide for kids aged 10–15 about cyberbullying. "
        "Answer using only the retrieved information. "
        "If the retrieved information is off-topic or not about cyberbullying, politely say you can only talk about cyberbullying topics. "
        "Keep answers simple, positive, and focused strictly on cyberbullying. "
        "Avoid health, legal, or personal advice."
    ) # Define chatbot behaviour
)