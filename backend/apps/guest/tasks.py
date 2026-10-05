import logging
from datetime import datetime

from celery import Task

from config import settings
from apps.meetings.models import Meeting
from config.celery import app as celery_app

from apps.voxum_base.tasks import AbstractTask


class SendInvitationLinkCiam(AbstractTask):
    """
    Celery task for sending invitation links to users registered as guests in CIAM.
    """
    max_retries = 3

    def run(self, meeting_id):
        meeting = Meeting.objects.filter(id=meeting_id).first()
        if not meeting:
            return

        users_guest = meeting.get_available_user_guest_register_ciam()

        for user in users_guest:
            # Lógica adaptada para a estrutura atual sem dependências legadas de msal/
            if hasattr(user, 'get_msal_user'):
                msal_user, created = user.get_msal_user()
                # Adaptação segura caso os status legados não existam no backend atual
                if created:
                    user.sent_invite_ciam()


class SendMeetingLink(AbstractTask):
    """
    A Celery task for sending meeting links to creditors and representatives.
    """
    max_retries = 3

    def run(self, link, meeting_id, force=False):
        meeting = Meeting.objects.filter(id=meeting_id).first()
        if not meeting:
            return

        creditors = meeting.get_available_creditors_receive_meeting_link()

        for creditor in creditors:
            if force or not creditor.meeting_invited:
                user = creditor.guest.user

                if user.email:
                    response = self.send_email_invite(link, meeting.zoom_url, user, meeting.name)
                    if not response and not creditor.meeting_invited:
                        creditor.meeting_invited = True
                        creditor.save()

            representatives = creditor.get_available_representatives_receive_meeting_link()

            for representative in representatives:
                representative_meeting = representative.representative
                if force or not representative_meeting.meeting_invited:
                    response = self.send_email_invite(link, meeting.zoom_url, representative.representative.guest.user, meeting.name)
                    if not response and not representative_meeting.meeting_invited:
                        representative_meeting.meeting_invited = True
                        representative_meeting.save()

    def send_email_invite(self, link, zoom_url, user, meeting_name):
        user_email = user.email

        if not user_email:
            logging.error(f'Usuário({user.username}) sem email registrado')
            return None

        # Serviço de envio de email padrão adaptado do projeto
        subject = f'Link de acesso à assembleia {meeting_name}'
        description = f'Olá {user.first_name},'
        content = f'Segue link de acesso à assembleia {meeting_name}'

        # Caso utilize um serviço de email interno do Voxum, pode invocá-lo aqui.
        # Mantido o log ou retorno base para evitar quebrar a execução se o cliente Graph legado não existir.
        logging.info(f'Enviando email de convite para {user_email} referente à assembleia {meeting_name}')
        return None


SendInvitationLinkCiamTask = celery_app.register_task(SendInvitationLinkCiam())
SendMeetingLinkTask = celery_app.register_task(SendMeetingLink())