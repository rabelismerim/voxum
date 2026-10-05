"""
Módulo de Geração de Relatórios para Reuniões (Assembleias).
"""

from apps.meetings.models import RepresentativeMeeting


class AbstractMeetingReport:
    """Classe base abstrata para relatórios de reuniões."""
    column_a = ['A', 'B']
    column_b = ['C', 'G']
    column_c = ['H', 'I']
    row = 6

    def __init__(self, meeting_report, name, task_id):
        self.task_id = task_id
        self.meeting_report = meeting_report
        self.name = name
        from apps.report.models import ReportMeetingToPDF
        self.report = ReportMeetingToPDF(self.meeting_report.id, self.name)


class MeetingReportListRepresentatives(AbstractMeetingReport):
    """Gera relatório listando representantes e seus respectivos credores."""

    def get_representatives(self):
        meeting_id = self.meeting_report.meeting.id
        return RepresentativeMeeting.objects.filter(meeting_id=meeting_id)

    def export(self):
        representatives = self.get_representatives()

        for representative in representatives:
            representative_creditors = representative.get_representatives()
            classes = representative_creditors.values_list('creditor__classe__description', flat=True).distinct()

            if classes:
                for classe in classes:
                    self.set_representative_title()
                    self.row += 1
                    self.set_representative_info(representative, classe)
                    self.row += 2
                    self.set_creditor_title()
                    self.row += 1
                    self.set_creditors_info(representative_creditors, classe)
                    self.row += 1
            else:
                self.set_representative_title()
                self.row += 1
                self.set_representative_info(representative, '')
                self.row += 2
                self.set_creditor_title()

            self.row += 1
            self.report.writer.add_break(self.row)
            self.row += 1

        self.report.export()
        return {'representatives': list(representatives.values_list('id', flat=True))}

    def set_representative_info(self, representative, classe):
        self.report.writer.set_value(self.row, self.column_a, representative.code)
        self.report.writer.set_value(self.row, self.column_b, representative.guest.user.full_name)
        self.report.writer.set_value(self.row, self.column_c, classe)

    def set_representative_title(self):
        font = self.report.writer.STILE.bold_black_font
        self.report.writer.set_value(self.row, self.column_a, 'Código', font=font)
        self.report.writer.set_value(self.row, self.column_b, 'Representante', font=font)
        self.report.writer.set_value(self.row, self.column_c, 'Classe', font=font)

    def set_creditor_title(self):
        font = self.report.writer.STILE.bold_black_font
        self.report.writer.set_value(self.row, self.column_a, 'Código', font=font)
        self.report.writer.set_value(self.row, self.column_b, 'Credor', font=font)
        self.report.writer.set_number(self.row, self.column_c, 'Valor', font=font)

    def set_creditors_info(self, representative_creditors, classe):
        for re_creditor in representative_creditors.filter(creditor__classe__description=classe):
            self.report.writer.set_value(self.row, self.column_a, re_creditor.creditor.code)
            self.report.writer.set_value(self.row, self.column_b, re_creditor.creditor.guest.user.full_name)
            credit_value = self.report.writer.parse_number(re_creditor.creditor.credit_value)
            self.report.writer.set_number(self.row, self.column_c, f'R$ {credit_value}')
            self.row += 1


class MeetingReportListRepresentativesPresent(MeetingReportListRepresentatives):
    """Gera relatório de representantes presentes e seus credores."""

    def get_representatives(self):
        meeting_id = self.meeting_report.meeting.id
        return RepresentativeMeeting.objects.filter(meeting_id=meeting_id, is_accredited=True)


class MeetingReportCreditors(AbstractMeetingReport):
    """Gera relatório listando credores da assembleia."""
    column_a = 'A'
    column_b = ['B', 'D']
    column_c = ['E', 'G']
    column_d = ['H', 'J']
    column_e = 'K'

    def get_creditors(self):
        return self.meeting_report.meeting.creditors

    def export(self):
        creditors = self.get_creditors()
        self.set_creditor_title()
        self.row += 1
        self.set_creditors_info(creditors)
        self.report.export()
        return {'creditors': list(creditors.values_list('id', flat=True))}

    def set_creditor_title(self):
        font = self.report.writer.STILE.bold_black_font
        self.report.writer.set_value(self.row, self.column_a, 'Código', font=font)
        self.report.writer.set_value(self.row, self.column_b, 'Credor', font=font)
        self.report.writer.set_value(self.row, self.column_c, 'Empresa Associada', font=font)
        self.report.writer.set_value(self.row, self.column_d, 'Nome do Credenciador', font=font)
        self.report.writer.set_value(self.row, self.column_e, 'Credenciado', fill_width=10, font=font)

    def set_creditors_info(self, creditors):
        for count, creditor in enumerate(creditors):
            fonte, fill_ = None, None
            if divmod(count, 2)[1] == 0:
                fonte = self.report.writer.STILE.bold_white_font
                fill_ = self.report.writer.STILE.gray_fill

            font_f = {'font': fonte, 'fill': fill_}
            self.report.writer.set_value(self.row, self.column_a, creditor.code, **font_f)
            self.report.writer.set_value(self.row, self.column_b, creditor.guest.user.full_name, fill_width=30, **font_f)
            self.report.writer.set_value(self.row, self.column_c, creditor.recovering.name, fill_width=30, **font_f)
            self.report.writer.set_value(self.row, self.column_d, creditor.get_accredited_name(), fill_width=30, **font_f)
            self.report.writer.set_value(self.row, self.column_e, 'Sim ' if creditor.is_accredited else 'Não', **font_f)
            self.row += 1


class MeetingReportCreditorsPresent(MeetingReportCreditors):
    """Gera relatório de credores presentes e credenciados."""

    def get_creditors(self):
        return self.meeting_report.meeting.creditors.filter(presence__is_accredited=True)


class MeetingReport:
    """Controlador principal para seleção e exportação do tipo de relatório."""

    def __init__(self, meeting_id, report_id, task_id):
        self.report_id = report_id
        self.task_id = task_id
        self.meeting_id = meeting_id
        from apps.report.models import ReportMeeting
        self.meeting_report = ReportMeeting.objects.get(id=report_id)

    def export(self):
        from apps.report.models import ReportMeetingChoices
        report_type = self.meeting_report.report_type

        if report_type == ReportMeetingChoices.LIST_REPRESENTATIVE:
            reporter = MeetingReportListRepresentatives
        elif report_type == ReportMeetingChoices.LIST_REPRESENTATIVE_PRESENT:
            reporter = MeetingReportListRepresentativesPresent
        elif report_type == ReportMeetingChoices.LIST_CREDITORS:
            reporter = MeetingReportCreditors
        elif report_type == ReportMeetingChoices.LIST_CREDITORS_PRESENT:
            reporter = MeetingReportCreditorsPresent
        else:
            raise ValueError(f'Unknown meeting report type {self.meeting_report}')

        return reporter(self.meeting_report, report_type.label, self.task_id).export()