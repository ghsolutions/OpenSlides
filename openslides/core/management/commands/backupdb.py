from optparse import make_option  # TODO: Use argpase in Django 1.8
import shutil

from django.core.management.base import NoArgsCommand, CommandError
from django.db import connection, transaction

from openslides.utils.main import get_database_path_from_settings


class Command(NoArgsCommand):
    """
    Commands to create or reset the adminuser
    """
    option_list = NoArgsCommand.option_list + (
        make_option('--path', dest='path'),
    )

    def handle_noargs(self, **options):
        path = options.get('path')

        @transaction.atomic
        def do_backup(src_path, dest_path):
            # perform a simple file-copy backup of the database
            # first we need a shared lock on the database, issuing a select()
            # will do this for us
            cursor = connection.cursor()
            cursor.execute("SELECT count(*) from sqlite_master")
            # now copy the file
            try:
                shutil.copy(src_path, dest_path)
            except IOError:
                # TODO: use the IOError message as message for the user
                raise CommandError("Database backup failed.")

        database_path = get_database_path_from_settings()
        if database_path:
            do_backup(database_path, path)
            self.stdout.write('Database %s successfully stored at %s.' % (database_path, path))
        else:
            raise CommandError(
                'Default database is not SQLite3. Only SQLite3 databases'
                'can currently be backuped.')
