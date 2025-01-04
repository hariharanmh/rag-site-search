from enum import Enum

rag_engine = dict(
    name = "RAG",
    description = "Operations with RAG",
)

class Tags(Enum):
    RAG_ENGINE = "RAG"

    @classmethod
    def get_router_prefix(cls, tag):
        if not isinstance(tag, cls) or tag.name not in cls._member_names_:
            raise ValueError(f"Invalid tag: {tag}")

        return f"/{tag.name.lower()}"