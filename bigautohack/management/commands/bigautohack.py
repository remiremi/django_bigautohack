from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.db.models.loading import get_model


class Command(BaseCommand):
    args = '<model model ...>'
    help = """Alter the database tables to use a big int for primary key.

Nice working solution before this gets properly resolved: https://code.djangoproject.com/ticket/14286"""

    CMD = "ALTER TABLE %(table_name)s ALTER COLUMN %(field_name)s TYPE %(data_type)s;"

    def get_auto_type(self):
        if connection.vendor == 'mysql':
            return "bigint AUTO_INCREMENT"
        elif connection.vendor == 'oracle':
            return "NUMBER(19)"
        elif connection.vendor[:8] == 'postgres':
            return "bigint"
        else:
            raise NotImplemented

    def get_related_type(self):
        if connection.vendor == 'mysql':
            return "bigint"
        elif connection.vendor == 'oracle':
            return "NUMBER(19)"
        elif connection.vendor[:8] == 'postgres':
            return "bigint"
        else:
            raise NotImplemented

    @transaction.atomic()
    def handle(self, *args, **options):
        cursor = connection.cursor()
        for model_path in args:
            cls = get_model(model_path)
            assert cls._meta.has_auto_field, 'Model %s doesn\'t have an auto field'
            param = {
                'table_name': cls._meta.db_table,
                'field_name': cls._meta.pk.column,
                'data_type': self.get_auto_type()
            }
            self.stdout.write("Altering %s" % (cls.__name__))
            cursor.execute(self.CMD % param)

            for related in cls._meta.get_all_related_objects():
                param = {
                    'table_name': related.model._meta.db_table,
                    'field_name': related.field.column,
                    'data_type': self.get_related_type()
                }
                self.stdout.write("  And related field %s.%s" % (related.model.__name__, related.field.name))
                cursor.execute(self.CMD % param)

            for m2m, mod in cls._meta.get_m2m_with_model():
                param = {
                    'table_name': m2m.m2m_db_table(),
                    'field_name': m2m.m2m_column_name(),
                    'data_type': self.get_related_type(),
                }
                self.stdout.write("  And m2m %s (%s.%s)" % (m2m.name, m2m.m2m_db_table(), m2m.m2m_column_name()))
                cursor.execute(self.CMD % param)

            for rel in cls._meta.get_all_related_many_to_many_objects():
                param = {
                    'table_name': rel.field.m2m_db_table(),
                    'field_name': rel.field.m2m_reverse_name(),
                    'data_type': self.get_related_type(),
                }
                self.stdout.write("  And m2m %s (%s.%s)" % (rel.field.m2m_field_name(), rel.field.m2m_db_table(), rel.field.m2m_reverse_name()))
                cursor.execute(self.CMD % param)

            self.stdout.write("")
