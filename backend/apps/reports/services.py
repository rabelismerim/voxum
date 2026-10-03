import openpyxl
from decimal import Decimal
from apps.creditors.models import Creditor, RecoveringCompany, CreditorClass

class ExcelImportService:
    """Carrega credores a partir de um ficheiro Excel (.xlsx)."""

    @staticmethod
    def import_creditors_from_excel(file_obj, company_id: int) -> dict:
        company = RecoveringCompany.objects.get(id=company_id)
        wb = openpyxl.load_workbook(file_obj)
        sheet = wb.active

        created_count = 0
        errors = []

        # Assume cabeçalho na linha 1: Nome | CPF/CNPJ | Classe (LABOR/SECURED/UNSECURED/MICRO) | Valor
        for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            if not row or not row[0]:
                continue
            
            try:
                name, cpf_cnpj, creditor_class, credit_value = row[0], str(row[1]), str(row[2]).upper(), row[3]
                
                # Valida classe
                if creditor_class not in CreditorClass.values:
                    errors.append(f"Linha {row_idx}: Classe '{creditor_class}' inválida.")
                    continue

                Creditor.objects.create(
                    recovering_company=company,
                    name=name,
                    cpf_cnpj=cpf_cnpj,
                    creditor_class=creditor_class,
                    credit_value=Decimal(str(credit_value))
                )
                created_count += 1
            except Exception as e:
                errors.append(f"Linha {row_idx}: Erro ao processar - {str(e)}")

        return {
            'imported': created_count,
            'errors': errors
        }