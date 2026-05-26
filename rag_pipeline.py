import os
import streamlit as st

from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from pypdf import PdfReader

# Cache

retriever_cache = {}


# Load Environment Variables

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


# Embeddings (Lazy Load + Cache)


@st.cache_resource
def load_embeddings():

    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


# Gemini Model (Lazy Load + Cache)


@st.cache_resource
def load_llm():

    return ChatGoogleGenerativeAI(model="gemini-2.5-flash")


# Prompt

prompt = ChatPromptTemplate.from_template("""
You are an AI Research Assistant.

Use the chat history and context to answer.

Chat History:
{chat_history}

Context:
{context}

Question:
{question}

Answer in English only.
""")


# PDF Text Loader


def load_pdf_text(pdf_path):

    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:

        extracted = page.extract_text()

        if extracted:

            text += extracted

    return text


# Main Function


def get_response(query, chat_history, video_id=None, pdf_path=None):

    # Load Models Only When Needed

    llm = load_llm()

    embeddings = load_embeddings()

    # Source Key

    source_key = video_id if video_id else pdf_path

    # Check Cache

    if source_key not in retriever_cache:

        # YouTube Transcript

        if video_id:

            ytt_api = YouTubeTranscriptApi()

            try:

                fetched_transcript = ytt_api.fetch(video_id, languages=["en", "hi"])

            except Exception as e:

                return (f"❌ Transcript Error:\n\n{str(e)}", [])

            text = " ".join([chunk.text for chunk in fetched_transcript])

        # PDF Text Extraction

        elif pdf_path:

            try:

                text = load_pdf_text(pdf_path)

            except Exception as e:

                return (f"❌ PDF Error:\n\n{str(e)}", [])

        # Chunking

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=700, chunk_overlap=150
        )

        chunks = text_splitter.split_text(text)

        # Vector Store

        vectorstore = FAISS.from_texts(chunks, embeddings)

        # Retriever

        retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 2})

        # Save To Cache

        retriever_cache[source_key] = retriever

    # Reuse Retriever

    retriever = retriever_cache[source_key]

    # RAG Chain

    rag_chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough(),
            "chat_history": lambda x: chat_history,
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    # Response

    response = rag_chain.invoke(query)

    retrieved_docs = retriever.invoke(query)

    return response, retrieved_docs
