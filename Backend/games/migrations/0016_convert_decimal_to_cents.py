# Generated migration for converting Decimal money to Integer cents in games
from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0015_migrate_to_integer_money'),
    ]

    operations = [
        # Step A: Add temporary fields for data conversion
        migrations.AddField(
            model_name='aposta',
            name='valor_temp',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='aposta',
            name='valor_premio_temp',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='parametrosdojogo',
            name='valor_minimo_para_brinde_temp',
            field=models.BigIntegerField(default=0),
        ),
        
        # Step B: Convert Decimal to cents (RunPython)
        migrations.RunPython(convert_games_decimal_to_cents, reverse_code=convert_games_cents_to_decimal),
        
        # Step C: Remove old Decimal fields and rename temp fields
        migrations.RemoveField(
            model_name='aposta',
            name='valor',
        ),
        migrations.RenameField(
            model_name='aposta',
            old_name='valor_temp',
            new_name='valor',
        ),
        
        migrations.RemoveField(
            model_name='aposta',
            name='valor_premio',
        ),
        migrations.RenameField(
            model_name='aposta',
            old_name='valor_premio_temp',
            new_name='valor_premio',
        ),
        
        migrations.RemoveField(
            model_name='parametrosdojogo',
            name='valor_minimo_para_brinde',
        ),
        migrations.RenameField(
            model_name='parametrosdojogo',
            old_name='valor_minimo_para_brinde_temp',
            new_name='valor_minimo_para_brinde',
        ),
    ]


def convert_games_decimal_to_cents(apps, schema_editor):
    """
    Convert existing Decimal values to integer cents in games models.
    Formula: new_cents = int(decimal_value * 100)
    """
    from django.db import connection
    from games.models import Aposta, ParametrosDoJogo
    
    with connection.cursor() as cursor:
        # Convert Aposta.valor
        cursor.execute("""
            UPDATE games_aposta 
            SET valor_temp = CAST(valor * 100 AS INTEGER)
            WHERE valor IS NOT NULL
        """)
        
        # Convert Aposta.valor_premio
        cursor.execute("""
            UPDATE games_aposta 
            SET valor_premio_temp = CAST(valor_premio * 100 AS INTEGER)
            WHERE valor_premio IS NOT NULL
        """)
        
        # Convert ParametrosDoJogo.valor_minimo_para_brinde
        cursor.execute("""
            UPDATE games_parametrosdojogo 
            SET valor_minimo_para_brinde_temp = CAST(valor_minimo_para_brinde * 100 AS INTEGER)
            WHERE valor_minimo_para_brinde IS NOT NULL
        """)


def convert_games_cents_to_decimal(apps, schema_editor):
    """
    Reverse migration: Convert cents back to Decimal in games models.
    Formula: new_decimal = cents / 100
    """
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Convert Aposta.valor back
        cursor.execute("""
            UPDATE games_aposta 
            SET valor = CAST(valor_temp AS FLOAT) / 100
            WHERE valor_temp IS NOT NULL
        """)
        
        # Convert Aposta.valor_premio back
        cursor.execute("""
            UPDATE games_aposta 
            SET valor_premio = CAST(valor_premio_temp AS FLOAT) / 100
            WHERE valor_premio_temp IS NOT NULL
        """)
        
        # Convert ParametrosDoJogo.valor_minimo_para_brinde back
        cursor.execute("""
            UPDATE games_parametrosdojogo 
            SET valor_minimo_para_brinde = CAST(valor_minimo_para_brinde_temp AS FLOAT) / 100
            WHERE valor_minimo_para_brinde_temp IS NOT NULL
        """)
