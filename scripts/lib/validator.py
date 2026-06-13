import json
import os
from jsonschema import validate, ValidationError as JsonSchemaValidationError
from scripts.lib.logger import setup_logger, ErrorCategory

logger = setup_logger("validator")

class RecordValidator:
    def __init__(self):
        self.schemas = {}
        schema_dir = "schemas"
        if os.path.exists(schema_dir):
            for file in os.listdir(schema_dir):
                if file.endswith(".schema.json"):
                    with open(os.path.join(schema_dir, file), "r", encoding="utf-8") as f:
                        name = file.split(".")[0]
                        self.schemas[name] = json.load(f)

    def validate_record(self, record: dict, schema_name: str) -> bool:
        if schema_name not in self.schemas:
            logger.error(f"Schema {schema_name} not found", extra={"error_category": ErrorCategory.SCHEMA_ERROR.value})
            return False

        try:
            validate(instance=record, schema=self.schemas[schema_name])
            
            # Additional traceability enforcement
            required_fields = ["source_url", "source_name", "retrieval_timestamp", "unique_id", "schema_version"]
            for field in required_fields:
                if field not in record:
                    logger.error(
                        f"Missing traceability field: {field}", 
                        extra={"error_category": ErrorCategory.VALIDATION_ERROR.value, "extra_fields": {"record_id": record.get("unique_id", "unknown")}}
                    )
                    return False
                    
            return True
        except JsonSchemaValidationError as e:
            logger.error(
                f"Validation failed: {str(e)}", 
                extra={"error_category": ErrorCategory.VALIDATION_ERROR.value, "extra_fields": {"record_id": record.get("unique_id", "unknown")}}
            )
            return False
