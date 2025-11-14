"""
Excepciones personalizadas para funcionalidad de cruce de datos
"""


class JoinError(Exception):
    """Excepción base para errores de join"""
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}


class JoinValidationError(JoinError):
    """Error en validación de configuración de join"""
    pass


class JoinExecutionError(JoinError):
    """Error durante ejecución del join"""
    pass


class MemoryLimitExceededError(JoinError):
    """Límite de memoria excedido"""
    pass


class UnsupportedJoinError(JoinError):
    """Tipo de join no soportado"""
    pass