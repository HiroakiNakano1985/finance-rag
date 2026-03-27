from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os

# DBの存在確認
if not os.path.exists("./chroma_db"):
    print("chroma_dbが見つかりません。先にbuild_db.pyを実行してください")
    exit()

# 既存DBを読み込む
print("DBを読み込み中...")
embeddings = SentenceTransformerEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
vectorstore = Chroma(embedding_function=embeddings, persist_directory="./chroma_db")

# LLMとチェーン構築
print("LLMを準備中...")
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

# 質問ループ
print("\n準備完了！質問してください（終了はquit）\n")
while True:
    question = input("質問: ")
    if question.lower() == "quit":
        break
    print("\n回答: ", end="", flush=True)
    for chunk in chain.stream(question):
        print(chunk, end="", flush=True)
    print("\n")