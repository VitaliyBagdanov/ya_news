from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, id_for_args):
    url = reverse('news:detail', args=id_for_args)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    author_client,
    author,
    form_data,
    id_for_args
):
    url = reverse('news:detail', args=id_for_args)
    response = author_client.post(url, data=form_data)
    expected_url = f'{url}#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 1


def test_user_cant_use_bad_words(
    author_client,
    author,
    bad_words,
    id_for_args
):
    url = reverse('news:detail', args=id_for_args)
    response = author_client.post(url, data=bad_words)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
    author_client,
    comment,
    comment_id_for_args,
    id_for_args,
    form_data
):
    url = reverse('news:edit', args=comment_id_for_args)
    response = author_client.post(url, data=form_data)
    news_url = reverse('news:detail', args=id_for_args)
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == 'Новый текст'


def test_author_can_delete_comment(
    author_client,
    comment_id_for_args,
    id_for_args,
    comment
):
    url = reverse('news:delete', args=comment_id_for_args)
    response = author_client.delete(url)
    news_url = reverse('news:detail', args=id_for_args)
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


def test_not_author_can_edit_comment(
    not_author_client,
    comment_id_for_args,
    form_data
):
    url = reverse('news:edit', args=comment_id_for_args)
    response = not_author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_author_can_delete_comment(
    not_author_client,
    comment_id_for_args,
):
    url = reverse('news:delete', args=comment_id_for_args)
    response = not_author_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
