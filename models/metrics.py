import logging
logger = logging.getLogger(__name__)

from peewee import DatabaseError

from schemas.metrics import Metrics

from werkzeug.exceptions import InternalServerError
from werkzeug.exceptions import Conflict
from werkzeug.exceptions import Unauthorized

class Metric_Model:
    def __init__(self) -> None:
        """
        """
        self.Metrics = Metrics

    def create(self, uid: str, phone_number: str, operator_name: str, auth_id: str, status: str = None, message: str = None) -> dict:
        """
        """
        try:
            metrics = self.Metrics.create(
                uid= uid,
                phone_number = phone_number,
                status = status,
                operator_name = operator_name,
                message = message,
                auth_id = auth_id
            )

            return {
                "uid": str(metrics.uid),
                "phone_number": metrics.phone_number,
                "dastatusta": metrics.status,
                "operator_name": metrics.operator_name,
                "message": metrics.message,
                "createdAt": metrics.createdAt
            }

        except DatabaseError as err:
            logger.error("FAILED TO CREATE METRICS FOR %s CHECK LOGS" % uid)
            raise InternalServerError(err)

    def find(self, auth_id: str) -> dict:
        """
        """
        try:
            logger.debug("finding metrics for '%s' ..." % auth_id)

            metrics = (
                self.Metrics.select()
                .where(
                    self.Metrics.auth_id == auth_id
                )
                .dicts()
            )

            requested = 0
            failed = 0

            result = []

            for metric in metrics:
                if metric["status"] == "requested":
                    requested += 1
                elif metric["status"] == "failed":
                    failed += 1

                result.append(metric)

            logger.info("- Metrics for '%s' found" % auth_id)

            return {
                "summary": {
                    "total": len(result),
                    "requested": requested,
                    "failed": failed,
                },
                "data": result
            }

        except DatabaseError as err:
            logger.error("FAILED FINDING METRICS FOR %s CHECK LOGS" % auth_id)
            raise InternalServerError(err)

    def update(self, uid: str = None, status: str = None, auth_id: str = None, new_auth_id: str = None) -> bool:
        try:
            """
            """
            if uid and status:
                logger.debug("finding metrics %s ..." % uid)

                metrics = (
                    self.Metrics.select()
                    .where(
                        self.Metrics.uid == uid
                    )
                    .dicts()
                )

                # check for duplicates
                if len(metrics) > 1:
                    logger.error("Multiple metric %s found" % uid)
                    raise Conflict()

                # check for no metric
                if len(metrics) < 1:
                    logger.error("No metric %s found" % uid)
                    raise Unauthorized()

                logger.debug("updating metric %s with status %s ..." % (uid, status))

                upd_metric = (
                    self.Metrics.update(
                        status=status
                    )
                    .where(
                        self.Metrics.uid == uid
                    )
                )

            elif auth_id and new_auth_id:
                logger.debug("updating metrics for auth_id '%s' with new_auth_id '%s' ..." % (auth_id, new_auth_id))

                upd_metric = (
                    self.Metrics.update(
                        auth_id=new_auth_id
                    )
                    .where(
                        self.Metrics.auth_id == auth_id
                    )
                )
                
            upd_metric.execute()

            logger.info("- SUCCESSFULLY UPDATED METRIC")
            
            return True

        except DatabaseError as err:
            logger.error("FAILED UPDATING METRIC CHECK LOGS")
            raise InternalServerError(err)