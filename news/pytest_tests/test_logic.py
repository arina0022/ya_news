from http import HTTPStatus
import random

import pytest
from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, comment, news):
    initial_comment_count = Comment.objects.count()
    url = reverse("news:detail", args=(news.pk,))
    comment_data = {"text": comment.text}
    response = client.post(url, data=comment_data)
    login_url = reverse("users:login")
    expected_url = f"{login_url}?next={url}"
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == initial_comment_count


@pytest.mark.django_db
def test_user_can_create_comment(client, author, comment, news):
    initial_comment_count = Comment.objects.count()
    client.force_login(author)
    url = reverse("news:detail", args=(news.pk,))
    comment_data = {"text": comment.text}
    response = client.post(url, data=comment_data)
    expected_url = f"/news/{news.pk}/#comments"
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == initial_comment_count + 1


@pytest.mark.django_db
def test_user_cant_use_bad_words(author, news, client):
    initial_comment_count = Comment.objects.count()
    client.force_login(author)
    url = reverse("news:detail", args=(news.pk,))
    random_bad_word = random.choice(BAD_WORDS)
    bad_words_data = {"text": f"Какой-то текст, {random_bad_word}, еще текст"}
    response = client.post(url, data=bad_words_data)
    assertFormError(response, form="form", field="text", errors=WARNING)

    comments_count = Comment.objects.count()
    assert comments_count == initial_comment_count


@pytest.mark.django_db
def test_author_can_delete_comment(comment, author, client, news):
    initial_comment_count = Comment.objects.count()
    url = reverse("news:delete", args=(comment.pk,))
    client.force_login(author)
    response = client.post(url)

    expected_url = f"/news/{news.pk}/#comments"
    assertRedirects(response, expected_url)

    comments_count = Comment.objects.count()
    assert comments_count == initial_comment_count - 1


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(comment, admin_client):
    initial_comment_count = Comment.objects.count()
    url = reverse("news:delete", args=(comment.pk,))
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == initial_comment_count


@pytest.mark.django_db
def test_author_can_edit_comment(comment, author, client, news):
    url = reverse("news:edit", args=(comment.pk,))
    client.force_login(author)
    new_text = "Новый текст"
    updated_data = {"text": new_text}
    response = client.post(url, data=updated_data)
    expected_url = f"/news/{news.pk}/#comments"
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == new_text


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(comment, admin_client):
    url = reverse("news:edit", args=(comment.pk,))
    new_text = "Новый текст"
    updated_data = {"text": new_text}
    response = admin_client.post(url, data=updated_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert not comment.text == new_text
