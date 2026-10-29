"""Policy Decision Point (PDP). Model output never grants permissions."""

ACCOUNT_ACCESS = {"user1": {"ACC123"}, "user2": {"ACC456"}}


def authorize(user_id, account_id):
    return account_id in ACCOUNT_ACCESS.get(user_id, set())
