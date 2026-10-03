import pytest
from decimal import Decimal
from apps.creditors.models import RecoveringCompany, Creditor, CreditorClass
from apps.meetings.models import Meeting, MeetingType, MeetingStatus
from apps.voting.models import Poll, Vote, VoteChoice
from apps.voting.services import VotingResultService


@pytest.mark.django_db
def test_voting_result_calculation():
    # Empresa e Assembleia
    company = RecoveringCompany.objects.create(name="Empresa Teste", cnpj="12.345.678/0001-90")
    meeting = Meeting.objects.create(
        recovering_company=company,
        title="1ª AGC Teste",
        call_type=MeetingType.FIRST_CALL,
        status=MeetingStatus.IN_PROGRESS,
        start_date="2026-10-03 10:00:00"
    )

    # Credores Trabalhistas
    c1 = Creditor.objects.create(
        recovering_company=company,
        name="Trabalhador A",
        cpf_cnpj="111.111.111-11",
        creditor_class=CreditorClass.LABOR,
        credit_value=Decimal("5000.00")
    )
    c2 = Creditor.objects.create(
        recovering_company=company,
        name="Trabalhador B",
        cpf_cnpj="222.222.222-22",
        creditor_class=CreditorClass.LABOR,
        credit_value=Decimal("15000.00")
    )

    # Votação
    poll = Poll.objects.create(meeting=meeting, title="Aprovação do Plano")

    # Registo de Votos
    Vote.objects.create(
        poll=poll,
        creditor=c1,
        choice=VoteChoice.YES,
        creditor_class=c1.creditor_class,
        credit_value=c1.credit_value
    )
    Vote.objects.create(
        poll=poll,
        creditor=c2,
        choice=VoteChoice.NO,
        creditor_class=c2.creditor_class,
        credit_value=c2.credit_value
    )

    # Execução do cômputo
    results = VotingResultService.calculate_poll_results(poll)

    # Validação do resultado por Classe Trabalhista
    labor_results = results[CreditorClass.LABOR]
    assert labor_results['total_heads'] == 2
    assert labor_results['total_value'] == Decimal("20000.00")
    assert labor_results['yes']['heads'] == 1
    assert labor_results['no']['heads'] == 1