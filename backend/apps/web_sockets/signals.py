from django.dispatch import Signal

update_voting_progress_detail = Signal()  # quando a votação em progresso precisa ser atualizada
update_voting_by_meeting_list = Signal()  # quando as votações precisa ser atualizada pelo id da meeting
update_voting_list = Signal()  # quando a votação precisa ser atualizada
update_creditor_detail = Signal()  # quando o credor precisa ser atualizado
update_representative_meeting_detail = Signal()  # quando o representante meeting precisa ser atualizado
update_creditor_list = Signal()  # quando os credores precisam ser atualizados
user_connected = Signal()  # quando o user é conectado ao sockets
user_disconnected = Signal()  # quando o user é desconectado do sockets
voting_start = Signal()  # quando a votação é iniciada
started_update_voting_progress_detail = Signal()  # quando a votação é iniciada
voting_end = Signal()  # quando a votação é encerrada
signal_meeting_detail = Signal()  # quando é necessário atualizar a meeting em progresso
signal_started_sockets = Signal()  # quando é necessário atualizar os users para offline
