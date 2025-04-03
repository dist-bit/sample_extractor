#!/usr/bin/env python3
"""
Nebuia API Client with cURL logging

A comprehensive client for interacting with the Nebuia API that also logs the equivalent cURL commands
for each API request, making it easier to debug, reproduce, or share API interactions.

Author: MIGUEL ANGEL
Date: March 31, 2025
Modified: Added cURL logging functionality
"""

import requests
import json
import time
import logging
import shlex
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("nebuia_client")


# Create a separate logger for cURL commands
curl_logger = logging.getLogger("nebuia_curl")
curl_logger.setLevel(logging.INFO)
curl_formatter = logging.Formatter('%(message)s')

# Create handler for curl logging to file
curl_file_handler = logging.FileHandler("nebuia_curl_commands.log")
curl_file_handler.setFormatter(curl_formatter)
curl_logger.addHandler(curl_file_handler)

# Also add console handler for immediate visibility if needed
curl_console_handler = logging.StreamHandler()
curl_console_handler.setFormatter(curl_formatter)
curl_logger.addHandler(curl_console_handler)


@dataclass
class NebuiaCredentials:
    """Stores and validates Nebuia API credentials."""
    client_id: str
    api_key: str
    api_secret: str
    
    def __post_init__(self):
        """Validate credentials after initialization."""
        if not self.client_id or not self.api_key or not self.api_secret:
            raise ValueError("All credential fields (client_id, api_key, api_secret) are required")


class NebuiaError(Exception):
    """Base exception class for all Nebuia-related errors."""
    pass


class NebuiaApiError(NebuiaError):
    """Exception raised for API errors with status code and details."""
    
    def __init__(self, status_code: int, message: str, response_body: Optional[str] = None):
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(f"API Error ({status_code}): {message}")


class NebuiaClient:
    """
    Client for interacting with the Nebuia API with cURL logging.
    
    Provides comprehensive methods for handling all main operations with the Nebuia API,
    including configuration management, records, documents, and jobs with improved
    error handling and response processing. Now with cURL command logging for each request.
    """
    
    BASE_URL = "https://clients-copilot.nebuia.com"
    DEFAULT_TIMEOUT = 300  # seconds
    
    def __init__(
        self, 
        client_id: str, 
        api_key: str, 
        api_secret: str, 
        timeout: int = DEFAULT_TIMEOUT,
        enable_curl_logging: bool = True,
        curl_log_file: Optional[str] = "nebuia_curl_commands.log",
        curl_log_console: bool = False
    ):
        """
        Initialize the Nebuia client with necessary credentials.
        
        Args:
            client_id (str): Client ID in Nebuia.
            api_key (str): API key for authentication.
            api_secret (str): API secret for authentication.
            timeout (int, optional): Default timeout for requests in seconds. Defaults to 300.
            enable_curl_logging (bool, optional): Whether to log cURL commands. Defaults to True.
            curl_log_file (str, optional): Path to log file for cURL commands. Defaults to "nebuia_curl_commands.log".
            curl_log_console (bool, optional): Whether to also log cURL commands to console. Defaults to True.
        
        Raises:
            ValueError: If any credential is missing or invalid.
        """
        self.credentials = NebuiaCredentials(client_id, api_key, api_secret)
        self.timeout = timeout
        self.headers = {
            "X-API-Key": self.credentials.api_key,
            "X-API-Secret": self.credentials.api_secret,
            "Content-Type": "application/json"
        }
        
        # Headers without Content-Type for file uploads
        self.upload_headers = {
            "X-API-Key": self.credentials.api_key,
            "X-API-Secret": self.credentials.api_secret
        }
        
        # Set session for connection pooling
        self.session = requests.Session()
        
        # Configure cURL logging
        self.enable_curl_logging = enable_curl_logging
        self._setup_curl_logging(curl_log_file, curl_log_console)
        
        logger.info(f"Initialized Nebuia client for client ID: {client_id}")
        if self.enable_curl_logging:
            logger.info(f"cURL logging enabled. Log file: {curl_log_file}")
    
    def _setup_curl_logging(self, log_file: Optional[str], log_console: bool):
        """
        Set up cURL command logging.
        
        Args:
            log_file (str, optional): Path to log file. If None, no file logging.
            log_console (bool): Whether to log to console.
        """
        global curl_logger
        
        # Clear existing handlers
        for handler in curl_logger.handlers[:]:
            curl_logger.removeHandler(handler)
        
        curl_formatter = logging.Formatter('%(message)s')
        
        # Add file handler if log_file is provided
        if log_file:
            file_handler = logging.FileHandler(log_file, mode='a')
            file_handler.setFormatter(curl_formatter)
            curl_logger.addHandler(file_handler)
        
        # Add console handler if log_console is True
        if log_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(curl_formatter)
            curl_logger.addHandler(console_handler)

    
    def _to_curl_command(
        self, 
        method: str, 
        url: str, 
        headers: Dict[str, str], 
        params: Optional[Dict] = None, 
        data: Optional[Dict] = None, 
        files: Optional[Dict] = None
    ) -> str:
        """
        Convert a request to its equivalent cURL command.
        
        Args:
            method (str): HTTP method (GET, POST, etc.).
            url (str): Full URL.
            headers (Dict): Headers dictionary.
            params (Dict, optional): Query parameters. Defaults to None.
            data (Dict, optional): Body data. Defaults to None.
            files (Dict, optional): Files data. Defaults to None.
        
        Returns:
            str: Equivalent cURL command.
        """
        # Start with the base curl command
        command = ['curl', '-X', method.upper()]
        
        # Add URL with query parameters if present
        full_url = url
        if params:
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{query_string}"
        command.append(shlex.quote(full_url))
        
        # Add headers
        for key, value in headers.items():
            command.extend(['-H', shlex.quote(f"{key}: {value}")])
        
        # Add data for non-file requests
        if data and not files:
            if isinstance(data, dict):
                data_str = json.dumps(data)
            else:
                data_str = str(data)
            command.extend(['--data', shlex.quote(data_str)])
        
        # Special handling for file uploads
        # Note: cURL representation for multipart/form-data and file uploads will be simplified
        if files:
            if data:
                for key, value in data.items():
                    command.extend(['-F', shlex.quote(f"{key}={value}")])
            
            for key, file_tuple in files.items():
                filename = file_tuple[0]
                command.extend(['-F', shlex.quote(f"{key}=@{filename}")])
                # Note: This doesn't capture the content type part, but is a good approximation
        
        # Add timeout
        command.extend(['--connect-timeout', str(self.timeout)])
        
        # Return the formatted command
        return ' '.join(command)
    
    def _log_curl_command(self, curl_command: str, operation_name: str):
        """
        Log cURL command with operation context.
        
        Args:
            curl_command (str): The cURL command to log.
            operation_name (str): Name of the operation for context.
        """
        if not self.enable_curl_logging:
            return
        
        # Format timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Format the log entry
        log_entry = f"\n{'=' * 80}\n"
        log_entry += f"OPERATION: {operation_name}\n"
        log_entry += f"TIMESTAMP: {timestamp}\n"
        log_entry += f"CURL COMMAND:\n{curl_command}\n"
        log_entry += f"{'=' * 80}\n"
        
        # Log using curl logger
        curl_logger.info(log_entry)
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None, 
        data: Optional[Dict] = None, 
        files: Optional[Dict] = None,
        custom_headers: Optional[Dict] = None,
        timeout: Optional[int] = None,
        operation_name: Optional[str] = None
    ) -> Dict:
        """
        Make a request to the Nebuia API with error handling and cURL logging.
        
        Args:
            method (str): HTTP method (GET, POST, etc.).
            endpoint (str): API endpoint path (without base URL).
            params (Dict, optional): Query parameters. Defaults to None.
            data (Dict, optional): Request body data. Defaults to None.
            files (Dict, optional): Files to upload. Defaults to None.
            custom_headers (Dict, optional): Custom headers to use instead of default.
                                           Useful for file uploads. Defaults to None.
            timeout (int, optional): Request timeout. Uses instance default if None.
            operation_name (str, optional): Name of the operation for cURL logging. Defaults to None.
        
        Returns:
            Dict: Parsed JSON response.
            
        Raises:
            NebuiaApiError: If the API returns an error status code.
            requests.RequestException: For network-related errors.
        """
        url = f"{self.BASE_URL}{endpoint}"
        headers = custom_headers or self.headers
        request_timeout = timeout or self.timeout
        
        # Determine operation name for logging if not provided
        if not operation_name:
            operation_name = f"{method.upper()} {endpoint}"
        
        # Generate and log cURL command before making the request
        if self.enable_curl_logging:
            curl_command = self._to_curl_command(method, url, headers, params, data, files)
            self._log_curl_command(curl_command, operation_name)
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, params=params, timeout=request_timeout)
            elif method.upper() == "POST":
                if files:
                    # For multipart/form-data requests with files
                    response = self.session.post(
                        url, headers=headers, params=params, data=data, 
                        files=files, timeout=request_timeout
                    )
                else:
                    # For JSON requests
                    response = self.session.post(
                        url, headers=headers, params=params, json=data, 
                        timeout=request_timeout
                    )
            else:
                # Add other methods if needed
                raise ValueError(f"HTTP method {method} not supported")
            
            # Log request information
            logger.debug(f"Request: {method} {url}")
            logger.debug(f"Status: {response.status_code}")
            
            if not response.ok:
                # Try to parse response for error details
                try:
                    error_details = response.json()
                except:
                    error_details = response.text
                
                raise NebuiaApiError(
                    status_code=response.status_code, 
                    message=f"Request failed: {response.reason}", 
                    response_body=error_details
                )
            
            # Return parsed JSON response
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Network error: {str(e)}")
            raise NebuiaError(f"Network error: {str(e)}") from e
    
    # Configuration Management
    
    def create_configuration(self, config_name: str, config_data: Dict) -> Dict:
        """
        Create a new configuration in Nebuia.
        
        Args:
            config_name (str): Name or identifier for the configuration (e.g., "hipotecario").
            config_data (Dict): Configuration data in JSON format.
                Must include title, subtitle, description, endpoint, icon, and documents.
        
        Returns:
            Dict: API response with details of the created configuration.
            
        Raises:
            NebuiaApiError: If the API returns an error.
            NebuiaError: For other Nebuia-specific errors.
        """
        endpoint = f"/clients/{self.credentials.client_id}/configurations/{config_name}"
        logger.info(f"Creating configuration: {config_name}")
        
        # Validate configuration data
        required_fields = ["title", "subtitle", "description", "endpoint", "icon", "documents"]
        missing_fields = [field for field in required_fields if field not in config_data]
        
        if missing_fields:
            raise ValueError(f"Configuration data missing required fields: {', '.join(missing_fields)}")
        
        return self._make_request(
            "POST", 
            endpoint, 
            data=config_data, 
            operation_name=f"Create Configuration: {config_name}"
        )
    
    def get_configuration(self, config_name: str) -> Dict:
        """
        Get details of an existing configuration.
        
        Args:
            config_name (str): Name or identifier of the configuration.
        
        Returns:
            Dict: Configuration details.
        """
        endpoint = f"/clients/{self.credentials.client_id}/configurations/{config_name}"
        logger.info(f"Getting configuration: {config_name}")
        return self._make_request(
            "GET", 
            endpoint, 
            operation_name=f"Get Configuration: {config_name}"
        )
    
    def list_configurations(self, page: int = 1, page_size: int = 50) -> Dict:
        """
        List all configurations for the client.
        
        Args:
            page (int, optional): Page number. Defaults to 1.
            page_size (int, optional): Items per page. Defaults to 50.
        
        Returns:
            Dict: List of configurations with pagination details.
        """
        endpoint = f"/clients/{self.credentials.client_id}/configurations"
        params = {"page": page, "page_size": page_size}
        logger.info(f"Listing configurations (page {page}, size {page_size})")
        return self._make_request(
            "GET", 
            endpoint, 
            params=params, 
            operation_name="List Configurations"
        )
    
    # Record Management
    
    def create_record(self, configuration_ref: str) -> Dict:
        """
        Create a new record associated with a specific configuration.
        
        Args:
            configuration_ref (str): Reference to the configuration for which
                                    the record will be created.
        
        Returns:
            Dict: API response with the created record ID.
            
        Raises:
            NebuiaApiError: If the API returns an error.
            NebuiaError: For other Nebuia-specific errors.
        """
        endpoint = f"/clients/{self.credentials.client_id}/records/create"
        data = {"configuration_ref": configuration_ref}
        logger.info(f"Creating record for configuration: {configuration_ref}")
        return self._make_request(
            "POST", 
            endpoint, 
            data=data, 
            operation_name=f"Create Record for: {configuration_ref}"
        )
    
    def get_record_details(self, record_id: str) -> Dict:
        """
        Get details of a specific record.
        
        Args:
            record_id (str): ID of the record to retrieve.
        
        Returns:
            Dict: API response with record details.
            
        Raises:
            NebuiaApiError: If the API returns an error.
            NebuiaError: For other Nebuia-specific errors.
        """
        endpoint = f"/clients/{self.credentials.client_id}/records/{record_id}"
        logger.info(f"Getting details for record: {record_id}")
        return self._make_request(
            "GET", 
            endpoint, 
            operation_name=f"Get Record Details: {record_id}"
        )
    
    def create_processing_job(
        self, 
        record_id: str
    ) -> Dict:
        """
        Create a processing job for a record that has already been uploaded with documents.
        This endpoint should be called after document type verification to process all documents.
        
        Args:
            record_id (str): ID of the record to process.
        
        Returns:
            Dict: API response containing the job ID and status.
                
        Raises:
            NebuiaApiError: If the API returns an error.
            NebuiaError: For other Nebuia-specific errors.
        """
        endpoint = f"/clients/{self.credentials.client_id}/records/{record_id}/process"
        
        logger.info(f"Creating processing job for record: {record_id}")
        
        return self._make_request(
            "POST", 
            endpoint, 
            data={},  # Empty data payload, record ID is in the URL
            operation_name=f"Create Processing Job for Record: {record_id}"
        )

    def get_document_status(
        self, 
        document_id: str
    ) -> Dict:
        """
        Get the processing status of a document.
        
        Args:
            document_id (str): ID of the document to check status for.
        
        Returns:
            Dict: API response containing the document status.
                Example: {"status": "complete"}
                
        Raises:
            NebuiaApiError: If the API returns an error.
            NebuiaError: For other Nebuia-specific errors.
        """
        # Note that this URL is different from the main API URL
        url = f"https://embeddings-distributor.nebuia.com/document/{document_id}/status"
        
        logger.info(f"Checking status for document: {document_id}")
        
        # Custom implementation for this endpoint since it uses a different base URL
        try:
            response = self.session.get(
                url,
                headers=self.headers,
                timeout=self.timeout
            )
            
            if not response.ok:
                # Try to parse response for error details
                try:
                    error_details = response.json()
                except:
                    error_details = response.text
                
                raise NebuiaApiError(
                    status_code=response.status_code, 
                    message=f"Request failed: {response.reason}", 
                    response_body=error_details
                )
            
            # Return parsed JSON response
            return response.json()
                
        except requests.RequestException as e:
            logger.error(f"Network error: {str(e)}")
            raise NebuiaError(f"Network error: {str(e)}") from e
    
    def list_records(
        self, 
        page: int = 1, 
        page_size: int = 50, 
        status: Optional[str] = None,
        configuration_ref: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> Dict:
        """
        List records with filtering options.
        
        Args:
            page (int, optional): Page number. Defaults to 1.
            page_size (int, optional): Items per page. Defaults to 50.
            status (str, optional): Filter by status (waiting, complete, etc.). Defaults to None.
            configuration_ref (str, optional): Filter by configuration reference. Defaults to None.
            date_from (str, optional): Filter records created after this date (ISO format). Defaults to None.
            date_to (str, optional): Filter records created before this date (ISO format). Defaults to None.
        
        Returns:
            Dict: API response with list of records and pagination details.
            
        Raises:
            NebuiaApiError: If the API returns an error.
            NebuiaError: For other Nebuia-specific errors.
        """
        endpoint = f"/clients/{self.credentials.client_id}/records"
        
        params = {
            "page": page,
            "page_size": page_size
        }
        
        # Add optional filters if provided
        if status:
            params["status"] = status
        
        if configuration_ref:
            params["configuration_ref"] = configuration_ref
        
        if date_from:
            params["date_from"] = date_from
        
        if date_to:
            params["date_to"] = date_to
        
        logger.info(f"Listing records with filters: {params}")
        return self._make_request(
            "GET", 
            endpoint, 
            params=params, 
            operation_name="List Records"
        )
    
    # Document Management

    def verify_document_type(
        self, 
        record_id: str, 
        document_type_id: str,
        timeout: int = 900
    ) -> Dict:
        """
        Verify if a document is of the expected type.
        
        Args:
            record_id (str): ID of the record associated with the document.
            document_type_id (str): ID of the document type to verify.
        
        Returns:
            Dict: API response with verification result.
                Example success response: {"status": true}
                Example failure response: {
                    "status": false,
                    "points": ["Reason 1", "Reason 2", ...],
                    "type_document_found": "actual document type"
                }
                
        Raises:
            NebuiaApiError: If the API returns an error.
            NebuiaError: For other Nebuia-specific errors.
        """
        endpoint = f"/clients/{self.credentials.client_id}/records/{record_id}/type/{document_type_id}"
        
        logger.info(f"Verifying document type {document_type_id} for record {record_id}")
        
        return self._make_request(
            "GET", 
            endpoint,
            timeout=timeout,
            operation_name=f"Verify Document Type: {document_type_id} for Record {record_id}"
        )
    
    def upload_document(
        self, 
        record_id: str, 
        file_path: Union[str, Path], 
        document_type: str,
        timeout: int = 900
    ) -> Dict:
        """
        Upload a document to a specific record.
        
        Args:
            record_id (str): ID of the record to associate the document with.
            file_path (str or Path): Path to the file to upload.
            document_type (str): Type of document according to configuration.
            timeout (int, optional): Upload timeout in seconds. Defaults to 900 (15 minutes).
        
        Returns:
            Dict: API response about the upload result.
            
        Raises:
            FileNotFoundError: If the specified file doesn't exist.
            ValueError: If the file is not a PDF.
            NebuiaApiError: If the API returns an error.
            NebuiaError: For other Nebuia-specific errors.
        """
        endpoint = f"/clients/{self.credentials.client_id}/records/{record_id}/documents"
        
        # Convert string path to Path object for better handling
        file_path = Path(file_path) if isinstance(file_path, str) else file_path
        
        # Verify the file exists
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Verify the file is a PDF
        if file_path.suffix.lower() != '.pdf':
            raise ValueError(f"File must be a PDF: {file_path}")
        
        # Get the file name
        file_name = file_path.name
        
        # Prepare multipart form data with explicit MIME type
        files = {
            "file": (file_name, open(file_path, "rb"), "application/pdf")
        }
        data = {"document_type": document_type}
        
        try:
            logger.info(f"Uploading document {document_type} ({file_path}) to record {record_id}...")
            response = self._make_request(
                "POST", 
                endpoint, 
                data=data, 
                files=files, 
                custom_headers=self.upload_headers,
                timeout=timeout,
                operation_name=f"Upload Document: {document_type} to Record {record_id}"
            )
            logger.info(f"Document upload successful for {document_type}")
            return response
        finally:
            # Ensure file is closed
            if "file" in files and hasattr(files["file"][1], "close"):
                files["file"][1].close()
    
    def list_documents(self, record_id: str) -> Dict:
        """
        List all documents associated with a record.
        
        Args:
            record_id (str): ID of the record.
        
        Returns:
            Dict: List of documents associated with the record.
        """
        endpoint = f"/clients/{self.credentials.client_id}/records/{record_id}/documents"
        logger.info(f"Listing documents for record: {record_id}")
        return self._make_request(
            "GET", 
            endpoint, 
            operation_name=f"List Documents for Record: {record_id}"
        )
    
    # Job Management
    
    def get_jobs_status(
        self, 
        detailed: bool = False, 
        page: int = 1, 
        page_size: int = 50,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> Dict:
        """
        Get jobs status with metrics and filtering options.
        
        Args:
            detailed (bool, optional): Indicate if additional details should be shown. Defaults to False.
            page (int, optional): Page number for pagination. Defaults to 1.
            page_size (int, optional): Size of each page. Defaults to 50.
            status (str, optional): Filter by job status. Defaults to None.
            date_from (str, optional): Filter jobs after this date (ISO format). Defaults to None.
            date_to (str, optional): Filter jobs before this date (ISO format). Defaults to None.
        
        Returns:
            Dict: API response with job status.
            
        Raises:
            NebuiaApiError: If the API returns an error.
            NebuiaError: For other Nebuia-specific errors.
        """
        endpoint = f"/clients/{self.credentials.client_id}/records/jobs/status/metrics"
        
        params = {
            "detailed": str(detailed).lower(),
            "page": page,
            "page_size": page_size
        }
        
        # Add optional filters if provided
        if status:
            params["status"] = status
        
        if date_from:
            params["date_from"] = date_from
        
        if date_to:
            params["date_to"] = date_to
        
        logger.info(f"Getting jobs status with filters: {params}")
        return self._make_request(
            "GET", 
            endpoint, 
            params=params, 
            operation_name="Get Jobs Status"
        )
    
    # Workflow Management
    
    def wait_for_record_completion(
        self, 
        record_id: str, 
        timeout: int = 300, 
        polling_interval: int = 10,
        status_callback: Optional[callable] = None
    ) -> Dict:
        """
        Wait for a record to complete by periodically checking its status.
        
        Args:
            record_id (str): ID of the record to monitor.
            timeout (int, optional): Maximum wait time in seconds. Defaults to 300.
            polling_interval (int, optional): Interval between checks in seconds. Defaults to 10.
            status_callback (callable, optional): Function to call on each status update.
                Function signature: callback(status: str, elapsed_time: float, record_details: Dict)
        
        Returns:
            Dict: Record details once completed.
            
        Raises:
            TimeoutError: If the wait time is exceeded.
            NebuiaApiError: If the API returns an error.
            NebuiaError: For other Nebuia-specific errors.
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            record_details = self.get_record_details(record_id)
            current_status = record_details.get("status", "unknown")
            elapsed_time = time.time() - start_time
            
            if status_callback:
                status_callback(current_status, elapsed_time, record_details)
            else:
                logger.info(f"Record {record_id} status: {current_status} (elapsed: {elapsed_time:.1f}s)")
            
            if current_status == "complete":
                logger.info(f"Record {record_id} completed successfully")
                return record_details
            
            if current_status == "error":
                error_message = record_details.get("error_message", "Unknown error")
                logger.error(f"Record {record_id} failed with error: {error_message}")
                raise NebuiaError(f"Record processing failed: {error_message}")
            
            time.sleep(polling_interval)
        
        logger.error(f"Timeout exceeded for record {record_id}")
        raise TimeoutError(f"Timeout exceeded for record {record_id} after {timeout} seconds")
    
    def process_full_workflow(
        self, 
        configuration_ref: str, 
        document_map: Dict[str, str],
        timeout: int = 900,
        status_callback: Optional[callable] = None
    ) -> Dict:
        """
        Execute the complete workflow: create a record, upload all documents, and wait for completion.
        
        Args:
            configuration_ref (str): Configuration reference.
            document_map (Dict[str, str]): Mapping of document types to file paths.
                Example: {"escritura": "/path/to/escritura.pdf"}
            timeout (int, optional): Maximum wait time for record completion in seconds. Defaults to 900.
            status_callback (callable, optional): Function to call on each status update.
                Function signature: callback(status: str, elapsed_time: float, record_details: Dict)
        
        Returns:
            Dict: Record details once processed completely.
            
        Raises:
            NebuiaError: If an error occurs in any part of the process.
        """
        try:
            # Create the record
            record_response = self.create_record(configuration_ref)
            record_id = record_response.get("id")
            logger.info(f"Record created with ID: {record_id}")
            
            # Upload all documents
            for doc_type, file_path in document_map.items():
                upload_response = self.upload_document(record_id, file_path, doc_type)
                logger.info(f"Document {doc_type} uploaded successfully")
            
            # Wait for the record to complete
            completed_record = self.wait_for_record_completion(
                record_id, 
                timeout=timeout,
                status_callback=status_callback
            )
            
            logger.info(f"Workflow completed successfully for record {record_id}")
            return completed_record
            
        except Exception as e:
            logger.error(f"Error in workflow execution: {str(e)}")
            raise NebuiaError(f"Workflow execution failed: {str(e)}") from e
    
    def process_multiple_records(
        self, 
        configuration_ref: str, 
        document_maps: List[Dict[str, str]],
        concurrent: bool = False,
        max_concurrent: int = 5
    ) -> List[Dict]:
        """
        Process multiple records in sequence or concurrently.
        
        Args:
            configuration_ref (str): Configuration reference.
            document_maps (List[Dict[str, str]]): List of document maps, each mapping
                document types to file paths for a single record.
            concurrent (bool, optional): Whether to process records concurrently. Defaults to False.
            max_concurrent (int, optional): Maximum number of concurrent records if concurrent=True.
                Defaults to 5.
        
        Returns:
            List[Dict]: List of completed record details.
            
        Raises:
            NebuiaError: If an error occurs in any part of the process.
        """
        results = []
        
        if concurrent:
            # For concurrent processing, you would use threading/async
            # This is a placeholder - implementation would depend on requirements
            logger.warning("Concurrent processing not fully implemented yet")
            # Example implementation would use ThreadPoolExecutor
        else:
            # Process records sequentially
            for i, document_map in enumerate(document_maps):
                logger.info(f"Processing record {i+1} of {len(document_maps)}")
                result = self.process_full_workflow(configuration_ref, document_map)
                results.append(result)
        
        return results
    
    def get_record_summary(self, record_id: str) -> Dict:
        """
        Get a summary of a record including its details and associated documents.
        
        Args:
            record_id (str): ID of the record.
        
        Returns:
            Dict: Summary information about the record.
        """
        # Get record details
        record_details = self.get_record_details(record_id)
        
        # Get documents associated with the record
        try:
            documents = self.list_documents(record_id)
        except:
            documents = {"documents": []}
        
        # Combine information
        summary = {
            "record": record_details,
            "documents": documents.get("documents", []),
            "total_documents": len(documents.get("documents", [])),
            "status": record_details.get("status"),
            "configuration_ref": record_details.get("configuration_ref"),
            "created_at": record_details.get("created_at"),
            "completed_at": record_details.get("completed_at")
        }
        
        return summary
    
    def __del__(self):
        """Clean up resources when the client is destroyed."""
        if hasattr(self, 'session'):
            self.session.close()
            