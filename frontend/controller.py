#Author: Vodohleb04
import os
from datetime import date
from logging import getLogger
from hashlib import sha256
from flask import render_template, request, redirect, Flask, url_for, session

from backend.service_layer.authentication_service.authentication_service_impl import (
    LoginUserDTO, SaveUserDTO, AuthorizationToken
)
from backend.service_layer.discussion_service.discussion_service_impl import SaveCommentDTO, SaveDiscussionDTO
from backend.service_layer.knowledge_service.knowledge_service_impl import SaveKnowledgeDTO, KnowledgeStatus

from broker.authentication_tasks import AuthenticationTasks
from broker.discussion_tasks import DiscussionTasks
from broker.knowledge_tasks import KnowledgeTasks


LOGIN_MAXLENGTH = 50
PASSWORD_MAXLENGTH = 100
ALL_CATEGORIES_ITEM = "Все категории"


logger = getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(128)

    # General
    @app.get('/')
    def redirect_to_main():
        return redirect(url_for('render_main_page'))

    @app.get('/main/')
    def render_main_page():
        return render_template(
            "general/main_page_index.html",
            about_us_url=url_for("render_about_us_page"),
            registration_url=url_for("render_registration_page"),
            guest_url=url_for("render_user_main_page"),
            login_url=url_for("render_login_page")
        )

    @app.get('/main/about_us')
    def render_about_us_page():
        return render_template("general/about_us_index.html")

    @app.get('/main/registration')
    def render_registration_page():
        return render_template(
            "general/registration_index.html",
            login_maxlength=LOGIN_MAXLENGTH,
            password_maxlength=PASSWORD_MAXLENGTH,
            username_maxlength=LOGIN_MAXLENGTH,
            post_registration_url=url_for("registrate"),
            login_url=url_for("render_login_page")
        )

    def registrate_post_form_parser():
        birthdate = request.form.get('birthdate')
        if birthdate is None:
            raise ValueError('birthdate is required')
        else:
            birthdate = date.fromisoformat(birthdate)
        tech_stack = request.form.get('tech_stack', None)
        if tech_stack is not None and tech_stack.replace(" ", "") == "":
            tech_stack = None
        email = request.form.get('email', None)
        if email is None or email.replace(" ", "") == "":
            raise ValueError('email is required')
        username = request.form.get('username', None)
        if username is None or username.replace(" ", "") == "":
            raise ValueError('username must be fulfilled')
        login = request.form.get('login', None).strip(" ")
        password = request.form.get('password')
        password_repeat = request.form.get('password_repeat')
        if not (login.replace(" ", "") and password.replace(" ", "") and password_repeat.replace(" ", "")):
            raise ValueError("login, password and passwort repeat must be fulfilled")
        if password != password_repeat:
            raise ValueError("passwords must be the same")
        return birthdate, tech_stack, email, username, login, password, password_repeat

    @app.post('/main/registration')
    def registrate():
        try:
            birthdate, tech_stack, email, username, login, password, password_repeat = registrate_post_form_parser()
        except ValueError:
            return redirect(url_for('render_registration_page'))
        authentication_token = AuthenticationTasks.register_task.delay(
            SaveUserDTO(
                is_admin=False,
                login=login,
                username=username,
                hashed_password=sha256(password.encode()).hexdigest(),
                email=email,
                birthdate=birthdate,
                stack=tech_stack
            )
        ).get()
        if authentication_token is None:
            return redirect(url_for('render_registration_page'))
        else:
            session["authorization_token"] = authentication_token.to_json()
            return redirect(url_for("render_user_main_page"))

    @app.get('/main/login')
    def render_login_page():
        return render_template(
            "general/login_index.html",
            login_maxlength=LOGIN_MAXLENGTH,
            password_maxlength=PASSWORD_MAXLENGTH,
            post_login_url=url_for("authorize"),
            registration_url=url_for("render_registration_page")
        )

    @app.post('/main/login')
    def authorize():
        login = request.form.get('login').strip(" ")
        password = request.form.get('password')
        if login is None or password is None:
            return redirect(url_for('render_login_page'))

        authentication_token = AuthenticationTasks.login_task.delay(
                LoginUserDTO(login=login, hashed_password=sha256(password.encode()).hexdigest())
        ).get()
        if authentication_token is None:
            return redirect(url_for('render_login_page'))
        else:
            session["authorization_token"] = authentication_token.to_json()
            if authentication_token.is_admin:
                return redirect(url_for("render_admin_main_page"))
            else:
                return redirect(url_for("render_user_main_page"))

    # User
    @app.get('/user/')
    def redirect_to_main_user():
        return redirect(url_for("render_user_main_page"))

    @app.get("/user/main")
    def render_user_main_page():
        return render_template(
            "user/user_main_index.html",
            discussions_url=url_for("render_user_discussions_page"),
            knowledge_url=url_for("render_user_knowledge_catalog_page"),
            form_action_url=url_for("user_main_page_post"),
            user_authorized=session.get("authorization_token")
        )

    @app.post("/user/main")
    def user_main_page_post():
        if session.get("authorization_token"):
            if "exit" in request.form.keys():
                session.pop("authorization_token")
                return redirect(url_for("render_user_main_page"))
        else:
            if "login" in request.form.keys():
                return redirect(url_for("render_login_page"))

    # Discussions

    @app.get("/user/discussions/")
    def render_user_discussions_page():
        return render_template(
            "user/discussions_search_index.html",
            discussions_url=url_for("render_user_discussions_page"),
            knowledge_url=url_for("render_user_knowledge_catalog_page"),
            add_discussion_url=url_for("render_add_discussion_page"),
            form_action_url=url_for("user_discussions_page_post"),
            all_categories_item=ALL_CATEGORIES_ITEM,
            categories=DiscussionTasks.get_discussion_categories_task.delay().get(),
            current_selected_category=ALL_CATEGORIES_ITEM,
            user_authorized=session.get("authorization_token")
        )

    def discussion_search():
        not_found_discussion_title = None
        category = request.form.get("categories_list")
        if request.form.get("title").replace(" ", "") == "":
            if category == ALL_CATEGORIES_ITEM:
                discussions = [
                    disc.title for disc in DiscussionTasks.get_all_discussions_task.delay().get()
                ]
            else:
                discussions = [
                    disc.title for disc in DiscussionTasks.get_discussions_by_category_task.delay(category).get()
                ]
        else:
            discussion = DiscussionTasks.get_discussion_by_title_task.delay(request.form.get("title").strip(" ")).get()
            if discussion is None:
                discussions = None
                not_found_discussion_title = request.form.get("title").strip(" ")
            else:
                discussions = [discussion.title]

        return render_template(
            "user/discussions_search_index.html",
            discussions_url=url_for("render_user_discussions_page"),
            knowledge_url=url_for("render_user_knowledge_catalog_page"),
            add_discussion_url=url_for("render_add_discussion_page"),
            form_action_url=url_for("user_discussions_page_post"),
            all_categories_item=ALL_CATEGORIES_ITEM,
            categories=DiscussionTasks.get_discussion_categories_task.delay().get(),
            current_selected_category=category,
            discussions_titles=discussions,
            not_found_discussion_title=not_found_discussion_title,
            user_authorized=session.get("authorization_token")
        )

    @app.post("/user/discussions/")
    def user_discussions_page_post():
        if "search" in request.form.keys():
            return discussion_search()
        elif "open_discussion" in request.form.keys():
            return redirect(
                url_for("render_discussion_page", discussion_title=request.form.get("open_discussion"))
            )

        if session.get("authorization_token"):
            if "exit" in request.form.keys():
                session.pop("authorization_token")
                return redirect(url_for("render_main_page"))
        else:
            if "login" in request.form.keys():
                return redirect(url_for("render_login_page"))

    def parse_comments_to_list(comments):
        return [
            {
                "sender_username": comment.comment_sender.username,
                "description": comment.description
            } for comment in comments
        ]

    @app.get("/user/discussions/<discussion_title>")
    def render_discussion_page(discussion_title):
        discussion = DiscussionTasks.get_discussion_by_title_task.delay(discussion_title).get()
        if discussion is None:
            return render_template(
                "user/discussions_search_index.html",
                discussions_url=url_for("render_user_discussions_page"),
                knowledge_url=url_for("render_user_knowledge_catalog_page"),
                add_discussion_url=url_for("render_add_discussion_page"),
                form_action_url=url_for("user_discussions_page_post"),
                all_categories_item=ALL_CATEGORIES_ITEM,
                categories=DiscussionTasks.get_discussion_categories_task.delay().get(),
                current_selected_category=ALL_CATEGORIES_ITEM,
                not_found_discussion_title=discussion_title,
                user_authorized=session.get("authorization_token")
            )
        else:
            return render_template(
                "user/discussion_opened_index.html",
                discussions_url=url_for("render_user_discussions_page"),
                knowledge_url=url_for("render_user_knowledge_catalog_page"),
                form_action_url=url_for("discussion_page_post", discussion_title=discussion.title),
                discussion_title=discussion.title,
                sender_username=discussion.discussion_sender.username,
                discussion_description=discussion.description,
                comments=parse_comments_to_list(discussion.connected_comments),
                user_authorized=session.get("authorization_token")
            )

    @app.post("/user/discussions/<discussion_title>")
    def discussion_page_post(discussion_title):
        if session.get("authorization_token"):
            if "exit" in request.form.keys():
                session.pop("authorization_token")
                return redirect(url_for("render_main_page"))
            elif "add_comment" in request.form.keys():
                DiscussionTasks.save_comment_task.delay(
                    SaveCommentDTO(
                        description=request.form.get("comment_description"),
                        sender_login=session.get("authorization_token").get("login"),
                        discussion_title=discussion_title
                    ),
                    AuthorizationToken(**session.get("authorization_token"))
                ).get()
                return redirect(url_for("render_discussion_page", discussion_title=discussion_title))
        else:
            if "login" in request.form.keys():
                return redirect(url_for("render_login_page"))

    @app.get("/user/discussions/add_discussion")
    def render_add_discussion_page():
        if session.get("authorization_token"):
            return render_template(
                "user/add_discussion_index.html",
                discussions_url=url_for("render_user_discussions_page"),
                knowledge_url=url_for("render_user_knowledge_catalog_page"),
                form_action_url=url_for("add_discussion_page_post")
            )
        else:
            return redirect(url_for("render_login_page"))

    def add_discussion_page_wrong_title(old_description, old_category, error_message):
        return render_template(
            "user/add_discussion_index.html",
            discussions_url=url_for("render_user_discussions_page"),
            knowledge_url=url_for("render_user_knowledge_catalog_page"),
            form_action_url=url_for("add_discussion_page_post"),
            old_description=old_description,
            old_category=old_category,
            error_message=error_message
        )

    def add_discussion_page_wrong_description(old_title, old_category, error_message):
        return render_template(
            "user/add_discussion_index.html",
            discussions_url=url_for("render_user_discussions_page"),
            knowledge_url=url_for("render_user_knowledge_catalog_page"),
            form_action_url=url_for("add_discussion_page_post"),
            old_title=old_title,
            old_category=old_category,
            error_message=error_message
        )

    def add_discussion_page_wrong_category(old_title, old_description, error_message):
        return render_template(
            "user/add_discussion_index.html",
            discussions_url=url_for("render_user_discussions_page"),
            knowledge_url=url_for("render_user_knowledge_catalog_page"),
            form_action_url=url_for("add_discussion_page_post"),
            old_title=old_title,
            old_description=old_description,
            error_message=error_message
        )

    def add_new_discussion():
        if not request.form.get("discussion_title").replace(" ", ""):
            return add_discussion_page_wrong_title(
                old_description=request.form.get("discussion_description").strip(" "),
                old_category=request.form.get("discussion_category"),
                error_message="Заголовок обсуждения должно быть не пустым."
            )
        elif not request.form.get("discussion_description").replace(" ", ""):
            return add_discussion_page_wrong_description(
                old_title=request.form.get("discussion_title").strip(" "),
                old_category=request.form.get("discussion_category"),
                error_message="Описание обсуждения должно быть не пустым."
            )
        elif not request.form.get("discussion_category").replace(" ", ""):
            return add_discussion_page_wrong_category(
                old_title=request.form.get("discussion_title").strip(" "),
                old_description=request.form.get("discussion_description"),
                error_message="Категория обсуждения должна быть не пустой."
            )
        elif DiscussionTasks.get_discussion_by_title_task.delay(request.form.get("discussion_title").strip(" ")).get():
            return add_discussion_page_wrong_title(
                old_description=request.form.get("discussion_description").strip(" "),
                old_category=request.form.get("discussion_category"),
                error_message=f"Заголовок обсуждения должен быть уникальным. Обсуждение с заголовком"
                              f" \"{request.form.get('discussion_title').strip(' ')}\" уже опубликован."
            )
        else:
            DiscussionTasks.save_discussion_task.delay(
                SaveDiscussionDTO(
                    title=request.form.get("discussion_title").strip(" "),
                    description=request.form.get("discussion_description"),
                    category=request.form.get("discussion_category"),
                    sender_login=session.get("authorization_token").get("login")
                ),
                AuthorizationToken(**session.get("authorization_token"))
            ).get()
            return redirect(url_for("render_user_discussions_page"))

    @app.post("/user/discussions/add_discussion")
    def add_discussion_page_post():
        if session.get("authorization_token"):
            if "exit" in request.form.keys():
                session.pop("authorization_token")
                return redirect(url_for("render_main_page"))
            elif "add_discussion" in request.form.keys():
                return add_new_discussion()
        else:
            return redirect(url_for("render_login_page"))

    # Knowledge

    @app.get("/user/knowledge_catalog/")
    def render_user_knowledge_catalog_page():
        return render_template(
            "user/knowledge_search_index.html",
            discussions_url=url_for("render_user_discussions_page"),
            knowledge_url=url_for("render_user_knowledge_catalog_page"),
            add_knowledge_url=url_for("render_add_knowledge_page"),
            form_action_url=url_for("user_knowledge_catalog_page_post"),
            all_categories_item=ALL_CATEGORIES_ITEM,
            categories=KnowledgeTasks.get_knowledge_categories_task.delay(status=KnowledgeStatus.PUBLISHED).get(),
            current_selected_category=ALL_CATEGORIES_ITEM,
            user_authorized=session.get("authorization_token")
        )

    def published_knowledge_search():
        not_found_knowledge_title = None
        category = request.form.get("categories_list")
        if request.form.get("title").replace(" ", "") == "":
            if category == ALL_CATEGORIES_ITEM:
                knowledge_titles = [
                    knowledge.title for knowledge in KnowledgeTasks.get_published_knowledge_task.delay().get()
                ]
            else:
                knowledge_titles = [
                    knowledge.title for knowledge in
                    KnowledgeTasks.get_knowledge_by_category_task.delay(category, KnowledgeStatus.PUBLISHED).get()
                ]
        else:
            knowledge = KnowledgeTasks.get_knowledge_by_title_task.delay(request.form.get("title").strip(" ")).get()
            if knowledge is None:
                knowledge_titles = None
                not_found_knowledge_title = request.form.get("title").strip(" ")
            else:
                knowledge_titles = [knowledge.title]

        return render_template(
            "user/knowledge_search_index.html",
            discussions_url=url_for("render_user_discussions_page"),
            knowledge_url=url_for("render_user_knowledge_catalog_page"),
            add_knowledge_url=url_for("render_add_knowledge_page"),
            form_action_url=url_for("user_knowledge_catalog_page_post"),
            all_categories_item=ALL_CATEGORIES_ITEM,
            categories=KnowledgeTasks.get_knowledge_categories_task.delay(status=KnowledgeStatus.PUBLISHED).get(),
            current_selected_category=category,
            knowledge_titles=knowledge_titles,
            not_found_knowledge_title=not_found_knowledge_title,
            user_authorized=session.get("authorization_token")
        )

    @app.post("/user/knowledge_catalog/")
    def user_knowledge_catalog_page_post():
        if "search" in request.form.keys():
            return published_knowledge_search()
        elif "open_knowledge" in request.form.keys():
            return redirect(
                url_for("render_user_knowledge_page", knowledge_title=request.form.get("open_knowledge"))
            )

        if session.get("authorization_token"):
            if "exit" in request.form.keys():
                session.pop("authorization_token")
                return redirect(url_for("render_main_page"))
        else:
            if "login" in request.form.keys():
                return redirect(url_for("render_login_page"))

    @app.get("/user/knowledge_catalog/<knowledge_title>")
    def render_user_knowledge_page(knowledge_title):
        knowledge = KnowledgeTasks.get_knowledge_by_title_task.delay(knowledge_title).get()
        if knowledge is None:
            return render_template(
                "user/knowledge_search_index.html",
                discussions_url=url_for("render_user_discussions_page"),
                knowledge_url=url_for("render_user_knowledge_catalog_page"),
                add_knowledge_url=url_for("render_add_knowledge_page"),
                form_action_url=url_for("user_knowledge_catalog_page_post"),
                all_categories_item=ALL_CATEGORIES_ITEM,
                categories=KnowledgeTasks.get_knowledge_categories_task.delay(status=KnowledgeStatus.PUBLISHED).get(),
                current_selected_category=ALL_CATEGORIES_ITEM,
                not_found_knowledge_title=knowledge_title,
                user_authorized=session.get("authorization_token")
            )
        else:
            return render_template(
                "user/knowledge_opened_index.html",
                discussions_url=url_for("render_user_discussions_page"),
                knowledge_url=url_for("render_user_knowledge_catalog_page"),
                form_action_url=url_for("knowledge_page_post", knowledge_title=knowledge_title),
                knowledge_title=knowledge.title,
                sender_username=knowledge.knowledge_sender.username,
                knowledge_description=knowledge.description,
                knowledge_link=knowledge.link,
                user_authorized=session.get("authorization_token")
            )

    @app.post("/user/knowledge_catalog/<knowledge_title>")
    def knowledge_page_post(knowledge_title):
        if session.get("authorization_token"):
            if "exit" in request.form.keys():
                session.pop("authorization_token")
                return redirect(url_for("render_main_page"))
        else:
            if "login" in request.form.keys():
                return redirect(url_for("render_login_page"))

    @app.get("/user/knowledge_catalog/add_knowledge")
    def render_add_knowledge_page():
        if session.get("authorization_token"):
            return render_template(
                "user/add_knowledge_index.html",
                discussions_url=url_for("render_user_discussions_page"),
                knowledge_url=url_for("render_user_knowledge_catalog_page"),
                form_action_url=url_for("add_knowledge_page_post")
            )
        else:
            return redirect(url_for("render_login_page"))

    def add_knowledge_page_wrong_title(old_description, old_category, old_link, error_message):
        return render_template(
            "user/add_knowledge_index.html",
            discussions_url=url_for("render_user_discussions_page"),
            knowledge_url=url_for("render_user_knowledge_catalog_page"),
            form_action_url=url_for("add_knowledge_page_post"),
            old_description=old_description,
            old_category=old_category,
            old_link=old_link,
            error_message=error_message
        )

    def add_knowledge_page_wrong_description(old_title, old_category, old_link, error_message):
        return render_template(
            "user/add_knowledge_index.html",
            discussions_url=url_for("render_user_discussions_page"),
            knowledge_url=url_for("render_user_knowledge_catalog_page"),
            form_action_url=url_for("add_knowledge_page_post"),
            old_title=old_title,
            old_category=old_category,
            old_link=old_link,
            error_message=error_message
        )

    def add_knowledge_page_wrong_category(old_title, old_description, old_link, error_message):
        return render_template(
            "user/add_knowledge_index.html",
            discussions_url=url_for("render_user_discussions_page"),
            knowledge_url=url_for("render_user_knowledge_catalog_page"),
            form_action_url=url_for("add_knowledge_page_post"),
            old_title=old_title,
            old_description=old_description,
            old_link=old_link,
            error_message=error_message
        )

    def add_knowledge_page_wrong_link(old_title, old_description, old_category, error_message):
        return render_template(
            "user/add_knowledge_index.html",
            discussions_url=url_for("render_user_discussions_page"),
            knowledge_url=url_for("render_user_knowledge_catalog_page"),
            form_action_url=url_for("add_knowledge_page_post"),
            old_title=old_title,
            old_description=old_description,
            old_category=old_category,
            error_message=error_message
        )

    def add_new_knowledge():
        if not request.form.get("knowledge_title").replace(" ", ""):
            return add_knowledge_page_wrong_title(
                old_description=request.form.get("knowledge_description"),
                old_category=request.form.get("knowledge_category"),
                old_link=request.form.get("knowledge_link"),
                error_message="Заголовок знания должен быть не пустым."
            )
        elif not request.form.get("knowledge_description").replace(" ", ""):
            return add_knowledge_page_wrong_description(
                old_title=request.form.get("knowledge_title").strip(' '),
                old_category=request.form.get("knowledge_category"),
                old_link=request.form.get("knowledge_link"),
                error_message="Описание должно быть не пустым."
            )
        elif not request.form.get("knowledge_category").replace(" ", ""):
            return add_knowledge_page_wrong_category(
                old_title=request.form.get("knowledge_title").strip(' '),
                old_description=request.form.get("knowledge_description"),
                old_link=request.form.get("knowledge_link"),
                error_message="Категория знания должна быть не пустой."
            )
        elif not request.form.get("knowledge_link").replace(" ", ""):
            return add_knowledge_page_wrong_link(
                old_title=request.form.get("knowledge_title").strip(' '),
                old_description=request.form.get("knowledge_description"),
                old_category=request.form.get("knowledge_category"),
                error_message="Ссылка на источник знания должна быть не пустой."
            )
        elif KnowledgeTasks.get_knowledge_by_title_task.delay(request.form.get("knowledge_title").strip(" ")).get():
            return add_knowledge_page_wrong_title(
                old_description=request.form.get("knowledge_description"),
                old_category=request.form.get("knowledge_category"),
                old_link=request.form.get("knowledge_link"),
                error_message=f"Заголовок знания должен быть уникальным. Знание с заголовком"
                              f" \"{request.form.get('knowledge_title').strip(' ')}\" уже существует в каталоге."
            )
        else:
            KnowledgeTasks.save_knowledge_task.delay(
                SaveKnowledgeDTO(
                    title=request.form.get("knowledge_title").strip(" "),
                    description=request.form.get("knowledge_description"),
                    link=request.form.get("knowledge_link"),
                    category=request.form.get("knowledge_category"),
                    sender_login=session.get("authorization_token").get("login")
                ),
                AuthorizationToken(**session.get("authorization_token"))
            ).get()
            return redirect(url_for("render_user_knowledge_catalog_page"))

    @app.post("/user/knowledge_catalog/add_knowledge")
    def add_knowledge_page_post():
        if session.get("authorization_token"):
            if "exit" in request.form.keys():
                session.pop("authorization_token")
                return redirect(url_for("render_main_page"))
            elif "add_knowledge" in request.form.keys():
                return add_new_knowledge()
        else:
            return redirect(url_for("render_login_page"))

    # Admin

    @app.get('/admin/')
    def redirect_to_main_admin():
        if session.get("authorization_token") and session.get("authorization_token").get("is_admin"):
            return redirect(url_for("render_admin_main_page"))
        else:
            return redirect(url_for("render_login_page"))

    @app.get("/admin/main")
    def render_admin_main_page():
        if session.get("authorization_token") and session.get("authorization_token").get("is_admin"):
            return render_template(
                "admin/main_admin_index.html",
                inspect_knowledge_url=url_for("render_knowledge_list_admin_page"),
                form_action_url=url_for("user_main_page_post")
            )
        else:
            return redirect(url_for("render_login_page"))

    @app.get("/admin/inspect_knowledge_catalog/")
    def render_knowledge_list_admin_page():
        if session.get("authorization_token") and session.get("authorization_token").get("is_admin"):
            knowledge_list = (
                KnowledgeTasks
                .get_in_processing_knowledge_task
                .delay(AuthorizationToken(**session.get("authorization_token")))
                .get()
            )
            return render_template(
                "admin/knowledge_list_admin_index.html",
                inspect_knowledge_url=url_for("render_admin_main_page"),
                form_action_url=url_for("knowledge_list_admin_post"),
                knowledge_titles=[knowledge.title for knowledge in knowledge_list]
            )
        else:
            return redirect(url_for("render_login_page"))

    @app.post("/admin/inspect_knowledge_catalog/")
    def knowledge_list_admin_post():
        if session.get("authorization_token") and session.get("authorization_token").get("is_admin"):
            if "exit" in request.form.keys():
                session.pop("authorization_token")
                return redirect(url_for("render_main_page"))
            elif "inspect_knowledge" in request.form.keys():
                return redirect(
                    url_for(
                        "render_knowledge_to_inspect", knowledge_title=request.form.get("inspect_knowledge")
                    )
                )
        else:
            return redirect(url_for("render_login_page"))

    def knowledge_to_inspect_error(error_message):
        knowledge_list = (
            KnowledgeTasks
            .get_in_processing_knowledge_task
            .delay(AuthorizationToken(**session.get("authorization_token")))
            .get()
        )
        return render_template(
            "admin/knowledge_list_admin_index.html",
            inspect_knowledge_url=url_for("render_admin_main_page"),
            form_action_url=url_for("knowledge_list_admin_post"),
            knowledge_titles=[knowledge.title for knowledge in knowledge_list],
            error_message=error_message
        )

    @app.get("/admin/inspect_knowledge_catalog/<knowledge_title>")
    def render_knowledge_to_inspect(knowledge_title):
        if session.get("authorization_token") and session.get("authorization_token").get("is_admin"):
            knowledge = KnowledgeTasks.get_knowledge_by_title_task.delay(knowledge_title).get()
            if knowledge is None:
                return knowledge_to_inspect_error(
                    error_message=f"Знание с заголовком \"{knowledge_title}\" не обнаружено."
                )
            elif knowledge.status != KnowledgeStatus.IN_PROCESSING:
                return knowledge_to_inspect_error(
                    error_message=f"Знание с заголовком \"{knowledge_title}\" уже обработано и не требует проверки."
                )
            else:
                return render_template(
                    "/admin/knowledge_opened_admin_index.html",
                    inspect_knowledge_url=url_for("render_admin_main_page"),
                    form_action_url=url_for("knowledge_to_inspect_post", knowledge_title=knowledge_title),
                    knowledge_title=knowledge.title,
                    knowledge_description=knowledge.description,
                    knowledge_link=knowledge.link,
                    sender_username=knowledge.knowledge_sender.username
                )
        else:
            return redirect(url_for("render_login_page"))

    @app.post("/admin/inspect_knowledge_catalog/<knowledge_title>")
    def knowledge_to_inspect_post(knowledge_title):
        print(request.form)
        if session.get("authorization_token") and session.get("authorization_token").get("is_admin"):
            if "exit" in request.form.keys():
                session.pop("authorization_token")
                return redirect(url_for("render_main_page"))
            elif "accept" in request.form.keys():
                (
                    KnowledgeTasks
                    .accept_knowledge_publishing_task
                    .delay(knowledge_title, AuthorizationToken(**session.get("authorization_token")))
                    .get()
                )
                return redirect(url_for("render_knowledge_list_admin_page"))
            elif "delete" in request.form.keys():
                (
                    KnowledgeTasks
                    .delete_knowledge_by_title_task
                    .delay(knowledge_title, AuthorizationToken(**session.get("authorization_token")))
                    .get()
                )
                return redirect(url_for("render_knowledge_list_admin_page"))
        else:
            return redirect(url_for("render_login_page"))

    return app


if __name__ == '__main__':
    app = create_app()

    app.run("127.0.0.1", 5000)

