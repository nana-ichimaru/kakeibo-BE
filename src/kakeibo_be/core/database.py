import os


def get_database_url() -> str:
    return (
        f"{os.environ['MYSQL_CONNECTION']}://"
        f"{os.environ['MYSQL_USER']}:"
        f"{os.environ['MYSQL_PASSWORD']}@"
        f"{os.environ['MYSQL_HOST']}:"
        f"{os.environ['MYSQL_PORT']}/"
        f"{os.environ['MYSQL_DATABASE']}"
    )