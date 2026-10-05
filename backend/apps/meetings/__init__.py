"""
Módulo de Assembleia

O módulo de assembleia é um conjunto de classes e funcionalidades relacionadas à organização e gerenciamento de
assembleias. Ele fornece modelos para representar assembleias, grupos de assembleias, representantes associados a
 assembleias
e associações entre usuários e assembleias. Além disso, inclui funcionalidades para despachar eventos em resposta a
ações específicas durante uma assembleia.

Funcionalidades Principais
Modelos
Classe (Classe):

Representa uma classe para credores.
Grupo de Assembleia (MeetingGroup):

Representa um grupo de assembleias.
Assembleia (Meeting):

Representa uma assembleia ou assembleia.
Contém informações como nome, local, data de início e fim, status e se atingiu o quorum.
Representante da Assembleia (RepresentativeMeeting):

Representa um representante associado a uma assembleia.
Usuário da Assembleia (UserMeeting):

Representa a associação entre usuários e assembleias.
Sinais (Signals)
Os sinais são usados para despachar eventos em resposta a ações específicas. Eles estão configurados para despachar
tarefas relevantes em determinados pontos durante uma assembleia.
Utilidades
O módulo inclui utilidades para calcular estatísticas sobre a presença de credores, seus votos e outros detalhes
relevantes durante uma assembleia.
"""
