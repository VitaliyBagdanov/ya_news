from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse
import pytest

from news.models import Comment
from news.forms import WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, id_for_args):
    url = reverse('news:detail', args=id_for_args)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_note(author_client, author, form_data, id_for_args):
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
