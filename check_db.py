from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

embeddings = SentenceTransformerEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
vectorstore = Chroma(embedding_function=embeddings, persist_directory="./chroma_db")

# 検索テスト
results = vectorstore.similarity_search("corporate bonds risk weight standarized approach", k=10)

print(f"ヒット数: {len(results)}\n")
for i, doc in enumerate(results):
    print(f"--- チャンク{i+1} ---")
    print(f"ファイル: {doc.metadata.get('source', 'unknown')}")
    print(f"内容: {doc.page_content[:500]}")
    print()