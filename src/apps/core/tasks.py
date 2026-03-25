from celery import shared_task


@shared_task
def ping_task() -> str:
    """
    Tarea mínima para validar conectividad de Celery/Redis sin depender del dominio de negocio.
    """

    return "pong"

