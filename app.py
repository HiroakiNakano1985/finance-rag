import streamlit as st
from langchain_chroma import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_ollama import OllamaLLM
from langchain_aws import ChatBedrock
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()

# ページ設定
st.set_page_config(
    page_title="Finance RAG",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Finance Document RAG")
st.caption("金融規制文書（金融庁・BIS・日銀）に基づいてAIが回答します")

# サイドバー：LLM切り替え
with st.sidebar:
    st.header("⚙️ 設定")
    llm_backend = st.radio(
        "LLMバックエンド",
        ["ローカル（Ollama）", "クラウド（AWS Bedrock）"],
        index=0
    )
    st.divider()
    st.header("📁 参照文書")
    st.markdown("""
    - 🏦 金融庁 主要行等向け監督指針
    - 🌐 BIS バーゼルIII
    - 🇯🇵 日本銀行 金融システムレポート
    """)
    st.divider()
    show_sources = st.toggle("参照チャンクを表示する", value=False)

# DBの存在確認
if not os.path.exists("./chroma_db"):
    st.error("chroma_dbが見つかりません。先にbuild_db.pyを実行してください")
    st.stop()

@st.cache_resource
def load_chain(backend):
    embeddings = SentenceTransformerEmbeddings(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )
    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )

    if backend == "クラウド（AWS Bedrock）":
        llm = ChatBedrock(
    model_id="us.meta.llama3-3-70b-instruct-v1:0",
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    model_kwargs={"max_tokens": 1000}
)
    else:
        llm = OllamaLLM(model="llama3.2:3b")

    prompt = ChatPromptTemplate.from_template("""
You are a financial regulation expert. Use the following context to answer the question.
The context may be in English. If so, answer in Japanese by translating the relevant parts.
If the context contains tables or numbers, extract and explain them clearly.
Even if the information is partial, provide what you can find.

Context:
{context}

Question: {question}

Answer in Japanese:
""")

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain, vectorstore

chain, vectorstore = load_chain(llm_backend)

# チャット履歴の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# バックエンド切り替え時にチャット履歴をリセット
if "current_backend" not in st.session_state:
    st.session_state.current_backend = llm_backend
if st.session_state.current_backend != llm_backend:
    st.session_state.messages = []
    st.session_state.current_backend = llm_backend

# チャット履歴を表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 質問入力
if question := st.chat_input("金融規制について質問してください..."):
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        with st.spinner("回答を生成中..."):
            response_placeholder = st.empty()
            full_response = ""

            full_response = chain.invoke(question)
            response_placeholder.markdown(full_response)

            if show_sources:
                docs = vectorstore.similarity_search(question, k=5)
                with st.expander("📄 参照した文書箇所"):
                    for i, doc in enumerate(docs):
                        st.caption(f"出典: {doc.metadata.get('source', 'unknown')}")
                        st.text(doc.page_content[:300])
                        if i < len(docs) - 1:
                            st.divider()

    st.session_state.messages.append({"role": "assistant", "content": full_response})