import streamlit as st

from rag_pipeline import get_response

# Page Config

st.set_page_config(page_title="AI Research Assistant", page_icon="🤖", layout="wide")


# Custom CSS

st.markdown(
    """
<style>

.main {
    max-width: 1200px;
}

.block-container {
    padding-top: 2rem;
}

.stChatMessage {
    border-radius: 15px;
    padding: 12px;
}

</style>
""",
    unsafe_allow_html=True,
)


# Session State

if "youtube_chats" not in st.session_state:

    st.session_state.youtube_chats = {"YouTube Chat 1": []}


if "pdf_chats" not in st.session_state:

    st.session_state.pdf_chats = {"PDF Chat 1": []}


if "current_youtube_chat" not in st.session_state:

    st.session_state.current_youtube_chat = "YouTube Chat 1"


if "current_pdf_chat" not in st.session_state:

    st.session_state.current_pdf_chat = "PDF Chat 1"


if "current_source" not in st.session_state:

    st.session_state.current_source = None


# Video ID Extractor


def extract_video_id(url):

    try:

        if "v=" not in url:

            return None

        video_id = url.split("v=")[1].split("&")[0]

        if len(video_id) != 11:

            return None

        return video_id

    except:

        return None


# Source Type

source_type = "youtube"


# Sidebar

with st.sidebar:

    st.header("⚙️ AI Research Assistant")

    st.divider()

    st.subheader("📺 YouTube Chats")

    # New YouTube Chat

    if st.button("➕ New YouTube Chat", use_container_width=True):

        new_chat = f"YouTube Chat {len(st.session_state.youtube_chats)+1}"

        st.session_state.youtube_chats[new_chat] = []

        st.session_state.current_youtube_chat = new_chat

        st.rerun()

    # Display YouTube Chats

    for chat_name in list(st.session_state.youtube_chats.keys()):

        col1, col2 = st.columns([4, 1])

        with col1:

            button_type = (
                "primary"
                if chat_name == st.session_state.current_youtube_chat
                else "secondary"
            )

            if st.button(
                f"📺 {chat_name}",
                key=f"yt_{chat_name}",
                use_container_width=True,
                type=button_type,
            ):

                st.session_state.current_youtube_chat = chat_name

                st.rerun()

        with col2:

            if st.button("🗑", key=f"delete_yt_{chat_name}", use_container_width=True):

                if len(st.session_state.youtube_chats) > 1:

                    del st.session_state.youtube_chats[chat_name]

                    st.session_state.current_youtube_chat = list(
                        st.session_state.youtube_chats.keys()
                    )[0]

                    st.rerun()

    st.divider()

    # PDF Chats

    st.subheader("📄 PDF Chats")

    if st.button("➕ New PDF Chat", use_container_width=True):

        new_chat = f"PDF Chat {len(st.session_state.pdf_chats)+1}"

        st.session_state.pdf_chats[new_chat] = []

        st.session_state.current_pdf_chat = new_chat

        st.rerun()

    # Display PDF Chats

    for chat_name in list(st.session_state.pdf_chats.keys()):

        col1, col2 = st.columns([4, 1])

        with col1:

            button_type = (
                "primary"
                if chat_name == st.session_state.current_pdf_chat
                else "secondary"
            )

            if st.button(
                f"📄 {chat_name}",
                key=f"pdf_{chat_name}",
                use_container_width=True,
                type=button_type,
            ):

                st.session_state.current_pdf_chat = chat_name

                st.rerun()

        with col2:

            if st.button("🗑", key=f"delete_pdf_{chat_name}", use_container_width=True):

                if len(st.session_state.pdf_chats) > 1:

                    del st.session_state.pdf_chats[chat_name]

                    st.session_state.current_pdf_chat = list(
                        st.session_state.pdf_chats.keys()
                    )[0]

                    st.rerun()

    st.divider()

    # Features

    st.markdown("### 🚀 Features")

    st.markdown("""
    ✅ YouTube RAG  
    ✅ PDF RAG  
    ✅ Gemini AI  
    ✅ FAISS Vector DB  
    ✅ MMR Retrieval  
    ✅ Multi Chat System  
    ✅ Conversational Memory  
    ✅ Retrieved Sources  
    """)

    st.divider()

    st.caption("Built with LangChain + Gemini + Streamlit")


# Main Title

st.title("🤖 AI Research Assistant")

st.caption("Ask questions from YouTube videos and PDFs using RAG")


# Tabs

tab1, tab2 = st.tabs(["📺 YouTube", "📄 PDF"])


video_url = None
pdf_file = None


# YouTube Tab

with tab1:

    video_url = st.text_input(
        "Paste YouTube URL", placeholder="https://youtube.com/watch?v=..."
    )


# PDF Tab

with tab2:

    pdf_file = st.file_uploader("Upload PDF", type=["pdf"])

    if pdf_file:

        st.success(f"✅ Uploaded: {pdf_file.name}")


# Determine Active Chat

if video_url:

    source_type = "youtube"

    current_messages = st.session_state.youtube_chats[
        st.session_state.current_youtube_chat
    ]

else:

    source_type = "pdf"

    current_messages = st.session_state.pdf_chats[st.session_state.current_pdf_chat]


# Display Old Messages

for message in current_messages:

    with st.chat_message(
        message["role"], avatar="👨‍💻" if message["role"] == "user" else "🤖"
    ):

        st.markdown(message["content"])


# Chat Input

query = st.chat_input("Ask your question...")


# Main Execution

if query:

    # YouTube Source

    if source_type == "youtube":

        video_id = extract_video_id(video_url)

        if video_id is None:

            st.error("❌ Invalid YouTube URL")

            st.stop()

        current_source = video_id

    # PDF Source

    else:

        if pdf_file is None:

            st.error("❌ Please upload PDF")

            st.stop()

        with open(pdf_file.name, "wb") as f:

            f.write(pdf_file.getbuffer())

        current_source = pdf_file.name

    # Store User Message

    if source_type == "youtube":

        st.session_state.youtube_chats[st.session_state.current_youtube_chat].append(
            {"role": "user", "content": query}
        )

        messages = st.session_state.youtube_chats[st.session_state.current_youtube_chat]

    else:

        st.session_state.pdf_chats[st.session_state.current_pdf_chat].append(
            {"role": "user", "content": query}
        )

        messages = st.session_state.pdf_chats[st.session_state.current_pdf_chat]

    # Chat Memory

    chat_history = ""

    for msg in messages:

        role = msg["role"]

        content = msg["content"]

        chat_history += f"{role}: {content}\n"

    # Show User Message

    with st.chat_message("user", avatar="👨‍💻"):

        st.markdown(query)

    # AI Response

    with st.chat_message("assistant", avatar="🤖"):

        progress = st.empty()

        progress.info("📥 Loading document...")

        progress.info("✂️ Chunking text...")

        progress.info("🧠 Creating embeddings...")

        progress.info("🔍 Retrieving context...")

        progress.info("🤖 Generating response...")

        # Get Response

        if source_type == "youtube":

            response, retrieved_docs = get_response(
                query, chat_history, video_id=video_id
            )

        else:

            response, retrieved_docs = get_response(
                query, chat_history, pdf_path=current_source
            )

        progress.empty()

        # Source Badge

        if source_type == "youtube":

            st.caption("📺 Source: YouTube")

        else:

            st.caption("📄 Source: PDF")

        # Response

        st.markdown(response)

        # Retrieved Sources

        with st.expander("📚 View Retrieved Sources"):

            for i, doc in enumerate(retrieved_docs):

                st.markdown(f"### Chunk {i+1}")

                st.write(doc.page_content)

    # Store AI Response

    if source_type == "youtube":

        st.session_state.youtube_chats[st.session_state.current_youtube_chat].append(
            {"role": "assistant", "content": response}
        )

    else:

        st.session_state.pdf_chats[st.session_state.current_pdf_chat].append(
            {"role": "assistant", "content": response}
        )
