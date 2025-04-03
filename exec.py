#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Nebuia Client Module

A client module for interacting with the Nebuia API for document processing,
verification, and information extraction.
"""

import logging
import time
from pathlib import Path
from pprint import pprint
from typing import Dict, Optional, List, Tuple

from nebuia_client import NebuiaClient, NebuiaError


class NebuiaHandler:
    """Handler for Nebuia API operations with improved structure and error handling."""

    def __init__(self, client_id: str, api_key: str, api_secret: str, log_level=logging.INFO):
        """
        Initialize the Nebuia handler with client credentials.
        
        Args:
            client_id: Client ID for Nebuia API
            api_key: API key for Nebuia API
            api_secret: API secret for Nebuia API
            log_level: Logging level (default: logging.INFO)
        """
        # Set up logging
        self.logger = self._setup_logging(log_level)
        
        # Initialize the Nebuia client
        self.client = NebuiaClient(
            client_id=client_id,
            api_key=api_key,
            api_secret=api_secret
        )
        
        self.logger.info("NebuiaHandler initialized successfully")

    def _setup_logging(self, log_level: int) -> logging.Logger:
        """
        Set up logging for the Nebuia handler.
        
        Args:
            log_level: Logging level
            
        Returns:
            Logger instance
        """
        logger = logging.getLogger("nebuia_handler")
        
        # Configure logging if not already configured
        if not logger.handlers:
            logging.basicConfig(
                level=log_level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler("nebuia.log"),
                    logging.StreamHandler()
                ]
            )
        
        return logger

    def status_callback(self, status: str, elapsed_time: float, record_details: Dict) -> None:
        """
        Callback function to handle status updates during record processing.
        
        Args:
            status: Current status of the record
            elapsed_time: Time elapsed since the start of processing (in seconds)
            record_details: Complete record details from the API
        """
        # Get record and job status
        record_status = status
        is_processing = record_details.get("is_processing", False)
        
        # Define emojis for statuses
        status_emoji = {
            "waiting": "⏳",
            "processing": "🔄",
            "complete": "✅",
            "error": "❌",
            "unknown": "❓"
        }.get(record_status, "❓")
        
        # Define job status indicator
        job_status = "JOBS RUNNING" if is_processing else "NO JOBS RUNNING"
        job_emoji = "⚙️" if is_processing else "🔍"
        
        # Format elapsed time nicely
        minutes, seconds = divmod(int(elapsed_time), 60)
        time_str = f"{minutes}m {seconds}s"
        
        # Print status with clear distinction between record status and job status
        print(f"{status_emoji} Record Status: {record_status.upper()} | {job_emoji} Jobs: {job_status} | Elapsed: {time_str} ")
        
        # Additional job details if available
        current_document = record_details.get("current_document_id")
        if current_document:
            print(f"   Currently Processing Document: {current_document}")

    def validate_documents(self, documents: Dict[str, str]) -> Dict[str, str]:
        """
        Validate that all documents exist and have the correct format.

        Args:
            documents: Dictionary mapping document types to file paths

        Returns:
            Dictionary with only valid documents
        """
        valid_documents = {}

        for doc_type, file_path in documents.items():
            path = Path(file_path)

            if not path.exists():
                self.logger.warning(f"❌ Document not found: {file_path}")
                continue

            if path.suffix.lower() != '.pdf':
                self.logger.warning(f"❌ Document is not a PDF: {file_path}")
                continue

            valid_documents[doc_type] = str(path)
            self.logger.info(f"✅ Validated document: {doc_type} - {path.name}")

        return valid_documents
    
    def _display_verification_points(self, result):
        """
        Muestra los puntos de verificación de documentos de forma destacada y legible.
        
        Args:
            result (dict): Resultado de la verificación del tipo de documento
        """
        # Verificar si hay puntos en el resultado
        if "points" in result and result["points"]:
            # Determinar el estatus general
            status = result.get("status", False)
            status_icon = "✅" if status else "❌"
            status_text = "VERIFICACIÓN EXITOSA" if status else "VERIFICACIÓN FALLIDA"
            
            # Imprimir encabezado con el estatus
            print(f"\n{status_icon} {status_text} {status_icon}")
            print("=" * 60)
            
            # Determinar el tipo de documento encontrado
            doc_type = result.get("type_document_found", "desconocido")
            print(f"📄 Tipo de documento: {doc_type}")
            
            # Mostrar los puntos de verificación con números y formato destacado
            print("\n🔍 CRITERIOS DE VERIFICACIÓN:")
            print("-" * 60)
            
            for i, point in enumerate(result["points"]):
                point_num = f"{i+1:02d}"  # Formato de número con padding (01, 02, etc.)
                print(f"  {point_num}. {point}")
            
            print("-" * 60)

    def verify_document_type(self, record_id: str, document_type_id: str) -> Tuple[bool, Dict]:
        """
        Verify if a document is of the expected type.

        Args:
            record_id: ID of the record associated with the document
            document_type_id: ID of the document type to verify

        Returns:
            Tuple of (verification success, verification details)
        """
        try:
            self.logger.info(f"Verifying document type {document_type_id} for record {record_id}")

            result = self.client.verify_document_type(record_id, document_type_id)
            verification_passed = result.get("status") is True

            self._display_verification_points(result)

            return verification_passed, result

        except Exception as e:
            self.logger.error(f"❌ Error verifying document type: {str(e)}")
            return False, {"status": False, "error": str(e)}

    def process_documents(
        self,
        documents: Dict[str, str], 
        config_name: str,
        wait_for_completion: bool = True,
        timeout: int = 300,
        auto_process: bool = True,
        status_check_interval: int = 5,
        status_check_timeout: int = 180
    ) -> Optional[Dict]:
        """
        Create a record, upload documents, verify and process them.
        
        Args:
            documents: Dictionary mapping document types to file paths
            config_name: Configuration name in Nebuia
            wait_for_completion: Whether to wait for the record to complete processing
            timeout: Maximum wait time in seconds if waiting for completion
            auto_process: Whether to automatically create a job if document types are verified
            status_check_interval: Interval in seconds between document status checks
            status_check_timeout: Maximum time in seconds to wait for documents to be processed
        
        Returns:
            Completed record details if wait_for_completion is True, otherwise the created record
        """
        try:
            # Validate documents before starting
            valid_documents = self.validate_documents(documents)
            
            if not valid_documents:
                self.logger.error("No valid documents found. Aborting.")
                return None
            
            # Create record and upload documents
            record_details = self._create_and_upload(valid_documents, config_name)
            if not record_details:
                return None
                
            record_id = record_details["id"]
            document_ids = record_details["document_ids"]
            
            # Wait for documents to be embedded
            embedding_success = self._wait_for_embedding(
                document_ids, 
                status_check_interval, 
                status_check_timeout
            )
            
            if not embedding_success:
                return self.client.get_record_details(record_id)
            
            # Verify all document types
            verification_results, verification_passed = self._verify_all_documents(
                record_id, document_ids
            )
            
            # Get updated record with verification results
            record_details = self.client.get_record_details(record_id)
            record_details["verification_results"] = verification_results
            
            # Process documents if verification passed
            if auto_process and verification_passed:
                return self._process_record(
                    record_id, 
                    verification_results, 
                    wait_for_completion, 
                    timeout
                )
            else:
                if not verification_passed:
                    self.logger.warning("Document type verification failed. Job not created.")
                    print("\n⚠️ Processing job NOT created due to document type verification failures.")
                elif not auto_process:
                    self.logger.info("Auto-processing disabled. Job not created.")
                    print("\n⚠️ Processing job NOT created (auto-processing disabled).")
                
                # Return record details with verification results
                return record_details
                
        except Exception as e:
            self.logger.error(f"❌ Unexpected error: {str(e)}", exc_info=True)
            return None

    def _create_and_upload(
        self, 
        documents: Dict[str, str], 
        config_name: str
    ) -> Optional[Dict]:
        """
        Create a record and upload documents.
        
        Args:
            documents: Dictionary of validated documents
            config_name: Configuration name in Nebuia
            
        Returns:
            Dictionary with record_id and document_ids or None on failure
        """
        # Create a new record
        self.logger.info(f"Creating record for configuration: {config_name}")
        record_response = self.client.create_record(config_name)
        record_id = record_response.get("id")
        
        if not record_id:
            self.logger.error("Failed to get record ID from response")
            return None
            
        self.logger.info(f"✅ Record created with ID: {record_id}")
        
        # Upload all documents
        document_ids = {}  # Track document IDs for verification
        
        for doc_type, file_path in documents.items():
            try:
                upload_response = self.client.upload_document(record_id, file_path, doc_type)
                self.logger.info(f"✅ Document {doc_type} uploaded successfully")
                
                # Get the document details from record to find document_id
                record_details = self.client.get_record_details(record_id)
                for document in record_details.get("documents", []):
                    if document.get("document_type") == doc_type:
                        document_ids[doc_type] = document.get("document_id")
                        break
                
            except Exception as e:
                self.logger.error(f"❌ Failed to upload document {doc_type}: {str(e)}")
        
        if not document_ids:
            self.logger.error("No documents were successfully uploaded.")
            return None
            
        return {"id": record_id, "document_ids": document_ids}

    def _wait_for_embedding(
        self, 
        document_ids: Dict[str, str], 
        check_interval: int, 
        timeout: int
    ) -> bool:
        """
        Wait for all documents to be processed by the embeddings engine.
        
        Args:
            document_ids: Dictionary mapping document types to document IDs
            check_interval: Interval in seconds between status checks
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if all documents were processed successfully, False otherwise
        """
        self.logger.info("Waiting for documents to be processed by embeddings engine...")
        print("\n--- DOCUMENT EMBEDDING PROCESSING ---")
        
        start_time = time.time()
        all_documents_processed = False
        
        while time.time() - start_time < timeout:
            pending_documents = []
            
            for doc_type, doc_id in document_ids.items():
                try:
                    doc_status = self.client.get_document_status(doc_id)
                    status = doc_status.get("status")
                    
                    if status != "complete":
                        pending_documents.append((doc_type, doc_id, status))
                except Exception as e:
                    self.logger.error(f"❌ Error checking status for document {doc_type}: {str(e)}")
                    pending_documents.append((doc_type, doc_id, "error"))
            
            if not pending_documents:
                all_documents_processed = True
                break
            
            # Print current status
            print(f"\rWaiting for {len(pending_documents)} documents to complete processing... ", end="")
            
            # Sleep before checking again
            time.sleep(check_interval)
        
        print("")  # New line after progress output
        
        if not all_documents_processed:
            self.logger.error(f"Timeout waiting for documents to be processed.")
            print("\n❌ Timeout while waiting for document embedding processing to complete.")
            return False
        
        self.logger.info("All documents have been processed by the embeddings engine.")
        print("✅ All documents have been processed by the embeddings engine.")
        return True

    def _verify_all_documents(
        self, 
        record_id: str, 
        document_ids: Dict[str, str]
    ) -> Tuple[Dict, bool]:
        """
        Verify all document types.
        
        Args:
            record_id: ID of the record
            document_ids: Dictionary mapping document types to document IDs
            
        Returns:
            Tuple of (verification results, overall pass/fail)
        """
        verification_results = {}
        verification_passed = True
        
        print("\n--- DOCUMENT TYPE VERIFICATION ---")
        for doc_type, doc_id in document_ids.items():
            if doc_id:
                self.logger.info(f"Verifying document type for {doc_type} (ID: {doc_id})")
                try:
                    is_valid, verification = self.verify_document_type(record_id, doc_id)
                    verification_results[doc_type] = verification
                    
                    if not is_valid:
                        verification_passed = False
                            
                except Exception as e:
                    self.logger.error(f"❌ Error verifying document type for {doc_type}: {str(e)}")
                    verification_results[doc_type] = {"status": False, "error": str(e)}
                    verification_passed = False
        
        return verification_results, verification_passed

    def _process_record(
        self, 
        record_id: str, 
        verification_results: Dict, 
        wait_for_completion: bool, 
        timeout: int
    ) -> Dict:
        """
        Create a job to process the record and optionally wait for completion.
        
        Args:
            record_id: ID of the record
            verification_results: Results of document type verification
            wait_for_completion: Whether to wait for processing to complete
            timeout: Maximum time to wait in seconds
            
        Returns:
            Record details with verification results
        """
        self.logger.info("All document types verified successfully. Creating processing job...")
        try:
            # Call the method to create a processing job
            job_response = self.client.create_processing_job(record_id)
            job_id = job_response.get("job_id")
            
            print(f"✅ Processing job created: {job_id}")
            print(f"   Status: {job_response.get('status')}")
            print(f"   Message: {job_response.get('message')}")
            
            # If waiting for completion is requested, do that
            if wait_for_completion:
                self.logger.info(f"Waiting for record {record_id} to complete (timeout: {timeout}s)")
                try:
                    completed_record = self.client.wait_for_record_completion(
                        record_id, 
                        timeout=timeout,
                        status_callback=self.status_callback
                    )
                    self.logger.info("✅ Record processing completed successfully")
                    
                    # Add verification results
                    completed_record["verification_results"] = verification_results
                    
                    return completed_record
                except TimeoutError as e:
                    self.logger.error(f"⏱️ Timeout waiting for record completion: {str(e)}")
                except NebuiaError as e:
                    self.logger.error(f"❌ Error during record processing: {str(e)}")
        except Exception as e:
            self.logger.error(f"❌ Failed to create processing job: {str(e)}")
        
        # Return current record details if waiting failed or wasn't requested
        record_details = self.client.get_record_details(record_id)
        record_details["verification_results"] = verification_results
        return record_details

    def extract_document_entities(self, record_result: Dict) -> Dict[str, List[Dict]]:
        """
        Extract relevant information from document entities.

        Args:
            record_result: The complete record result from Nebuia API

        Returns:
            Dictionary with document types as keys and lists of cleaned entity structures as values
        """
        extracted_info = {}

        # Check if documents exist in the result
        if not record_result or 'documents' not in record_result:
            self.logger.warning("No documents found in the result")
            return extracted_info

        # Process each document
        for document in record_result['documents']:
            doc_type = document.get('document_type', 'unknown')
            entities = document.get('entities', [])

            # Initialize list for this document type
            if doc_type not in extracted_info:
                extracted_info[doc_type] = []

            # Process each entity in the document
            for entity in entities:
                if 'structure' in entity:
                    # Create a copy of the structure
                    structure = entity['structure'].copy()

                    # Remove the name_to_show field if it exists
                    if 'name_to_show' in structure:
                        del structure['name_to_show']

                    # Add the cleaned structure to the results
                    extracted_info[doc_type].append(structure)

        return extracted_info

    def list_configurations(self) -> None:
        """List available configurations with detailed information."""
        try:
            self.logger.info("Listing available configurations")
            configs = self.client.list_configurations()

            print("\n" + "=" * 80)
            print("AVAILABLE CONFIGURATIONS")
            print("=" * 80)

            if configs:
                # Iterate through configurations
                for i, (config_name, config_data) in enumerate(configs.items()):
                    print(f"\n{i+1}. {config_name} - {config_data.get('title', 'No Title')}")
                    print(f"   Description: {config_data.get('description', 'No Description')}")
                    print(f"   Subtitle: {config_data.get('subtitle', 'No Subtitle')}")

                    # Display document types
                    documents = config_data.get('documents', {})
                    if documents:
                        doc_types = list(documents.keys())
                        print(f"   Document types: {', '.join(doc_types)}")

                        # Display required documents
                        required_docs = [doc for doc, info in documents.items()
                                        if info.get('required', False)]
                        if required_docs:
                            print(f"   Required documents: {', '.join(required_docs)}")

                        # For each document type, show entities to be extracted
                        print("\n   Document details:")
                        for doc_type, doc_info in documents.items():
                            print(f"   - {doc_type}: {doc_info.get('title', 'No Title')}")

                            # Show number of entities to extract
                            entities = doc_info.get('entities', [])
                            if entities:
                                entity_names = [e.get('name_to_show', 'Unnamed') for e in entities]
                                print(f"     Entities ({len(entities)}): {', '.join(entity_names)}")

                    print("\n" + "-" * 80)
            else:
                print("No configurations found")

        except Exception as e:
            self.logger.error(f"❌ Error listing configurations: {str(e)}")


def main():
    """Main function to demonstrate the usage of NebuiaHandler."""
    print("\n" + "=" * 70)
    print("📋 NEBUIA CLIENT EXAMPLE SCRIPT")
    print("=" * 70)

    # Initialize the Nebuia handler
    handler = NebuiaHandler(
        client_id="67d1*********193a7f",
        api_key="34RMXYA-*******-*******-17CZNF8",
        api_secret="c98a77ca-*******-4965-*******-b0084ec*******"
    )

    # Define documents to process
    documents = {
        "acta_constitutiva": "./documentos/NebulaPlatformActaConstitutiva_compressed (1).pdf",
        "actas_de_asamblea": "./documentos/Acta Asamblea Alsa, Jul. 15, 2022.pdf",
    }

    print("\n" + "=" * 70)
    print("EJEMPLO 1: CREAR RECORD Y SUBIR DOCUMENTOS")
    print("=" * 70)
    
    result = handler.process_documents(
        documents=documents,
        config_name="dictaminación",
        wait_for_completion=True
    )
    
    if result:
        print("\nRESULTADO FINAL (INFORMACIÓN RELEVANTE):")
        extracted_info = handler.extract_document_entities(result)
        pprint(extracted_info)


if __name__ == "__main__":
    main()