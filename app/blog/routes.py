from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..forms import CommentForm, PostForm
from ..models import Category, Comment, Post, Tag
from ..utils import clean_html, get_category, get_tags, plain_text
from . import bp


def _body_ok(form):
    form.body.data = clean_html(form.body.data or "")
    if not plain_text(form.body.data):
        form.body.errors = list(form.body.errors) + ["Your story can't be empty."]
        return False
    return True


@bp.route("/post/new", methods=["GET", "POST"])
@login_required
def create():
    form = PostForm()
    if form.validate_on_submit() and _body_ok(form):
        post = Post(title=form.title.data.strip(), body=form.body.data, author=current_user,
                    category=get_category(form.category.data), tags=get_tags(form.tags.data))
        db.session.add(post)
        db.session.commit()
        flash("Your story is live ✿", "success")
        return redirect(url_for("blog.detail", post_id=post.id))
    return render_template("blog/form.html", form=form, title="New story", heading="Write a new story",
                           categories=Category.query.order_by(Category.name).all())


@bp.route("/post/<int:post_id>")
def detail(post_id):
    post = db.get_or_404(Post, post_id)
    return render_template("blog/detail.html", post=post, form=CommentForm(), title=post.title,
                           comments=post.comments.all())


@bp.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit(post_id):
    post = db.get_or_404(Post, post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if request.method == "GET":
        form.title.data = post.title
        form.body.data = post.body
        form.category.data = post.category.name if post.category else ""
        form.tags.data = ", ".join(t.name for t in post.tags)
    elif form.validate_on_submit() and _body_ok(form):
        post.title = form.title.data.strip()
        post.body = form.body.data
        post.category = get_category(form.category.data)
        post.tags = get_tags(form.tags.data)
        db.session.commit()
        flash("Story updated.", "success")
        return redirect(url_for("blog.detail", post_id=post.id))
    return render_template("blog/form.html", form=form, title="Edit story", heading="Edit your story",
                           categories=Category.query.order_by(Category.name).all())


@bp.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete(post_id):
    post = db.get_or_404(Post, post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Story deleted.", "info")
    return redirect(url_for("main.index"))


@bp.route("/post/<int:post_id>/comment", methods=["POST"])
@login_required
def comment(post_id):
    post = db.get_or_404(Post, post_id)
    form = CommentForm()
    if form.validate_on_submit():
        db.session.add(Comment(body=form.body.data.strip(), author=current_user, post=post))
        db.session.commit()
        flash("Comment added.", "success")
    else:
        flash("Comment can't be empty or longer than 1000 characters.", "danger")
    return redirect(url_for("blog.detail", post_id=post.id) + "#comments")


@bp.route("/comment/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment(comment_id):
    c = db.get_or_404(Comment, comment_id)
    if c.author != current_user and c.post.author != current_user:
        abort(403)
    pid = c.post_id
    db.session.delete(c)
    db.session.commit()
    flash("Comment removed.", "info")
    return redirect(url_for("blog.detail", post_id=pid) + "#comments")
