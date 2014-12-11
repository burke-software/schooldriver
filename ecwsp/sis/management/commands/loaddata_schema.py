

from tenant_schemas.management.commands import BaseTenantCommand


class Command(BaseTenantCommand):
    '''
    `loaddata` clone but with schema support. Copied from https://github.com/bernardopires/django-tenant-schemas/issues/152#issuecomment-46078301

    Use like this: `loaddata_schema foot.json --schema=schema_you_want`
    '''
    COMMAND_NAME = 'loaddata'

