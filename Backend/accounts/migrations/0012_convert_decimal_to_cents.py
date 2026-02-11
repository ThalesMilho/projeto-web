# Generated migration for converting Decimal money to Integer cents
from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_migrate_to_integer_money'),
    ]

    operations = [
        # Step A: Add temporary fields for data conversion
        migrations.AddField(
            model_name='customuser',
            name='saldo_temp',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='solicitacaopagamento',
            name='valor_temp',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='transacao',
            name='saldo_anterior_temp',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='transacao',
            name='saldo_posterior_temp',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='transacao',
            name='valor_temp',
            field=models.BigIntegerField(default=0),
        ),
        
        # Step B: Convert Decimal to cents (RunPython)
        migrations.RunPython(convert_decimal_to_cents, reverse_code=convert_cents_to_decimal),
        
        # Step C: Remove old Decimal fields and rename temp fields
        migrations.RemoveField(
            model_name='customuser',
            name='saldo',
        ),
        migrations.RenameField(
            model_name='customuser',
            old_name='saldo_temp',
            new_name='saldo',
        ),
        
        migrations.RemoveField(
            model_name='solicitacaopagamento',
            name='valor',
        ),
        migrations.RenameField(
            model_name='solicitacaopagamento',
            old_name='valor_temp',
            new_name='valor',
        ),
        
        migrations.RemoveField(
            model_name='transacao',
            name='saldo_anterior',
        ),
        migrations.RenameField(
            model_name='transacao',
            old_name='saldo_anterior_temp',
            new_name='saldo_anterior',
        ),
        
        migrations.RemoveField(
            model_name='transacao',
            name='saldo_posterior',
        ),
        migrations.RenameField(
            model_name='transacao',
            old_name='saldo_posterior_temp',
            new_name='saldo_posterior',
        ),
        
        migrations.RemoveField(
            model_name='transacao',
            name='valor',
        ),
        migrations.RenameField(
            model_name='transacao',
            old_name='valor_temp',
            new_name='valor',
        ),
    ]


def convert_decimal_to_cents(apps, schema_editor):
    """
    Convert existing Decimal values to integer cents.
    Formula: new_cents = int(decimal_value * 100)
    """
    from django.db import connection
    from accounts.models import CustomUser, SolicitacaoPagamento, Transacao
    
    with connection.cursor() as cursor:
        # Convert CustomUser.saldo
        cursor.execute("""
            UPDATE accounts_customuser 
            SET saldo_temp = CAST(saldo * 100 AS INTEGER)
            WHERE saldo IS NOT NULL
        """)
        
        # Convert SolicitacaoPagamento.valor
        cursor.execute("""
            UPDATE accounts_solicitacaopagamento 
            SET valor_temp = CAST(valor * 100 AS INTEGER)
            WHERE valor IS NOT NULL
        """)
        
        # Convert Transacao fields
        cursor.execute("""
            UPDATE accounts_transacao 
            SET saldo_anterior_temp = CAST(saldo_anterior * 100 AS INTEGER),
                saldo_posterior_temp = CAST(saldo_posterior * 100 AS INTEGER),
                valor_temp = CAST(valor * 100 AS INTEGER)
            WHERE saldo_anterior IS NOT NULL 
               OR saldo_posterior IS NOT NULL 
               OR valor IS NOT NULL
        """)


def convert_cents_to_decimal(apps, schema_editor):
    """
    Reverse migration: Convert cents back to Decimal.
    Formula: new_decimal = cents / 100
    """
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Convert CustomUser.saldo back
        cursor.execute("""
            UPDATE accounts_customuser 
            SET saldo = CAST(saldo_temp AS FLOAT) / 100
            WHERE saldo_temp IS NOT NULL
        """)
        
        # Convert other fields back
        cursor.execute("""
            UPDATE accounts_solicitacaopagamento 
            SET valor = CAST(valor_temp AS FLOAT) / 100
            WHERE valor_temp IS NOT NULL
        """)
        
        cursor.execute("""
            UPDATE accounts_transacao 
            SET saldo_anterior = CAST(saldo_anterior_temp AS FLOAT) / 100,
                saldo_posterior = CAST(saldo_posterior_temp AS FLOAT) / 100,
                valor = CAST(valor_temp AS FLOAT) / 100
            WHERE saldo_anterior_temp IS NOT NULL 
               OR saldo_posterior_temp IS NOT NULL 
               OR valor_temp IS NOT NULL
        """)
