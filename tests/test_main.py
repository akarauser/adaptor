import os

from adaptor.main import get_conversation, init_db, start_conversation


def test_initialize_database():
    init_db()
    assert os.path.isfile("adaptor/data/history/conversations.db")


def test_initialize_conversation():
    start_conversation("test")
    assert get_conversation("test") == []
