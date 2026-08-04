


# ------------------------------------
# Streamlit UI
# ------------------------------------

st.set_page_config(
    page_title="AI PDF Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("📄 AI PDF Chatbot")
st.write("Upload a PDF and ask questions.")

# ------------------------------------
# Upload PDF
# ------------------------------------

uploaded_file = st.file_uploader(
    "Choose a PDF",
    type="pdf"
)

# ------------------------------------
# Process PDF
# ------------------------------------

if uploaded_file:

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:

        tmp.write(uploaded_file.read())

        pdf_path = tmp.name

    loader = PyPDFLoader(pdf_path)

    documents = loader.load()

    st.success(f"PDF Loaded Successfully ({len(documents)} Pages)")

    # ------------------------------------
    # Split into Chunks
    # ------------------------------------

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=500,

        chunk_overlap=100

    )

    chunks = splitter.split_documents(documents)

    st.write("Total Chunks:", len(chunks))

    # ------------------------------------
    # Embeddings
    # ------------------------------------

    embeddings = HuggingFaceEmbeddings(

        model_name="sentence-transformers/all-MiniLM-L6-v2"

    )

    # ------------------------------------
    # ChromaDB
    # ------------------------------------

    vector_store = Chroma.from_documents(

        documents=chunks,

        embedding=embeddings

    )

    st.success("Embeddings Created Successfully")

    # ------------------------------------
    # Ask Question
    # ------------------------------------

    question = st.text_input("Ask your question")

    if st.button("Generate Answer"):

        with st.spinner("Searching PDF..."):

            results = vector_store.similarity_search(

                question,

                k=2

            )

        context = ""

        st.subheader("Retrieved Chunks")

        for i, doc in enumerate(results):

            st.write(f"### Chunk {i+1}")

            st.write(doc.page_content)

            st.divider()

            context += doc.page_content + "\n"

        # ------------------------------------
        # Gemini
        # ------------------------------------

    

        llm = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=prompt
)


prompt = f"""
You are a helpful AI Assistant.

Answer ONLY from the context below.

If the answer is not available, say:

I couldn't find that information in the PDF

Context:

{context}

Question:

{question}

Answer:
"""

with st.spinner("Generating Answer..."):

    response = client.models.generate_content(
           model="gemini-2.5-flash",
           contents=prompt
    )

st.subheader("Gemini Answer")

st.success(response.text)
       
