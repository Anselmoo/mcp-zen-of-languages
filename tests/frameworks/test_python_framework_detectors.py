from __future__ import annotations

import pytest

from mcp_zen_of_languages.analyzers.analyzer_factory import create_analyzer
from mcp_zen_of_languages.frameworks.django.rules import DJANGO_ZEN
from mcp_zen_of_languages.frameworks.fastapi.rules import FASTAPI_ZEN
from mcp_zen_of_languages.frameworks.pydantic.rules import PYDANTIC_ZEN
from mcp_zen_of_languages.frameworks.sqlalchemy.rules import SQLALCHEMY_ZEN


def _principle_lookup(*zens) -> dict[str, str]:
    return {
        principle.id: principle.principle
        for zen in zens
        for principle in zen.principles
    }


PRINCIPLES = _principle_lookup(
    PYDANTIC_ZEN,
    FASTAPI_ZEN,
    DJANGO_ZEN,
    SQLALCHEMY_ZEN,
)


@pytest.mark.parametrize(
    ("rule_id", "bad_code", "good_code"),
    [
        (
            "pydantic-001",
            """
from pydantic import BaseModel


class User(BaseModel):
    name: str


user = User(name="Ada")
payload = user.dict()
""",
            """
from pydantic import BaseModel


class User(BaseModel):
    name: str


user = User(name="Ada")
payload = user.model_dump()
""",
        ),
        (
            "pydantic-002",
            """
from pydantic import BaseModel


class User(BaseModel):
    name: str


user = User.parse_obj({"name": "Ada"})
""",
            """
from pydantic import BaseModel


class User(BaseModel):
    name: str


user = User.model_validate({"name": "Ada"})
""",
        ),
        (
            "pydantic-003",
            """
from pydantic import BaseModel


class User(BaseModel):
    tags: list[str] = []
""",
            """
from pydantic import BaseModel
from pydantic import Field


class User(BaseModel):
    tags: list[str] = Field(default_factory=list)
""",
        ),
        (
            "pydantic-004",
            """
from pydantic import BaseModel


class User(BaseModel):
    class Config:
        frozen = True
""",
            """
from pydantic import BaseModel
from pydantic import ConfigDict


class User(BaseModel):
    model_config = ConfigDict(frozen=True)
""",
        ),
        (
            "pydantic-005",
            """
from pydantic import BaseModel
from pydantic import validator


class User(BaseModel):
    name: str

    @validator("name")
    def normalize_name(cls, value: str) -> str:
        return value.strip()
""",
            """
from pydantic import BaseModel
from pydantic import field_validator


class User(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip()
""",
        ),
        (
            "pydantic-006",
            """
from pydantic import BaseModel


class User(BaseModel):
    name: str


field_names = User.__fields__.keys()
""",
            """
from pydantic import BaseModel


class User(BaseModel):
    name: str


field_names = User.model_fields.keys()
""",
        ),
        (
            "pydantic-007",
            """
from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    nickname: Optional[str] = None
""",
            """
from pydantic import BaseModel


class User(BaseModel):
    nickname: str | None = None
""",
        ),
        (
            "pydantic-008",
            """
from pydantic import BaseModel


class User(BaseModel):
    class Config:
        orm_mode = True
""",
            """
from pydantic import BaseModel
from pydantic import ConfigDict


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
""",
        ),
    ],
)
def test_pydantic_framework_rules_detect_and_ignore_expected_cases(
    rule_id: str,
    bad_code: str,
    good_code: str,
) -> None:
    analyzer = create_analyzer("pydantic")
    principle = PRINCIPLES[rule_id]

    assert principle in {
        violation.principle for violation in analyzer.analyze(bad_code).violations
    }
    assert principle not in {
        violation.principle for violation in analyzer.analyze(good_code).violations
    }


@pytest.mark.parametrize(
    ("rule_id", "bad_code", "good_code"),
    [
        (
            "fastapi-001",
            """
from fastapi import APIRouter

router = APIRouter()


@router.get("/users/{user_id}")
async def read_user(user_id: int):
    return {"id": user_id}
""",
            """
from fastapi import APIRouter

router = APIRouter()


@router.get("/users/{user_id}", response_model=dict)
async def read_user(user_id: int):
    return {"id": user_id}
""",
        ),
        (
            "fastapi-002",
            """
from fastapi import FastAPI

app = FastAPI()


@app.post("/users", response_model=dict)
def create_user():
    return {"ok": True}
""",
            """
from fastapi import FastAPI

app = FastAPI()


@app.post("/users", response_model=dict, status_code=201)
def create_user():
    return {"ok": True}
""",
        ),
        (
            "fastapi-003",
            """
from fastapi import FastAPI

app = FastAPI()


@app.get("/boom", response_model=dict)
def boom():
    raise Exception("boom")
""",
            """
from fastapi import FastAPI
from fastapi import HTTPException

app = FastAPI()


@app.get("/boom", response_model=dict)
def boom():
    raise HTTPException(status_code=400, detail="boom")
""",
        ),
        (
            "fastapi-004",
            """
import threading

from fastapi import FastAPI

app = FastAPI()


@app.post("/jobs", response_model=dict, status_code=202)
def create_job():
    threading.Thread(target=print, args=("job",)).start()
    return {"queued": True}
""",
            """
from fastapi import BackgroundTasks
from fastapi import FastAPI

app = FastAPI()


@app.post("/jobs", response_model=dict, status_code=202)
def create_job(background_tasks: BackgroundTasks):
    background_tasks.add_task(print, "job")
    return {"queued": True}
""",
        ),
        (
            "fastapi-005",
            """
import requests

from fastapi import FastAPI

app = FastAPI()


@app.get("/external", response_model=dict)
async def external():
    response = requests.get("https://example.com")
    return response.json()
""",
            """
import httpx

from fastapi import FastAPI

app = FastAPI()


@app.get("/external", response_model=dict)
async def external():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://example.com")
    return response.json()
""",
        ),
        (
            "fastapi-006",
            """
from fastapi import FastAPI

app = FastAPI()


@app.route("/users", methods=["GET"])
def read_users():
    return {"ok": True}
""",
            """
from fastapi import FastAPI

app = FastAPI()


@app.get("/users", response_model=dict)
def read_users():
    return {"ok": True}
""",
        ),
    ],
)
def test_fastapi_framework_rules_detect_and_ignore_expected_cases(
    rule_id: str,
    bad_code: str,
    good_code: str,
) -> None:
    analyzer = create_analyzer("fastapi")
    principle = PRINCIPLES[rule_id]

    assert principle in {
        violation.principle for violation in analyzer.analyze(bad_code).violations
    }
    assert principle not in {
        violation.principle for violation in analyzer.analyze(good_code).violations
    }


@pytest.mark.parametrize(
    ("rule_id", "bad_code", "good_code"),
    [
        (
            "django-001",
            """
def load_user(cursor, user_id: int):
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
""",
            """
def load_user(cursor, user_id: int):
    cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])
""",
        ),
        (
            "django-002",
            """
SECRET_KEY = "hardcoded"
""",
            """
import os

SECRET_KEY = os.getenv("SECRET_KEY")
""",
        ),
        (
            "django-003",
            """
DEBUG = True
""",
            """
# DEBUG = True
DEBUG = False
""",
        ),
        (
            "django-004",
            """
from django.shortcuts import redirect


def dashboard():
    return redirect("/dashboard/")
""",
            """
from django.shortcuts import redirect


def dashboard():
    return redirect("dashboard")
""",
        ),
        (
            "django-005",
            """
from django.db.models.signals import post_save


post_save.connect(sync_profile, sender=User)
""",
            """
def create_profile(user):
    return {"user_id": user.id}
""",
        ),
        (
            "django-006",
            """
def render_posts():
    for post in Post.objects.all():
        print(post.author.name)
""",
            """
def render_posts():
    for post in Post.objects.select_related("author").all():
        print(post.author.name)
""",
        ),
    ],
)
def test_django_framework_rules_detect_and_ignore_expected_cases(
    rule_id: str,
    bad_code: str,
    good_code: str,
) -> None:
    analyzer = create_analyzer("django")
    principle = PRINCIPLES[rule_id]

    assert principle in {
        violation.principle for violation in analyzer.analyze(bad_code).violations
    }
    assert principle not in {
        violation.principle for violation in analyzer.analyze(good_code).violations
    }


@pytest.mark.parametrize(
    ("rule_id", "bad_code", "good_code"),
    [
        (
            "sqlalchemy-001",
            """
from sqlalchemy import text


def find_user(user_id: int):
    return text(f"select * from users where id = {user_id}")
""",
            """
from sqlalchemy import text


def find_user(user_id: int):
    return text("select * from users where id = :user_id")
""",
        ),
        (
            "sqlalchemy-002",
            """
def load_user(Session):
    session = Session()
    return session
""",
            """
def load_user(Session, stmt):
    with Session() as session:
        return session.execute(stmt)
""",
        ),
        (
            "sqlalchemy-003",
            """
from sqlalchemy import Column
from sqlalchemy import Integer


class User:
    id = Column(Integer, primary_key=True)
""",
            """
from sqlalchemy import Integer
from sqlalchemy.orm import mapped_column


class User:
    id = mapped_column(Integer, primary_key=True)
""",
        ),
        (
            "sqlalchemy-004",
            """
from sqlalchemy.orm import declarative_base


Base = declarative_base()
""",
            """
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
""",
        ),
        (
            "sqlalchemy-005",
            """
from sqlalchemy.orm import relationship


class User:
    items = relationship("Item")
""",
            """
from sqlalchemy.orm import relationship


class User:
    items = relationship("Item", lazy="selectin")
""",
        ),
        (
            "sqlalchemy-006",
            """
def persist_rows(session, rows, Model):
    for row in rows:
        session.add(Model(name=row["name"]))
""",
            """
from sqlalchemy import insert


def persist_rows(session, rows, Model):
    session.execute(insert(Model), rows)
""",
        ),
    ],
)
def test_sqlalchemy_framework_rules_detect_and_ignore_expected_cases(
    rule_id: str,
    bad_code: str,
    good_code: str,
) -> None:
    analyzer = create_analyzer("sqlalchemy")
    principle = PRINCIPLES[rule_id]

    assert principle in {
        violation.principle for violation in analyzer.analyze(bad_code).violations
    }
    assert principle not in {
        violation.principle for violation in analyzer.analyze(good_code).violations
    }
