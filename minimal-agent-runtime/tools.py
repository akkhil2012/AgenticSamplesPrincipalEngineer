"""Tools supply facts the model cannot know. These fixtures contain synthetic data only."""

ACCOUNTS = {"ACC123": 50000, "ACC456": 25000}


def get_account_balance(account_id):
    return {
        "account_id": account_id,
        "balance": ACCOUNTS[account_id],
        "currency": "INR",
    }


def validate_balance_result(result, account_id):
    if (
        not isinstance(result, dict)
        or set(result) != {"account_id", "balance", "currency"}
        or result["account_id"] != account_id
        or result["currency"] != "INR"
        or type(result["balance"]) is not int
        or result["balance"] < 0
    ):
        raise ValueError("Invalid tool result")
    return dict(result)
