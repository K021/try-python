from try_python.try_enum.custom_enum import (
    StrEnum,
    ComparableStrEnum,
    auto,
)

class DatabaseType(StrEnum):
    postgres = auto()
    mysql = auto()
    sqlite = auto()


class UserRole(ComparableStrEnum):
    admin = 100
    user = 90
    guest = 80


def test_str_enum():
    assert DatabaseType.postgres == "postgres"
    assert DatabaseType.postgres == DatabaseType.postgres
    assert DatabaseType.postgres != DatabaseType.mysql
    assert DatabaseType.postgres != "mysql"


def test_comparable_str_enum():
    assert UserRole.admin > UserRole.user
    assert (UserRole.admin < UserRole.user) is False
    assert UserRole.admin == UserRole.admin
    assert UserRole.admin == "admin"
    assert UserRole.admin > "user"
    assert UserRole.admin.level == 100

