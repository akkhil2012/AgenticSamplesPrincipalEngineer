from src.config import Settings
from src.state.repository import Repository
from src.knowledge.retrieval import KnowledgeService


def main():
    settings = Settings()
    Repository(settings.database_url)
    for tenant in ["bank-a", "bank-b"]:
        assert len(KnowledgeService(settings.data_dir).retrieve(tenant)) == 4
    print("SQLite tables initialized; synthetic JSON fixtures and current policies validated.")


if __name__ == "__main__":
    main()
