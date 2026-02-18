
class InstagramAPIError(Exception):
    """Базовая ошибка при работе с внешним Instagram API."""
    pass


class InstagramNotFoundError(InstagramAPIError):
    """Пост существует локально, но не найден во внешнем Instagram API."""
    pass


class InstagramAuthError(InstagramAPIError):
    """Ошибка авторизации (401/403) при обращении к Instagram API."""
    pass
