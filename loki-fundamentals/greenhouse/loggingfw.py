# Import the function to set the global logger provider from the OpenTelemetry logs module.
from opentelemetry._logs import set_logger_provider

# Import the LoggerProvider and LoggingHandler classes from the OpenTelemetry SDK logs module.
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler, LogRecord

from opentelemetry.exporter.otlp.proto.common._log_encoder import encode_logs

# Import the BatchLogRecordProcessor class from the OpenTelemetry SDK logs export module.
from opentelemetry.sdk._logs.export import  LogExporter, LogExportResult, SimpleLogRecordProcessor

# Import the Resource class from the OpenTelemetry SDK resources module.
from opentelemetry.sdk.resources import Resource

# Import the logging and json module.
import logging, json

from typing import Sequence


from confluent_kafka import Producer




class KafkaLogExporter(LogExporter):
    def __init__(self, kafka_broker):
        self.producer = Producer({'bootstrap.servers': kafka_broker})

    def export(self, batch: Sequence[LogRecord]) -> LogExportResult:
        try:
            serialized_data = encode_logs(batch).SerializeToString()
        except Exception as e:
                print(f"Failed to convert record to json: {e}")
                return LogExportResult.FAILURE
        
        # Send OTLP logs to the otlp kafka receiver (alloy)
        self.producer.produce("otlp", value=serialized_data, callback=self.delivery_callback)
        
        # Send raw json logs to the loki kafka receiver (alloy)
        for record in batch:
            try:
                record = record.__dict__
                print(record, flush=True)
                entry = record["log_record"].to_json()
                print(entry, flush=True)
                self.producer.produce("loki", value=entry, callback=self.delivery_callback)
            except Exception as e:
                print(f"Failed to convert record to json: {e}")
                return LogExportResult.FAILURE

        self.producer.flush()
        return LogExportResult.SUCCESS
    
    def delivery_callback(self,err, msg):
        if err:
            print('%% Message failed delivery: %s\n' % err)
        else:
            print('%% Message delivered to %s [%d] @ %d\n' %
                             (msg.topic(), msg.partition(), msg.offset()))

    def shutdown(self):
        self.producer.flush()


class CustomLogFW:
    """
    CustomLogFW sets up logging using OpenTelemetry with a specified service name and instance ID.
    """
    
    def __init__(self, service_name, instance_id):
        """
        Initialize the CustomLogFW with a service name and instance ID.

        :param service_name: Name of the service for logging purposes.
        :param instance_id: Unique instance ID of the service.
        """
        # Create an instance of LoggerProvider with a Resource object that includes
        # service name and instance ID, identifying the source of the logs.
        self.logger_provider = LoggerProvider(
            resource=Resource.create(
                {
                    "service.name": service_name,
                    "service.instance.id": instance_id,
                }
            )
        )

    def setup_logging(self, kafka_broker="kafka:9092"):
        """
        Set up the logging configuration.

        :return: LoggingHandler instance configured with the logger provider.
        """
        # Set the created LoggerProvider as the global logger provider.
        set_logger_provider(self.logger_provider)

        # Create an instance of OTLPLogExporter with insecure connection.
        # Create an instance of KafkaLogExporter.
        exporter = KafkaLogExporter(kafka_broker=kafka_broker)

        # Add a BatchLogRecordProcessor to the logger provider with the exporter.
        self.logger_provider.add_log_record_processor(SimpleLogRecordProcessor(exporter))

        # Create a LoggingHandler with the specified logger provider and log level set to NOTSET.
        handler = LoggingHandler(level=logging.NOTSET, logger_provider=self.logger_provider)

        return handler
