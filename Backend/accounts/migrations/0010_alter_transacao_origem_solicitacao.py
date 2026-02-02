from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_alter_solicitacaopagamento_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transacao',
            name='origem_solicitacao',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='transacoes', to='accounts.solicitacaopagamento'),
        ),
    ]
