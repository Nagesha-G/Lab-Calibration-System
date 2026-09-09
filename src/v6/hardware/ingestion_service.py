from src.v6.hardware.acquisition_service import AcquisitionService
from src.v6.hardware.connection_manager import ConnectionManager


class IngestionService:
    """
    Coordinates instrument connection and measurement ingestion.
    """

    def __init__(
        self,
        connection_manager: ConnectionManager,
        acquisition_service: AcquisitionService,
    ):
        self.connection_manager = connection_manager
        self.acquisition_service = acquisition_service

    def ingest_once(self):
        connected = self.connection_manager.ensure_connected()

        if not connected:
            raise RuntimeError(
                "Unable to establish instrument connection."
            )

        return self.acquisition_service.acquire_once()