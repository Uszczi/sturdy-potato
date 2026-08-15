import pytest
from django.test import Client
from django.utils import timezone
from polls.models import Choice, Question


@pytest.mark.django_db
def test_poll_index_lists_questions() -> None:
    question = Question.objects.create(
        question_text="What is your favorite color?",
        pub_date=timezone.now(),
    )

    response = Client().get("/polls/")

    assert response.status_code == 200
    assert question.question_text in response.content.decode()


@pytest.mark.django_db
def test_vote_without_a_choice_renders_an_error() -> None:
    question = Question.objects.create(
        question_text="What is your favorite color?",
        pub_date=timezone.now(),
    )

    response = Client().post(f"/polls/{question.id}/vote/", {})

    assert response.status_code == 200
    assert response.context["error_message"] == "You didn't select a choice."


@pytest.mark.django_db
def test_vote_increments_the_selected_choice() -> None:
    question = Question.objects.create(
        question_text="What is your favorite color?",
        pub_date=timezone.now(),
    )
    choice = Choice.objects.create(question=question, choice_text="Blue")

    response = Client().post(
        f"/polls/{question.id}/vote/",
        {"choice": choice.id},
    )

    assert response.status_code == 302
    assert response["Location"] == f"/polls/{question.id}/results/"
    choice.refresh_from_db()
    assert choice.votes == 1
