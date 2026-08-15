from polls.models import Choice, Question


def test_poll_model_string_representations() -> None:
    question = Question(question_text="Question")
    choice = Choice(question=question, choice_text="Choice")

    assert str(question) == "Question"
    assert str(choice) == "Choice"
