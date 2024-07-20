from .types import ConvertibleToWhere


class BaseFilterModel():
    """
    For Base models, provide 'to_where_statement'
    """

    def to_where_statement(self) -> ConvertibleToWhere:
        raise NotImplementedError()
