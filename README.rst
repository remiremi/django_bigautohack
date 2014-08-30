Django BigAuto Hack
===================

`Support for BigAutoField <https://code.djangoproject.com/ticket/14286>`_ has been a work in progress for 4 years now. But the ticket has the following valuable comment:

    In the meantime, it suffices to use a standard AutoField and hack the database like so:
    In the table in question, alter the field like so: ``ALTER TABLE [table_name] ALTER COLUMN [field_name] [data_type]``, where ``[data_type]`` is one of the following:
    - MySQL: bigint AUTO_INCREMENT
    - Oracle: NUMBER(19)
    - PostgreSQL: bigserial
    - SQLite: integer
    For every foreign key pointing to your field, you will also need to alter the column, but with these data types:
    - MySQL: bigint
    - Oracle: NUMBER(19)
    - PostgreSQL: bigint
    - SQLite: integer
    This is a pain, but you only need to do it when creating tables, once. On the other hand, users shouldn't have to hack the database for such a simple feature, in my opinion. It would be super-cool if 1.3 included a fully-functional BigAutoField.

This simple django app makes this hack less of pain. Running

::

    $ python manage.py myapp.MyModel

Will run the needed ``ALTER TABLE`` commands, turning the database column for ``MyModel``'s primary key into a big integer, as well as all columns referencing ``MyModel``.

Limitation
==========

You probably need to make generic foreign keys use a big integers as well.
