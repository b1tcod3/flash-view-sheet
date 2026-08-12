"""
Excepciones personalizadas para funcionalidad de cruce de datos
"""

class JoinError(Exception):
    """Excepción base para errores de join"""
    def __init__(self, message: str, error_code: str | None = None, details: dict | None = None) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}

class JoinValidationError(JoinError):
    """Error en validación de configuración de join"""

class JoinExecutionError(JoinError):
    """Error durante ejecución del join"""

class MemoryLimitExceededError(JoinError):
    """Límite de memoria excedido"""

class UnsupportedJoinError(JoinError):
    """Tipo de join no soportado"""
