# 📊 Finance RAG — Local LLM × Financial Regulation Documents

> **日本語** | [English](#english)

---

## 日本語

### 概要

金融規制文書（金融庁監督指針・BISバーゼルIII・日銀金融システムレポート）に対して、**ローカルLLM（Llama3.2）** を使ってRAG（検索拡張生成）で質問応答するシステムです。

**機密情報を外部APIに送信せず、完全ローカルで動作する**ことが最大の特徴です。

### なぜローカルLLMか？

金融機関では社内文書・規制文書を外部サービス（OpenAI等）に送信することはコンプライアンス上困難です。本システムはOllamaを使いすべての推論をローカルで完結させることで、**機密情報を守りながらAIを活用**できる設計になっています。

### 技術スタック

| コンポーネント | 技術 |
|---|---|
| LLM | Llama 3.2 3B（Ollama） |
| RAGフレームワーク | LangChain |
| ベクトルDB | ChromaDB |
| 埋め込みモデル | paraphrase-multilingual-MiniLM-L12-v2 |
| UI | Streamlit |

### セットアップ

#### 1. Ollamaのインストールとモデルのダウンロード

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2:3b
```

#### 2. 依存ライブラリのインストール

```bash
pip install langchain langchain-community langchain-ollama langchain-text-splitters chromadb pymupdf streamlit sentence-transformers
```

#### 3. 文書の準備

```bash
mkdir docs
# 金融庁 監督指針
curl -L "https://www.fsa.go.jp/common/law/guide/city.pdf" -o docs/fsa_supervisory.pdf
# BIS バーゼルIII
curl -L "https://www.bis.org/bcbs/publ/d424.pdf" -o docs/basel3.pdf
# 日銀 金融システムレポート
curl -L "https://www.boj.or.jp/research/brp/fsr/data/fsr241024a.pdf" -o docs/boj_fsr.pdf
```

#### 4. ベクトルDBの構築

```bash
python build_db.py
```

#### 5. アプリの起動

```bash
streamlit run app.py
```

### ファイル構成

```
finance-rag/
├── app.py          # StreamlitのUI
├── build_db.py     # ベクトルDB構築スクリプト
├── rag.py          # CLIで動作するRAG
├── check_db.py     # DBの中身確認用
├── .gitignore
└── README.md
```

### 今後の拡張予定

- [ ] AWS BedrockへのLLM切り替え対応
- [ ] 文書の自動更新機能
- [ ] 回答の根拠ページ数表示
- [ ] EDINETの有価証券報告書への対応

---

## English

### Overview

A **Retrieval-Augmented Generation (RAG)** system for financial regulation documents (FSA Supervisory Guidelines, BIS Basel III, BOJ Financial System Report) powered by a **local LLM (Llama3.2)**.

The key feature is that **all inference runs locally — no data is sent to external APIs.**

### Why Local LLM?

In financial institutions, sending internal or regulatory documents to external services (e.g. OpenAI) raises serious compliance concerns. This system uses Ollama to run all inference locally, enabling **AI-powered document QA while keeping sensitive data secure.**

### Tech Stack

| Component | Technology |
|---|---|
| LLM | Llama 3.2 3B (Ollama) |
| RAG Framework | LangChain |
| Vector DB | ChromaDB |
| Embedding Model | paraphrase-multilingual-MiniLM-L12-v2 |
| UI | Streamlit |

### Setup

#### 1. Install Ollama and pull model

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2:3b
```

#### 2. Install dependencies

```bash
pip install langchain langchain-community langchain-ollama langchain-text-splitters chromadb pymupdf streamlit sentence-transformers
```

#### 3. Download documents

```bash
mkdir docs
curl -L "https://www.fsa.go.jp/common/law/guide/city.pdf" -o docs/fsa_supervisory.pdf
curl -L "https://www.bis.org/bcbs/publ/d424.pdf" -o docs/basel3.pdf
curl -L "https://www.boj.or.jp/research/brp/fsr/data/fsr241024a.pdf" -o docs/boj_fsr.pdf
```

#### 4. Build vector DB

```bash
python build_db.py
```

#### 5. Run the app

```bash
streamlit run app.py
```

### File Structure

```
finance-rag/
├── app.py          # Streamlit UI
├── build_db.py     # Vector DB builder
├── rag.py          # CLI-based RAG
├── check_db.py     # DB inspection tool
├── .gitignore
└── README.md
```

### Roadmap

- [ ] AWS Bedrock LLM backend support
- [ ] Automatic document update pipeline
- [ ] Source page number display in answers
- [ ] EDINET financial statement integration
