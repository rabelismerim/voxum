import textwrap

from utils import _

from apps.meetings.models import RepresentativeMeeting


class AbstractVotingReport:
    column_a = 'A'
    column_b = ['B', 'D']
    column_c = ['E', 'F']
    column_d = 'G'
    column_e = ['H', 'I']

    # column_d = ['F', 'G']
    # column_e = 'H'
    column_f = ['J', 'K']
    column_g = 'L'
    column_h = 'M'
    row = 6
    count = 0

    def __init__(self, voting_report, name):
        self.voting_report = voting_report
        self.task_id = voting_report.task_id
        self.name = name
        from apps.report.models import ReportVotingToPDF
        self.report = ReportVotingToPDF(self.voting_report.id, self.name)
        self.report.writer.default_fill_width = 20

    def get_font_bold_gray(self):
        fonte = None
        fill_ = None

        if divmod(self.count, 2)[1] == 0:
            fill_ = self.report.writer.STILE.gray_fill

        font_f = {
            'font': fonte,
            'fill': fill_,
            'alignment': 'left'
        }

        self.count += 1

        return font_f


class ReportVotingDetail(AbstractVotingReport):
    column_a = ['A', 'B']
    column_b = ['C', 'D']
    count = 0

    def get_representatives(self):
        meeting_id = self.voting_report.voting.meeting.id
        return RepresentativeMeeting.objects.filter(meeting_id=meeting_id)

    def export(self):
        self.set_title()
        self.set_votes_representatives()
        self.set_votes_creditors()
        self.report.export()
        return True

    def set_votes_representatives(self):
        representatives = self.get_representatives()
        for representative in representatives:
            voting_results = representative.get_creditor_votes_by_class_voting(self.voting_report.voting)

            self.set_voting_results(representative, voting_results)

    def set_voting_results(self, representative, voting_results):
        for voting in voting_results:
            name = representative.guest.user.full_name
            name = textwrap.fill(name, width=20)

            font_f = self.get_font_bold_gray()

            miscellaneous_creditors = _('CREDORES DIVERSOS')
            miscellaneous_creditors = textwrap.fill(miscellaneous_creditors, width=20)

            self.report.writer.set_value(self.row, self.column_a, miscellaneous_creditors, wrap_text=True, **font_f)
            self.report.writer.set_value(self.row, self.column_b, name, wrap_text=True, **font_f)
            self.report.writer.set_value(self.row, self.column_c, voting['class_name'], **font_f)
            self.report.writer.set_value(self.row, self.column_d, voting['total_votes'], **font_f)
            self.report.writer.set_value(self.row, self.column_e, voting['vote_description'], wrap_text=True, **font_f)
            self.report.writer.set_value(self.row, self.column_f, self.voting_report.voting.description, wrap_text=True,
                                         **font_f)
            self.row += 1
            # self.count += 1

    def get_votes_creditors(self):
        return self.voting_report.voting.vote_by_creditors.filter()

    def set_votes_creditors(self):
        vote_by_creditors = self.get_votes_creditors()

        for result in vote_by_creditors:

            voted_by = result.voted_by

            if voted_by and voted_by != result.creditor.guest.user and result.creditor.representatives.filter(
                    representative__guest__user=voted_by).exists():
                continue

            name = result.creditor.guest.user.full_name
            name = textwrap.fill(name, width=20)
            font_f = self.get_font_bold_gray()

            self.report.writer.set_value(self.row, self.column_a, name, wrap_text=True, **font_f)

            self.report.writer.set_value(self.row, self.column_b, 'PRÓPRIO', **font_f)
            self.report.writer.set_value(self.row, self.column_c, result.vote.classe.description, **font_f)
            self.report.writer.set_value(self.row, self.column_d, 1, **font_f)

            self.report.writer.set_value(self.row, self.column_e, result.vote.value, wrap_text=True, **font_f)
            self.report.writer.set_value(self.row, self.column_f, self.voting_report.voting.description, wrap_text=True,
                                         **font_f)
            self.row += 1

    def set_title(self):
        font = self.report.writer.STILE.bold_black_font
        self.report.writer.set_value(self.row, self.column_a, 'Credor', font=font)
        self.report.writer.set_value(self.row, self.column_b, 'Representante', font=font)
        self.report.writer.set_value(self.row, self.column_c, 'Classe', font=font)
        self.report.writer.set_value(self.row, self.column_d, 'Total', font=font)
        self.report.writer.set_value(self.row, self.column_e, 'Voto', font=font)
        self.report.writer.set_value(self.row, self.column_f, 'Assunto', font=font)

        self.report.writer.set_repeat_title(self.row, self.row + 1)
        self.row += 1
        self.report.writer.set_value(self.row, self.column_d, 'Votos', font=font)
        self.row += 2


class ReportVotingDetailReservations(ReportVotingDetail):

    def set_votes_representatives(self):
        representatives = self.get_representatives()
        for representative in representatives:
            voting_results = representative.get_creditor_reservations_votes_by_class_voting(self.voting_report.voting)

            self.set_voting_results(representative, voting_results)


    def get_votes_creditors(self):
        return super().get_votes_creditors().filter(has_reservations=True)


class ReportVotingPresentDetail(AbstractVotingReport):
    column_a = 'A'
    column_b = ['B', 'C']
    column_c = 'D'
    column_d = ['E', 'F']
    column_e = 'G'
    column_f = 'H'
    column_g = 'I'
    column_h = ['J', 'K']

    def get_representatives(self):
        meeting_id = self.voting_report.voting.meeting.id
        return RepresentativeMeeting.objects.filter(meeting_id=meeting_id)

    def export(self):
        self.set_title()
        self.set_votes_representatives()
        self.set_votes_creditors()
        self.report.export()
        return True

    def set_votes_representatives(self):
        representatives = self.get_representatives()
        for representative in representatives:
            voting_results = representative.get_creditor_presence_votes_by_class_voting(self.voting_report.voting)
            self.set_voting_results(representative, voting_results)

    def set_voting_results(self, representative, voting_results):
        for voting in voting_results:
            font_f = self.get_font_bold_gray()

            self.report.writer.set_value(self.row, self.column_a, representative.code, **font_f)
            self.report.writer.set_value(self.row, self.column_b, 'CREDORES DIVERSOS', **font_f)

            self.report.writer.set_value(self.row, self.column_c, representative.guest.entity.legal_number,
                                         wrap_text=True, **font_f)
            name = representative.guest.user.full_name
            name = textwrap.fill(name, width=20)

            self.report.writer.set_value(self.row, self.column_d, name, wrap_text=True, **font_f)
            self.report.writer.set_value(self.row, self.column_e, voting['class_name'], **font_f)
            self.report.writer.set_value(self.row, self.column_f, voting['total_votes'], **font_f)
            self.report.writer.set_value(self.row, self.column_g, voting['vote_description'], wrap_text=True,
                                         fill_width=10, **font_f)

            total_credit = self.report.writer.parse_number(voting['total_credit'])
            self.report.writer.set_value(self.row, self.column_h, f'R$ {total_credit}', **font_f)
            self.row += 1

    def get_voting_results(self):
        return self.voting_report.voting.vote_by_creditors.filter(creditor__presence__is_present=True)

    def set_votes_creditors(self):
        vote_by_creditors = self.get_voting_results()

        for result in vote_by_creditors:

            voted_by = result.voted_by

            if voted_by and voted_by != result.creditor.guest.user and result.creditor.representatives.filter(
                    representative__guest__user=voted_by).exists():
                continue

            name = result.creditor.guest.user.full_name
            name = textwrap.fill(name, width=25)
            font_f = self.get_font_bold_gray()

            self.report.writer.set_value(self.row, self.column_a, result.creditor.code, **font_f)
            self.report.writer.set_value(self.row, self.column_b, name, wrap_text=True, **font_f)
            self.report.writer.set_value(self.row, self.column_c, result.creditor.guest.entity.legal_number, **font_f)
            self.report.writer.set_value(self.row, self.column_d, 'PRÓPRIO', **font_f)
            self.report.writer.set_value(self.row, self.column_e, result.vote.classe.description, **font_f)
            self.report.writer.set_value(self.row, self.column_f, 1, **font_f)
            self.report.writer.set_value(self.row, self.column_g, result.vote.value, wrap_text=True, fill_width=10,
                                         **font_f)

            credit_value = self.report.writer.parse_number(result.creditor.credit_value)
            self.report.writer.set_value(self.row, self.column_h, f'R$ {credit_value}', **font_f)
            self.row += 1

    def set_title(self):
        font = self.report.writer.STILE.bold_black_font
        self.report.writer.set_value(self.row, self.column_a, 'Código', font=font)
        self.report.writer.set_value(self.row, self.column_b, 'Credor', font=font)
        self.report.writer.set_value(self.row, self.column_c, 'CPF/CNPJ', font=font)
        self.report.writer.set_value(self.row, self.column_d, 'Representante', font=font)
        self.report.writer.set_value(self.row, self.column_e, 'Classe', font=font)
        self.report.writer.set_value(self.row, self.column_f, 'Total', font=font)
        self.report.writer.set_value(self.row, self.column_g, 'Voto', font=font)
        self.report.writer.set_value(self.row, self.column_h, 'Valor', font=font)

        self.report.writer.set_repeat_title(self.row, self.row + 1)
        self.row += 1
        self.report.writer.set_value(self.row, self.column_f, 'Votos', font=font)
        self.row += 2


class ReportVotingPresentDetailReservations(ReportVotingPresentDetail):
    column_a = 'A'
    column_b = ['B', 'C']
    column_c = 'D'
    column_d = ['E', 'F']
    column_e = 'G'
    column_f = 'H'
    column_g = 'I'
    column_h = ['J', 'K']

    def set_votes_representatives(self):
        representatives = self.get_representatives()
        for representative in representatives:
            voting_results = representative.get_creditor_reservations_presence_votes_by_class_voting(self.voting_report.voting)

            self.set_voting_results(representative, voting_results)

    def get_voting_results(self):
        return super().get_voting_results().filter(has_reservations=True)


class VotingReport:

    def __init__(self, report_id):
        self.report_id = report_id
        from apps.report.models import ReportVoting
        self.voting_report: ReportVoting = ReportVoting.objects.get(id=report_id)

    def export(self):
        from apps.report.models import ReportVotingChoices

        report_export_types = {
            ReportVotingChoices.VOTING_DETAIL.value: {'label': ReportVotingChoices.VOTING_DETAIL.label,
                                                      'report': ReportVotingDetail},
            ReportVotingChoices.VOTING_PRESENT_DETAIL.value: {'label': ReportVotingChoices.VOTING_PRESENT_DETAIL.label,
                                                              'report': ReportVotingPresentDetail},
            ReportVotingChoices.VOTING_RESERVATION_DETAIL.value: {
                'label': ReportVotingChoices.VOTING_RESERVATION_DETAIL.label, 'report': ReportVotingDetailReservations},
            ReportVotingChoices.VOTING_RESERVATION_PRESENT_DETAIL.value: {
                'label': ReportVotingChoices.VOTING_RESERVATION_PRESENT_DETAIL.label,
                'report': ReportVotingPresentDetailReservations},
        }

        report = report_export_types.get(self.voting_report.report_type)

        if report:
            report['report'](self.voting_report, report['label']).export()
        else:
            raise ValueError(f'Unknown meeting report type {self.voting_report}')
