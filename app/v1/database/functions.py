from sqlalchemy import FunctionElement, DateTime
from sqlalchemy.ext.compiler import compiles


class utc_now(FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(utc_now, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"
