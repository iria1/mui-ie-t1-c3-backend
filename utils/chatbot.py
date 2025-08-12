import openai
import re
from llama_index.core import VectorStoreIndex, Settings, SimpleDirectoryReader
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import SimpleNodeParser
from utils.config import OPENAI_API_KEY
from better_profanity import profanity

# function declaration
def get_bot_response(user_input: str) -> str:
    if is_code_input(user_input):
        return "Sorry, I cannot run or answer questions about scripts or code."

    if contains_bad_words(user_input):
        return (
            "Let’s try to keep things respectful. Words can really affect people.\n"
            "If someone said that to you, I’m here to help you talk about what you can do."
        )

    # Inject persona consistently
    persona_prefix = (
        "You are Caro, a friendly guide for kids (10–15) about cyberbullying. Be warm, simple, and safe. No advice on health, law, or personal info."
        f"User: {user_input}\nCaro:"
    )

    response = query_engine.query(persona_prefix)
    return str(response)

def load_and_chunk_docs(directory="data", chunk_size=512):
    """
    Loads and chunks all markdown files from the specified folder.
    Returns a list of nodes (text chunks).
    """
    documents = SimpleDirectoryReader(directory).load_data()
    parser = SimpleNodeParser.from_defaults(chunk_size=chunk_size)
    nodes = parser.get_nodes_from_documents(documents)
    print(f"Loaded {len(documents)} documents")
    print(f"Parsed into {len(nodes)} chunks")
    return nodes

def is_code_input(text: str) -> bool:
    """
    Detects if the user is attempting to run or ask about code/script execution.
    """
    code_patterns = [
        r"\bimport\b", r"\beval\b", r"\bexec\b", r"os\.system", r"subprocess", r"`.*?`", 
        r"\brun\b", r"\bcompile\b", r"\bscript\b", r"\bshell\b", r"\bcommand\b"
    ]
    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in code_patterns)

def contains_bad_words(text: str) -> bool:
    """
    Detects if the user input contains profanity or inappropriate language.
    Uses better_profanity's default filter list.
    """
    return profanity.contains_profanity(text)


# LLM initialization
openai.api_key = OPENAI_API_KEY

# Load and chunk the knowledge base
documents = load_and_chunk_docs("data/")

# Define LLM and embedding model
llm = OpenAI(model="gpt-4o", temperature=0.3, max_tokens=100)
embed_model = OpenAIEmbedding(model="text-embedding-3-small")

Settings.llm = llm
Settings.embed_model = embed_model

index = VectorStoreIndex.from_documents(documents)

system_prompt = (
    "You are Caro, a friendly digital guide helping youths aged 10–15 understand and respond to cyberbullying. "
    "You must never give medical or legal advice. Never ask for or store personal information. "
    "Speak in a friendly, simple, and supportive tone. If a question is unrelated, gently redirect the user to topics on cyberbullying."
)

query_engine = index.as_query_engine(
    similarity_top_k=2,
    system_prompt=system_prompt,
    response_mode="compact"
)