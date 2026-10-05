"""
Módulo de configuração do Django Admin para os modelos de resultados de votação (ClasseResult e ChoiceResult).

Este módulo define as classes de administração para gerenciar os resultados por classe
e por escolha, incluindo uma ação personalizada para exportar os dados para planilhas do Excel (.xlsx).
"""
import openpyxl
from django.contrib import admin
from django.http import HttpResponse

# Substituído o import genérico anterior por uma referência padrão ou compatível
from django.contrib.admin import ModelAdmin as AbstractAdmin

from apps.voting.big_number.models import ClasseResult, ChoiceResult
from utils import _


@admin.register(ClasseResult)
class ClasseResultAdmin(AbstractAdmin):
    """
    Configuração do painel administrativo para o modelo ClasseResult.
    """
    list_display = (
        'voting', 'classe', 'count_voters', 'count_qualified_creditors', 'count_remaining', 'percentage_voters',
        'percentage_remaining',
        'total_credit_value', 'total_voters_credit_value', 'total_remaining', 'total_percentage_voters',
        'total_percentage_remaining')

    actions = ('export_to_excel',)

    @admin.action(description=_('Exportar os itens selecionados para Excel'))
    def export_to_excel(self, request, queryset):
        """
        Exporta os registros selecionados de ClasseResult para um arquivo Excel (.xlsx).
        """
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': 'attachment; filename="classe_results.xlsx"'},
        )

        workbook = openpyxl.Workbook()

        sheet = workbook.active
        sheet.title = 'Resultados por Classe'

        # Escreve o cabeçalho
        headers = [
            'Voting', 'Classe', 'Total de Votantes', 'Credores Qualificados', 'Restantes',
            'Porcentagem de Votantes', 'Porcentagem Restante', 'Valor Total do Crédito',
            'Valor Total do Crédito dos Votantes', 'Total Restante',
            'Porcentagem Total de Votantes', 'Porcentagem Total Restante'
        ]
        sheet.append(headers)

        # Escreve as linhas de dados
        for classe_result in queryset:
            sheet.append([
                str(classe_result.voting.id),
                classe_result.classe.description,
                classe_result.count_voters,
                classe_result.count_qualified_creditors,
                classe_result.count_remaining,
                classe_result.percentage_voters,
                classe_result.percentage_remaining,
                classe_result.total_credit_value,
                classe_result.total_voters_credit_value,
                classe_result.total_remaining,
                classe_result.total_percentage_voters,
                classe_result.total_percentage_remaining,
            ])

        workbook.save(response)
        return response


@admin.register(ChoiceResult)
class ChoiceResultAdmin(AbstractAdmin):
    """
    Configuração do painel administrativo para o modelo ChoiceResult.
    """
    list_display = (
        'classe_result', 'choice', 'count_voters', 'percentage_voters', 'count_qualified_creditors',
        'total_voters_credit_value', 'total_percentage_voters'
    )

    actions = ['export_to_excel']

    @admin.action(description=_('Exportar os itens selecionados para Excel'))
    def export_to_excel(self, request, queryset):
        """
        Exporta os registros selecionados de ChoiceResult para um arquivo Excel (.xlsx).
        """
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': 'attachment; filename="choice_results.xlsx"'},
        )

        workbook = openpyxl.Workbook()

        sheet = workbook.active
        sheet.title = 'Resultados por Escolha'

        # Escreve o cabeçalho
        headers = [
            'Resultado da Classe', 'Escolha', 'Total de Votantes', 'Porcentagem de Votantes',
            'Credores Qualificados', 'Valor Total do Crédito dos Votantes', 'Porcentagem Total de Votantes'
        ]
        sheet.append(headers)

        # Escreve as linhas de dados
        for choice_result in queryset:
            sheet.append([
                str(choice_result.classe_result.id),
                choice_result.choice.value,
                choice_result.count_voters,
                choice_result.percentage_voters,
                choice_result.count_qualified_creditors,
                choice_result.total_voters_credit_value,
                choice_result.total_percentage_voters,
            ])

        workbook.save(response)
        return response