import re

import bleach

from .extensions import db
from .models import Category, Tag

ALLOWED_TAGS = ["p", "br", "strong", "em", "u", "s", "h1", "h2", "h3", "ul", "ol", "li",
                "blockquote", "pre", "code", "a"]
ALLOWED_ATTRS = {"a": ["href", "title"], "pre": ["class"]}


def clean_html(html):
    return bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS,
                        protocols=["http", "https", "mailto"], strip=True)


def plain_text(html):
    return re.sub(r"\s+", " ", bleach.clean(html or "", tags=[], strip=True)).strip()


def excerpt(html, length=170):
    text = plain_text(html)
    return text if len(text) <= length else text[:length].rsplit(" ", 1)[0] + "…"


def reading_time(html):
    return max(1, round(len(plain_text(html).split()) / 200))


def get_category(name):
    name = (name or "").strip()
    if not name:
        return None
    cat = Category.query.filter(db.func.lower(Category.name) == name.lower()).first()
    if not cat:
        cat = Category(name=name)
        db.session.add(cat)
    return cat


def get_tags(raw):
    names = []
    for part in (raw or "").split(","):
        part = part.strip().lower()[:30]
        if part and part not in names:
            names.append(part)
    tags = []
    for n in names[:8]:
        tag = Tag.query.filter_by(name=n).first()
        if not tag:
            tag = Tag(name=n)
            db.session.add(tag)
        tags.append(tag)
    return tags
