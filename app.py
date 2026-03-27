import streamlit as st
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os

# ページ設定
st.set_page_config(
    page_title="Finance RAG",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Finance Document RAG")
st.caption("金融規制文書（金融庁・BIS・日銀）に基づいてAIが回答します")

# DBの存在確認
if not os.path.exists("./chroma_db"):
    st.error("chroma_dbが見つかりません。先にbuild_db.pyを実行してください")
    st.stop()

# 初期化（キャッシュで毎回ロードしない）
@st.cache_resource
def load_chain():
    embeddings = SentenceTransformerEmbeddings(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )
    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )
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

chain, vectorstore = load_chain()

# サイドバー：参照文書の表示
with st.sidebar:
    st.header("📁 参照文書")
    st.markdown("""
    - 🏦 金融庁 主要行等向け監督指針
    - 🌐 BIS バーゼルIII
    - 🇯🇵 日本銀行 金融システムレポート
    """)
    st.divider()
    show_sources = st.toggle("参照チャンクを表示する", value=False)

# チャット履歴の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# チャット履歴を表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 質問入力
if question := st.chat_input("金融規制について質問してください..."):
    # ユーザーの質問を表示
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    # 回答を生成
    with st.chat_message("assistant"):
        with st.spinner("回答を生成中..."):
            # ストリーミング表示
            response_placeholder = st.empty()
            full_response = ""
            
            for chunk in chain.stream(question):
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            
            # 参照チャンクの表示
            if show_sources:
                docs = vectorstore.similarity_search(question, k=5)
                with st.expander("📄 参照した文書箇所"):
                    for i, doc in enumerate(docs):
                        st.caption(f"出典: {doc.metadata.get('source', 'unknown')}")
                        st.text(doc.page_content[:300])
                        if i < len(docs) - 1:
                            st.divider()
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})