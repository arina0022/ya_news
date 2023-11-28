import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, form_data):
    url = reverse("news:home")
    response = client.get(url)
    display_objects = response.context["object_list"]
    news_count = len(display_objects)

    assert news_count is settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_count(client, form_data):
    url = reverse("news:home")

    response = client.get(url)
    display_objects = response.context["object_list"]
    all_dates = [news.date for news in display_objects]

    sorted_dates = sorted(all_dates, reverse=True)

    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, form_comment, news):
    url = reverse("news:detail", args=(news.pk,))
    response = client.get(url)
    news = response.context["news"]
    all_comments = news.comment_set.all()
    for i in range(len(all_comments) - 1):
        assert all_comments[i].created <= all_comments[i + 1].created


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news):
    url = reverse("news:detail", args=(news.pk,))
    response = client.get(url)
    assert "form" not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(client, author, news):
    client.force_login(author)
    url = reverse("news:detail", args=(news.pk,))
    response = client.get(url)
    assert "form" in response.context
    assert isinstance(response.context["form"], CommentForm)
