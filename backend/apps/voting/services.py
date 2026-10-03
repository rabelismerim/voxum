from django.db.models import Sum, Count
from apps.voting.models import Poll, Vote, VoteChoice
from apps.creditors.models import CreditorClass


class VotingResultService:
    """Serviço responsável por calcular e consolidar os resultados de uma votação."""

    @staticmethod
    def calculate_poll_results(poll: Poll) -> dict:
        votes = poll.votes.all()
        results = {}

        for class_code, class_label in CreditorClass.choices:
            class_votes = votes.filter(creditor_class=class_code)
            
            # Totais da classe
            total_heads = class_votes.count()
            total_value = class_votes.aggregate(total=Sum('credit_value'))['total'] or 0

            # Votos SIM
            yes_votes = class_votes.filter(choice=VoteChoice.YES)
            yes_heads = yes_votes.count()
            yes_value = yes_votes.aggregate(total=Sum('credit_value'))['total'] or 0

            # Votos NÃO
            no_votes = class_votes.filter(choice=VoteChoice.NO)
            no_heads = no_votes.count()
            no_value = no_votes.aggregate(total=Sum('credit_value'))['total'] or 0

            # Abstenções
            abstain_votes = class_votes.filter(choice=VoteChoice.ABSTAIN)
            abstain_heads = abstain_votes.count()
            abstain_value = abstain_votes.aggregate(total=Sum('credit_value'))['total'] or 0

            results[class_code] = {
                'label': class_label,
                'total_heads': total_heads,
                'total_value': total_value,
                'yes': {'heads': yes_heads, 'value': yes_value},
                'no': {'heads': no_heads, 'value': no_value},
                'abstain': {'heads': abstain_heads, 'value': abstain_value},
            }

        return results