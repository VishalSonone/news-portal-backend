from enum import Enum as PyEnum

class RoleEnum(PyEnum):
    reader = "reader"
    author = "author"
    editor = "editor"
    admin = "admin"

class ArticleStatus(PyEnum):
    draft = "draft"
    published = "published"
    archived = "archived"

