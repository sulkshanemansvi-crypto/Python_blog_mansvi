from flask import abort, current_app, render_template, request

from ..models import Category, Post, Tag, User
from . import bp


def filtered_posts(base=None):
    q = (request.args.get("q") or "").strip()
    cat = request.args.get("category", type=int)
    tag = request.args.get("tag", type=int)
    query = base if base is not None else Post.query
    if q:
        like = f"%{q}%"
        query = query.filter(Post.title.ilike(like) | Post.body.ilike(like))
    if cat:
        query = query.filter(Post.category_id == cat)
    if tag:
        query = query.filter(Post.tags.any(Tag.id == tag))
    page = request.args.get("page", 1, type=int)
    return query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False)


@bp.route("/")
def index():
    pagination = filtered_posts()
    return render_template(
        "index.html", pagination=pagination, posts=pagination.items,
        categories=Category.query.order_by(Category.name).all(),
        tags=Tag.query.order_by(Tag.name).all(),
        q=request.args.get("q", ""), cat=request.args.get("category", type=int),
        tag=request.args.get("tag", type=int))


@bp.route("/user/<username>")
def profile(username):
    user = User.query.filter(User.username.ilike(username)).first()
    if not user:
        abort(404)
    page = request.args.get("page", 1, type=int)
    pagination = user.posts.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False)
    return render_template("profile.html", user=user, pagination=pagination,
                           posts=pagination.items, title=user.username)
