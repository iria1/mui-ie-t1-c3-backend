import openai
import re
import time
from llama_index.core import VectorStoreIndex, Settings, SimpleDirectoryReader
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import SimpleNodeParser
from utils.config import OPENAI_API_KEY
from better_profanity import profanity
from cachetools import LRUCache

# ------------------------------
# Session memory management
# ------------------------------

class MemoryEntry:
    def __init__(self):
        self.memory = ChatMemoryBuffer(token_limit=1000)
        self.last_seen = time.time()

# LRU cache with max 100 concurrent sessions
user_memories = LRUCache(maxsize=100)
SESSION_TIMEOUT = 600  # 10 minutes

def get_user_memory(session_id: str):
    now = time.time()

    # Cleanup expired sessions lazily
    expired = [sid for sid, entry in user_memories.items()
               if now - entry.last_seen > SESSION_TIMEOUT]
    for sid in expired:
        del user_memories[sid]

    # Return or create new memory entry
    if session_id not in user_memories:
        user_memories[session_id] = MemoryEntry()
    user_memories[session_id].last_seen = now

    return user_memories[session_id].memory

# ------------------------------
# Core chatbot logic
# ------------------------------

def get_bot_response(user_input: str, session_id: str) -> str: 
    """
    Generate a chatbot reply for Caro, a friendly guide on cyberbullying.
    Applies content filters before passing input to the LLM.
    """
    if is_code_input(user_input):
        return "Sorry, I cannot run or answer questions about scripts or code."

    memory = get_user_memory(session_id)
    chat_engine = index.as_chat_engine(
        chat_mode="best",
        memory=memory,
        system_prompt=(
            "You are Caro, a kind and supportive guide for kids aged 10–15 about cyberbullying. "
            "Answer using only the retrieved information. "
            "If the retrieved information is off-topic or not about cyberbullying, politely say you can only talk about cyberbullying topics. "
            "Keep answers simple, positive, and focused strictly on cyberbullying. "
            "Avoid health, legal, or personal advice."
        )
    )

    response = chat_engine.chat(user_input)
    return response.response

def load_and_chunk_docs(directory="data", chunk_size=256):
    documents = SimpleDirectoryReader(directory).load_data()
    parser = SimpleNodeParser.from_defaults(chunk_size=chunk_size)
    nodes = parser.get_nodes_from_documents(documents)
    print(f"Loaded {len(documents)} documents")
    print(f"Parsed into {len(nodes)} chunks")
    return nodes

def is_code_input(text: str) -> bool:
    code_patterns = [
        r"\bimport\b", r"\beval\b", r"\bexec\b", r"os\.system", r"subprocess", r"`.*?`", 
        r"\brun\b", r"\bcompile\b", r"\bscript\b", r"\bshell\b", r"\bcommand\b"
    ]
    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in code_patterns)

def contains_bad_words(text: str) -> bool:
    return profanity.contains_profanity(text)

# ------------------------------
# Initialization
# ------------------------------

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
