from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
import os
import glob

# docs/フォルダのPDFを全部読み込む
print("PDFを読み込み中...")
pdf_files = glob.glob("docs/*.pdf")
if not pdf_files:
    print("docs/フォルダにPDFがありません")
    exit()

documents = []
for pdf_path in pdf_files:
    print(f"  読み込み中: {pdf_path}")
    loader = PyMuPDFLoader(pdf_path)
    documents.extend(loader.load())

print(f"合計{len(documents)}ページ読み込みました")

# チャンク分割
print("テキストを分割中...")
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(documents)
print(f"{len(chunks)}チャンクに分割しました")

# ベクトルDB構築
print("ベクトルDBを構築中...")
embeddings = SentenceTransformerEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_db")
print("完了！chroma_dbに保存しました")