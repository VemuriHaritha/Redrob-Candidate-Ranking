from datetime import date

CANDIDATES_PATH = "candidates.jsonl"
OUTPUT_PATH     = "submission.csv"
TOP_STAGE1      = 600
TODAY           = date(2026, 6, 25)

MUST_HAVE_GROUPS = {
    "embeddings_retrieval": [
        "embeddings", "embedding", "dense retrieval", "semantic search",
        "sentence transformers", "sentence-transformers", "bi-encoder",
        "cross-encoder", "bge", "e5 model", "openai embeddings",
        "text embeddings", "vector embeddings", "neural retrieval",
        "dense vectors", "approximate nearest neighbor", "ann",
    ],
    "vector_db_infra": [
        "faiss", "pinecone", "weaviate", "qdrant", "milvus", "pgvector",
        "chromadb", "annoy", "vector database", "vector store", "vector search",
        "vector index", "opensearch", "elasticsearch", "hybrid search",
        "approximate nearest", "hnsw",
    ],
    "python_engineering": [
        "python", "fastapi", "flask", "django", "sqlalchemy", "pydantic",
        "pytest", "asyncio", "celery", "redis", "production python",
    ],
    "nlp_ir_core": [
        "nlp", "natural language processing", "information retrieval",
        "bm25", "tf-idf", "tfidf", "text ranking", "text classification",
        "tokenization", "named entity", "ner", "text mining",
        "document retrieval", "question answering",
    ],
    "llm_transformers": [
        "llm", "large language model", "gpt", "llama", "mistral", "gemini",
        "transformer", "bert", "roberta", "t5", "rag",
        "retrieval augmented generation", "in-context learning",
        "prompt engineering", "instruction tuning", "hugging face",
        "huggingface", "langchain", "llamaindex",
    ],
    "ranking_evaluation": [
        "ranking", "reranking", "re-ranking", "learning to rank", "ltr",
        "ndcg", "mrr", "recall@k", "precision@k",
        "a/b test", "a/b testing", "offline evaluation", "online evaluation",
        "relevance judgments", "evaluation framework",
        "lambdarank", "listwise", "pairwise",
    ],
}

NICE_TO_HAVE_GROUPS = {
    "fine_tuning": [
        "fine-tuning", "fine tuning", "finetuning", "lora", "qlora", "peft",
        "rlhf", "sft", "supervised fine", "adapter", "parameter efficient",
    ],
    "learning_to_rank": [
        "xgboost", "lightgbm", "catboost", "gbdt", "gradient boosting",
        "lambdamart", "ranknet", "learning to rank",
    ],
    "mlops_infra": [
        "mlops", "mlflow", "kubeflow", "airflow", "kubernetes", "docker",
        "wandb", "weights & biases", "dvc", "model registry", "ci/cd",
        "bentoml", "triton", "ray serve", "torchserve",
    ],
    "dl_frameworks": [
        "pytorch", "tensorflow", "jax", "keras", "onnx",
        "accelerate", "deepspeed", "transformers library",
    ],
    "open_source_evidence": [
        "open source", "open-source", "github", "contributions", "maintainer",
        "arxiv", "paper", "published", "conference", "workshop",
    ],
    "hr_marketplace": [
        "hr tech", "hrtech", "recruiting", "recruitment", "talent", "ats",
        "marketplace", "recommendation system", "matching", "job matching",
        "candidate matching",
    ],
    "distributed_scale": [
        "distributed", "kafka", "spark", "flink", "stream processing",
        "large scale", "inference optimization", "throughput", "latency",
        "serving", "production ml", "scale",
    ],
}

RETRIEVAL_TITLE_KWS = [
    "search engineer", "ranking engineer", "recommendation",
    "retrieval", "relevance engineer", "nlp engineer",
    "applied ml", "applied scientist", "ml engineer",
    "machine learning engineer", "ai engineer", "research engineer",
    "data scientist",
]

BAD_TITLE_KWS = [
    "marketing manager", "hr manager", "operations manager",
    "content writer", "graphic designer", "business analyst",
    "accountant", "civil engineer", "mechanical engineer",
    "finance manager", "legal", "sales manager", "customer success",
    "ui designer", "product designer", "project manager",
    "seo", "brand manager", "recruiter",
]

CONSULTING_FIRMS = {
    "tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini",
    "hcl", "tech mahindra", "mphasis", "hexaware", "ltimindtree",
}

INDIA_PREFERRED = {
    "pune", "noida", "delhi", "gurgaon", "gurugram", "ncr",
    "hyderabad", "mumbai", "bengaluru", "bangalore",
}

AI_CERTS = {
    "aws machine learning", "google professional ml", "tensorflow developer",
    "pytorch", "deep learning", "nlp", "ai", "ml", "data science",
    "hugging face", "fastai", "coursera ml", "deeplearning.ai",
}

ROLE_RELEVANT_ASSESSMENTS = {
    "nlp", "information retrieval", "sentence transformers",
    "vector search", "semantic search", "learning to rank",
    "fine-tuning llms", "rag", "machine learning", "data science",
    "elasticsearch", "faiss", "qdrant", "milvus", "hugging face transformers",
    "recommendation systems", "mlops", "peft", "lora",
    "langchain", "llamaindex", "prompt engineering",
}

JD_TEXT = """
senior ai engineer machine learning nlp information retrieval embeddings vector search
semantic search python production ranking reranking evaluation ndcg mrr
sentence transformers bert transformers hugging face faiss pinecone qdrant weaviate
milvus elasticsearch opensearch vector database hybrid search
large language model llm rag retrieval augmented generation fine tuning lora peft
xgboost learning to rank a/b testing offline evaluation online evaluation
pytorch tensorflow mlops docker kubernetes startup product company
candidate matching job matching recommendation system talent intelligence
series a founding team engineer ship production deployment
""".lower()
