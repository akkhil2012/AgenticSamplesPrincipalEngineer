from models import Evaluation


class LoanApprovalAgent:
    """Pure recommendation logic: no database, tool handles or final approval authority."""

    def evaluate(self, application, minimum_credit_score, maximum_loan_amount):
        reasons = []
        if application.credit_score < minimum_credit_score:
            reasons.append("Credit score is below the configured minimum")
        if application.loan_amount > maximum_loan_amount:
            reasons.append("Loan amount exceeds the configured maximum")
        return Evaluation(
            recommendation="REJECT" if reasons else "APPROVE",
            reason="; ".join(reasons)
            if reasons
            else "Credit score and loan amount meet policy requirements",
        )
