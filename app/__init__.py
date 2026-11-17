import os

import click
from flask import Flask, render_template

from config import Config

from .extensions import db, login_manager, migrate
from .utils import excerpt, reading_time

BANNER = """
  ╔══════════════════════════════════════════╗
  ║                                          ║
  ║     ✿   M A N S V I   B L O G   ✿        ║
  ║      stories • ideas • little thoughts   ║
  ║                                          ║
  ╚══════════════════════════════════════════╝
"""


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    os.makedirs(os.path.join(app.root_path, "..", "instance"), exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from .auth import bp as auth_bp
    from .blog import bp as blog_bp
    from .main import bp as main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(blog_bp)

    app.jinja_env.filters["excerpt"] = excerpt
    app.jinja_env.filters["reading_time"] = reading_time

    @app.context_processor
    def inject_site():
        return {"site_name": app.config["SITE_NAME"], "site_tagline": app.config["SITE_TAGLINE"]}

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    register_cli(app)

    if not app.testing and os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        click.secho(BANNER, fg="magenta", bold=True)
        click.secho("  ✿ Mansvi Blog is starting — made with love by Mansvi ✿\n", fg="cyan", bold=True)
    return app


def register_cli(app):
    @app.cli.command("seed")
    def seed():
        """Create a demo user (mansvi / mansvi123) with sample posts."""
        from .models import Comment, Post, User
        from .utils import get_category, get_tags

        if User.query.filter_by(username="mansvi").first():
            click.echo("Demo data already exists.")
            return
        user = User(username="mansvi", email="mansvi@example.com",
                    bio="Writer, dreamer and chai enthusiast. Welcome to my corner of the internet ✿")
        user.set_password("mansvi123")
        db.session.add(user)
        samples = [
            ("Welcome to Mansvi", "Life", "welcome, hello",
             "<p>Hello and welcome! This is my little corner of the internet where I share <strong>stories</strong>, ideas and small everyday thoughts.</p><p>Grab a cup of chai and stay a while.</p>"),
            ("Why I Love Rainy Mornings", "Life", "rain, mornings",
             "<p>There is something magical about waking up to the sound of rain on the window.</p><blockquote>Rain is poetry the sky writes for us.</blockquote><p>It makes everything slow down.</p>"),
            ("Learning Flask, One Blueprint at a Time", "Tech", "flask, python",
             "<p>Flask is small, friendly and powerful. Blueprints let you split your app into neat pieces.</p><ul><li>Auth</li><li>Blog</li><li>Profiles</li></ul>"),
            ("Five Books That Changed Me", "Books", "reading, books",
             "<p>Books are quiet friends. Here are five that stayed with me long after the last page.</p>"),
            ("A Simple Masala Chai Recipe", "Food", "chai, recipe",
             "<p>Crush ginger and cardamom, boil with water, add tea leaves, then milk. Simmer. Sip happily.</p>"),
            ("Notes on Slow Living", "Life", "mindfulness",
             "<p>Slow living is not about doing less; it is about doing things with <em>intention</em>.</p>"),
            ("Debugging With a Calm Mind", "Tech", "python, debugging",
             "<p>When the bug refuses to leave, take a walk. The answer is often waiting outside the editor.</p>"),
            ("Travel Diaries: The Hills", "Travel", "travel, hills",
             "<p>Mist, pine trees and winding roads: the hills always feel like home.</p>"),
        ]
        for title, cat, tags, body in samples:
            p = Post(title=title, body=body, author=user, category=get_category(cat), tags=get_tags(tags))
            db.session.add(p)
        db.session.flush()
        db.session.add(Comment(body="Lovely start! Looking forward to more.", author=user, post=Post.query.first()))
        db.session.commit()
        click.secho("Seeded! Login: mansvi / mansvi123", fg="green")
