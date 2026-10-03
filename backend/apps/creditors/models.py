from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class RecoveringCompany(models.Model):
    """Empresa em Recuperação Judicial."""
    name = models.CharField("Nome / Razão Social", max_length=255)  # Corrigido max_length
    cnpj = models.CharField("CNPJ", max_length=18, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Empresa Recuperanda"
        verbose_name_plural = "Empresas Recuperandas"

    def __str__(self):
        return self.name


class CreditorClass(models.TextChoices):
    """Classes de Credores segundo a Lei 11.101/2005."""
    LABOR = 'LABOR', 'Classe I - Trabalhista'
    SECURED = 'SECURED', 'Classe II - Garantia Real'
    UNSECURED = 'UNSECURED', 'Classe III - Quirogratário'
    MICRO_ENTERPRISE = 'MICRO', 'Classe IV - ME / EPP'


class Creditor(models.Model):
    """Credor cadastrado no processo de recuperação."""
    recovering_company = models.ForeignKey(
        RecoveringCompany, 
        on_delete=models.CASCADE, 
        related_name='creditors'
    )
    name = models.CharField("Nome / Razão Social", max_length=255)
    cpf_cnpj = models.CharField("CPF/CNPJ", max_length=18)
    creditor_class = models.CharField("Classe", max_length=20, choices=CreditorClass.choices)
    credit_value = models.DecimalField(
        "Valor do Crédito", 
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    email = models.EmailField("E-mail", blank=True, null=True)
    phone = models.CharField("Telefone", max_length=20, blank=True, null=True)
    
    # Flags de controle e status
    doc_ok = models.BooleanField("Documentação Aprovada", default=False)
    is_deleted = models.BooleanField("Excluído", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Credor"
        verbose_name_plural = "Credores"
        indexes = [
            models.Index(fields=['cpf_cnpj']),
            models.Index(fields=['creditor_class']),
        ]

    def __str__(self):
        return f"{self.name} - {self.get_creditor_class_display()}"


class Representative(models.Model):
    """Representante / Procurador de um ou mais credores."""
    creditor = models.ForeignKey(
        Creditor, 
        on_delete=models.CASCADE, 
        related_name='representatives'
    )
    name = models.CharField("Nome do Representante", max_length=255)
    cpf_cnpj = models.CharField("CPF/CNPJ", max_length=18)
    email = models.EmailField("E-mail")
    phone = models.CharField("Telefone", max_length=20, blank=True, null=True)
    is_power_of_attorney_ok = models.BooleanField("Procuração Válida", default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Representante"
        verbose_name_plural = "Representantes"

    def __str__(self):
        return f"{self.name} (Rep: {self.creditor.name})"