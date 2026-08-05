import streamlit as st
import tempfile

from google import genai
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# ----------------------------
# Gemini Client
# ----------------------------
client = genai.Client(
    api_key=st.secrets["GOOGLE_API_KEY"]
)

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(
    page_title="AI PDF Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("📄 AI PDF Chatbot")
st.write("Upload a PDF and ask questions.")

# ----------------------------
# Upload PDF
# ----------------------------
uploaded_file = st.file_uploader(
    "Choose a PDF",
    type="pdf"
)

# ----------------------------
# Process PDF
# ----------------------------
if uploaded_file:

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    # Load PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    st.success(f"PDF Loaded Successfully ({len(documents)} Pages)")

    # ----------------------------
    # Split into Chunks
    # ----------------------------
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)

    st.write(f"Total Chunks: {len(chunks)}")

    # ----------------------------
    # Create Embeddings
    # ----------------------------
    with st.spinner("Creating embeddings..."):
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings
        )

    st.success("Embeddings Created Successfully")

    # ----------------------------
    # Ask Question
    # ----------------------------
    question = st.text_input("Ask your question")

    if st.button("Generate Answer"):

        if question.strip() == "":
            st.warning("Please enter a question.")
            st.stop()

        with st.spinner("Searching PDF..."):
            results = vector_store.similarity_search(
                question,
                k=2
            )

        context = ""

        st.subheader("Retrieved Chunks")

        for i, doc in enumerate(results):
            st.markdown(f"### Chunk {i+1}")
            st.write(doc.page_content)
            st.divider()

            context += doc.page_content + "\n"

        prompt = f"""
You are a helpful AI Assistant.

Answer ONLY from the context below.

If the answer is not available in the context, reply exactly:

I couldn't find that information in the PDF.

Context:
{context}

Question:
{question}

Answer:
"""

        with st.spinner("Generating Answer..."):

            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

        st.subheader("Gemini Answer")
        st.success(response.text)

       

