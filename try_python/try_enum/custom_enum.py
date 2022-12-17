from enum import (
    Enum,
    EnumMeta,
    _EnumDict,
    _is_descriptor,
    _is_dunder,
    _is_private,
    _is_sunder,
    auto,
)

auto = auto  # pylint: disable=self-assigning-variable


class StrEnum(str, Enum):
    """
    Mixin class for using auto()
    """

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        """
        Ref: https://docs.python.org/3/library/enum.html#supported-sunder-names
        Used by auto to get an appropriate value for an enum member
        """
        _ = start, count, last_values

        return name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    @classmethod
    def has_value(cls, value: str) -> bool:
        """Check if the value is in the enum

        Parameters
        ----------
        value : str
            The value to check

        Returns
        -------
        bool
            True if the value is in the enum, False otherwise

        Examples
        --------
        >>> from runway.common.enum import StrEnum
        >>> class MyEnum(StrEnum):
        ...     A = auto()
        ...     B = auto()
        ...     C = auto()
        ...
        >>> MyEnum.has_value('A')
        True
        """
        return value in cls._value2member_map_  # pylint: disable=maybe-no-member


class _EnumDictAuto(_EnumDict):
    """
    Auto create Enum member value all the time
    """

    def __init__(self):
        super().__init__()
        self._member_levels = {}
        self._cls_name = None

    def __setitem__(self, key, value):
        if any(
            (
                _is_private(self._cls_name, key),
                _is_sunder(key),
                _is_dunder(key),
                key in self._member_names,
                key in self._ignore,
                _is_descriptor(value),
            ),
        ):
            super().__setitem__(key, value)
        else:
            super().__setitem__(key, auto())
            self._member_levels[key] = value


class ComparableEnumMeta(EnumMeta):
    """
    Metaclass for Comparable Enum
    """

    @classmethod
    def __prepare__(metacls, cls, bases, **kwds):
        # check that previous enum members do not exist
        metacls._check_for_existing_members_(cls, bases)

        # create the namespace dict
        enum_dict = _EnumDictAuto()
        enum_dict._cls_name = cls  # pylint: disable=protected-access

        # inherit previous flags and _generate_next_value_ function
        _, first_enum = metacls._get_mixins_(cls, bases)
        if first_enum is not None:
            enum_dict["_generate_next_value_"] = getattr(
                first_enum,
                "_generate_next_value_",
                None,
            )

        return enum_dict

    def __new__(metacls, cls, bases, classdict, **kwds):
        enum_class = super().__new__(metacls, cls, bases, classdict, **kwds)
        enum_class._member_levels_ = classdict._member_levels
        for member_name in enum_class._member_names_:
            member = enum_class._member_map_[member_name]
            member._level_ = enum_class._member_levels_[member_name]

        return enum_class


class ComparableStrEnum(StrEnum, metaclass=ComparableEnumMeta):
    """
    ComparableStrEnum is a StrEnum with levels for comparison

    Examples
    --------
    >>> from runway.common.enum import ComparableStrEnum
    >>> class UserRole(ComparableStrEnum):
    ...     admin = 100
    ...     user = 90
    ...     guest = 80
    ...
    >>> UserRole.admin > UserRole.user
    True
    >>> UserRole.admin < UserRole.user
    False
    >>> UserRole.admin == UserRole.admin
    True
    >>> UserRole.admin == "admin"
    True
    >>> UserRole.admin > "user"
    True
    >>> UserRole.admin.level
    100
    """

    def _validate_type_to_compare(self, other) -> "ComparableStrEnum":
        if not isinstance(other, (self.__class__, str)):
            raise TypeError(
                f"Cannot compare {self.__class__.__name__} "
                f"with {other.__class__.__name__}",
            )
        if isinstance(other, str) and not isinstance(other, self.__class__):
            if not self.__class__.has_value(other):
                raise ValueError(
                    f"`{other}` is not a valid value to compare with "
                    f"`{self.__class__.__name__}.{self}`",
                )

        return self.__class__(other)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        if isinstance(other, str):
            return self.name == other
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        other = self._validate_type_to_compare(other)
        return self._level_ < other._level_

    def __le__(self, other):
        other = self._validate_type_to_compare(other)
        return self._level_ <= other._level_

    def __gt__(self, other):
        other = self._validate_type_to_compare(other)
        return self._level_ > other._level_

    def __ge__(self, other):
        other = self._validate_type_to_compare(other)
        return self._level_ >= other._level_

    @property
    def level(self):
        """The level of the Enum member."""
        return self._level_