# 📊 Finance RAG — Local LLM × Financial Regulation Documents

> **日本語** | [English](#english)

---

## 日本語

### 概要

金融規制文書（金融庁監督指針・BISバーゼルIII・日銀金融システムレポート）に対して、**ローカルLLM（Llama3.2）またはAWS Bedrock（Llama3.3 70B）** を使ってRAG（検索拡張生成）で質問応答するシステムです。

**機密情報を外部APIに送信せず、完全ローカルで動作する**ことが最大の特徴です。AWS Bedrockを使用する場合も、文書・ベクトルDBはローカルに保持したまま、推論のみクラウドで処理します。

### なぜローカルLLM／Bedrockか？

金融機関では社内文書・規制文書を外部サービス（OpenAI等）に送信することはコンプライアンス上困難です。本システムは2つのバックエンドを選択可能にすることで、セキュリティ要件に応じた柔軟な運用を実現しています。

| バックエンド | データの場所 | 速度 | コスト | 用途 |
|---|---|---|---|---|
| ローカル（Ollama） | 完全ローカル | 低速 | 無料 | 機密性最優先 |
| AWS Bedrock | AWS内に閉じる | 高速 | 従量課金 | 実務・デモ用途 |

### アーキテクチャ

```
ユーザー（ブラウザ）
    ↓
Streamlit UI
    ↓
ChromaDB（ローカル）← 文書・ベクトルDBは常にローカル
    ↓
LLM（切り替え可能）
    ├── Ollama（ローカル）: 完全オフライン
    └── AWS Bedrock（クラウド）: AWS内に閉じた推論
```

### 技術スタック

| コンポーネント | 技術 |
|---|---|
| LLM（ローカル） | Llama 3.2 3B（Ollama） |
| LLM（クラウド） | Llama 3.3 70B（AWS Bedrock） |
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
pip install langchain langchain-community langchain-ollama langchain-aws langchain-chroma langchain-text-splitters chromadb pymupdf streamlit sentence-transformers boto3 python-dotenv
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

#### 4. AWS Bedrockを使う場合（オプション）

`.env` ファイルを作成：

```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
```

#### 5. ベクトルDBの構築

```bash
python build_db.py
```

#### 6. アプリの起動

```bash
streamlit run app.py
```

サイドバーからローカル／Bedrockを切り替え可能です。

### ファイル構成

```
finance-rag/
├── app.py          # StreamlitのUI（ローカル／Bedrock切り替え対応）
├── build_db.py     # ベクトルDB構築スクリプト
├── rag.py          # CLIで動作するRAG
├── check_db.py     # DBの中身確認用
├── .env            # AWS認証情報（gitignore済み）
├── .gitignore
└── README.md
```

### 今後の拡張予定

- [ ] EC2へのデプロイ（完全クラウド化）
- [ ] 文書の自動更新機能
- [ ] 回答の根拠ページ数表示
- [ ] EDINETの有価証券報告書への対応

---

## English

### Overview

A **Retrieval-Augmented Generation (RAG)** system for financial regulation documents (FSA Supervisory Guidelines, BIS Basel III, BOJ Financial System Report) powered by a **local LLM (Llama3.2) or AWS Bedrock (Llama3.3 70B)**.

The key feature is that **documents and vector DB always remain local** — only inference is optionally offloaded to AWS Bedrock, keeping sensitive data within a controlled environment.

### Why Local LLM / Bedrock?

In financial institutions, sending internal or regulatory documents to external services (e.g. OpenAI) raises serious compliance concerns. This system supports two backends to balance security and performance:

| Backend | Data Location | Speed | Cost | Use Case |
|---|---|---|---|---|
| Local (Ollama) | Fully local | Slow | Free | Maximum confidentiality |
| AWS Bedrock | Within AWS | Fast | Pay-per-use | Production / Demo |

### Architecture

```
User (Browser)
    ↓
Streamlit UI
    ↓
ChromaDB (Local) ← Documents & vectors always stay local
    ↓
LLM (Switchable)
    ├── Ollama (Local): Fully offline
    └── AWS Bedrock (Cloud): Inference within AWS
```

### Tech Stack

| Component | Technology |
|---|---|
| LLM (Local) | Llama 3.2 3B (Ollama) |
| LLM (Cloud) | Llama 3.3 70B (AWS Bedrock) |
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
pip install langchain langchain-community langchain-ollama langchain-aws langchain-chroma langchain-text-splitters chromadb pymupdf streamlit sentence-transformers boto3 python-dotenv
```

#### 3. Download documents

```bash
mkdir docs
curl -L "https://www.fsa.go.jp/common/law/guide/city.pdf" -o docs/fsa_supervisory.pdf
curl -L "https://www.bis.org/bcbs/publ/d424.pdf" -o docs/basel3.pdf
curl -L "https://www.boj.or.jp/research/brp/fsr/data/fsr241024a.pdf" -o docs/boj_fsr.pdf
```

#### 4. AWS Bedrock setup (optional)

Create a `.env` file:

```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
```

#### 5. Build vector DB

```bash
python build_db.py
```

#### 6. Run the app

```bash
streamlit run app.py
```

Switch between Local and Bedrock backends from the sidebar.

### File Structure

```
finance-rag/
├── app.py          # Streamlit UI (Local / Bedrock switchable)
├── build_db.py     # Vector DB builder
├── rag.py          # CLI-based RAG
├── check_db.py     # DB inspection tool
├── .env            # AWS credentials (gitignored)
├── .gitignore
└── README.md
```

### Roadmap

- [ ] EC2 deployment (full cloud setup)
- [ ] Automatic document update pipeline
- [ ] Source page number display in answers
- [ ] EDINET financial statement integration
