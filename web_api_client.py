# MongoDB Atlas API Web App
#
# This script runs a simple Flask web server to provide a web interface
# for fetching and managing stream processors from the MongoDB Atlas API.
#
# Prerequisites:
# 1. You must have the required Python libraries installed:
#    pip install Flask requests python-dotenv
#
# 2. To run securely with HTTPS, create a file named '.env' in the same
#    directory as this script. This file should contain the paths to your
#    TLS certificate and key:
#
#    # .env file content
#    TLS_CERT_PATH=/path/to/your/certificate.pem
#    TLS_KEY_PATH=/path/to/your/private.key
#
# How to Run:
# 1. Save this code as a Python file (e.g., web_api_client.py).
# 2. Optionally, create the .env file as described above for HTTPS.
# 3. Run the script from your terminal: python web_api_client.py
# 4. Open your web browser and navigate to the URL shown in the terminal.

import os
import json
import requests
from requests.auth import HTTPDigestAuth
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv

# --- Flask App Initialization ---
app = Flask(__name__)

# --- HTML & JavaScript Template ---
# This single string contains the entire frontend for our web application.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MongoDB Atlas Stream Processing</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f0f2f5;
            color: #1c1e21;
            margin: 0;
            padding: 20px;
        }
        .container {
            width: 100%;
            max-width: 900px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            padding: 30px;
        }
        h1 {
            text-align: center;
            color: #00684a;
            margin-bottom: 25px;
        }
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        .form-group { margin-bottom: 0; }
        .form-group.full-width { grid-column: 1 / -1; }
        label { display: block; font-weight: 600; margin-bottom: 5px; color: #606770; }
        input[type="text"], input[type="password"] {
            width: 100%; padding: 10px; border: 1px solid #dddfe2;
            border-radius: 6px; box-sizing: border-box; font-size: 16px;
        }
        .button-section {
            grid-column: 1 / -1;
            margin-top: 20px;
        }
        .button-row {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }
        .button-row:last-child {
            margin-bottom: 0;
        }
        button, .file-input-label {
            flex-grow: 1; padding: 12px 20px; border: none; border-radius: 6px;
            font-size: 16px; font-weight: bold; cursor: pointer; transition: background-color 0.2s;
            text-align: center;
        }
        #loadConfigBtn { background-color: #795548; color: white; }
        #loadConfigBtn:hover { background-color: #5D4037; }
        #listProcessorsBtn { background-color: #4CAF50; color: white; }
        #listProcessorsBtn:hover { background-color: #45a049; }
        #listConnectionsBtn { background-color: #FF9800; color: white; }
        #listConnectionsBtn:hover { background-color: #F57C00; }
        #listSpisBtn { background-color: #03A9F4; color: white; }
        #listSpisBtn:hover { background-color: #0288D1; }
        #createBtn { background-color: #1976D2; color: white; }
        #createBtn:hover { background-color: #1565C0; }
        #createSpiBtn { background-color: #009688; color: white; }
        #createSpiBtn:hover { background-color: #00796B; }
        #createConnectionBtn { background-color: #9C27B0; color: white; }
        #createConnectionBtn:hover { background-color: #7B1FA2; }
        #deleteSpiBtn { background-color: #d32f2f; color: white; }
        #deleteSpiBtn:hover { background-color: #c62828; }
        #clearBtn { background-color: #607D8B; color: white; }
        #clearBtn:hover { background-color: #546E7A; }
        #output { margin-top: 25px; }
        .spinner {
            border: 4px solid rgba(0, 0, 0, 0.1); width: 36px; height: 36px;
            border-radius: 50%; border-left-color: #4CAF50;
            animation: spin 1s ease infinite; display: none; margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .results-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .results-table th, .results-table td { border: 1px solid #ddd; padding: 12px; text-align: left; vertical-align: middle; }
        .results-table th { background-color: #00684a; color: white; font-weight: 600; }
        .results-table tr:nth-child(even) { background-color: #f9f9f9; }
        .results-table tr:hover { background-color: #f1f1f1; }
        
        .state-CREATED { color: #1976d2; font-weight: bold; }
        .state-STOPPED { color: #F57C00; font-weight: bold; }
        .state-FAILED { color: #d32f2f; font-weight: bold; }
        .state-STARTED, .state-RUNNING { color: #388e3c; font-weight: bold; }

        .actions-cell { text-align: center !important; }
        .action-btn {
            padding: 5px 10px; font-size: 12px; margin: 0 2px;
            flex-grow: 0; color: white; border-radius: 4px; border: none; cursor: pointer;
        }
        .start-btn { background-color: #4CAF50; }
        .stop-btn { background-color: #f44336; }
        .delete-btn { background-color: #607D8B; }
        .stats-btn, .view-btn { background-color: #FFC107; }

        #errorMessage {
            color: #d32f2f; background-color: #ffcdd2; border: 1px solid #d32f2f;
            padding: 15px; border-radius: 6px; margin-top: 20px;
            display: none; white-space: pre-wrap; font-family: "Courier New", Courier, monospace;
        }
        /* Modal Styles */
        .modal {
            display: none; position: fixed; z-index: 1000; left: 0; top: 0;
            width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.5);
            align-items: center; justify-content: center;
        }
        .modal-content {
            background-color: #fefefe; margin: auto; padding: 20px;
            border: 1px solid #888; width: 80%; max-width: 700px; border-radius: 8px;
            display: flex; flex-direction: column;
        }
        .modal-header { padding-bottom: 10px; border-bottom: 1px solid #eee; }
        .modal-header h2 { margin: 0; }
        .modal-body { padding: 15px 0; max-height: 60vh; overflow-y: auto; }
        .modal-footer { display: flex; justify-content: flex-end; gap: 10px; padding-top: 10px; border-top: 1px solid #eee; }
        textarea.json-body {
            width: 100%; height: 300px; font-family: "Courier New", monospace;
            font-size: 14px; box-sizing: border-box;
        }
        pre.json-output {
            background-color: #263238; color: #FFFFFF; padding: 15px;
            border-radius: 6px; white-space: pre-wrap; word-wrap: break-word;
            font-family: "Courier New", Courier, monospace;
        }
        .modal-error-message { color: #d32f2f; margin-bottom: 10px; }
        input[type="file"] { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>MongoDB Atlas Stream Processing</h1>
        <form id="apiForm">
            <div class="form-grid">
                <div class="form-group full-width">
                     <button type="button" id="loadConfigBtn">Load Config from File or Text</button>
                </div>
                <div class="form-group">
                    <label for="publicKey">Public Key:</label>
                    <input type="text" id="publicKey" name="publicKey" required>
                </div>
                <div class="form-group">
                    <label for="privateKey">Private Key:</label>
                    <input type="password" id="privateKey" name="privateKey" required>
                </div>
                <div class="form-group">
                    <label for="projectId">Project ID:</label>
                    <input type="text" id="projectId" name="projectId" required>
                </div>
                <div class="form-group">
                    <label for="instanceName">Stream Instance Name:</label>
                    <input type="text" id="instanceName" name="instanceName" required>
                </div>
                <div class="form-group full-width">
                    <label for="atlasHost">Atlas API Host:</label>
                    <input type="text" id="atlasHost" name="atlasHost" required>
                </div>
                <div class="button-section">
                    <div class="button-row">
                        <button type="button" id="createBtn">Create Processor</button>
                        <button type="button" id="createConnectionBtn">Create Connection</button>
                        <button type="button" id="createSpiBtn">Create SPI</button>
                    </div>
                    <div class="button-row">
                        <button type="submit" id="listProcessorsBtn">List Processors</button>
                        <button type="button" id="listConnectionsBtn">List Connections</button>
                        <button type="button" id="listSpisBtn">List SPIs</button>
                    </div>
                    <div class="button-row">
                        <button type="button" id="clearBtn">Clear Output</button>
                        <button type="button" id="deleteSpiBtn">Delete SPI</button>
                    </div>
                </div>
            </div>
        </form>
        <div id="output">
            <div id="spinner" class="spinner"></div>
            <div id="errorMessage"></div>
            <table id="spisTable" class="results-table" style="display:none;">
                <thead>
                    <tr>
                        <th>Instance Name</th>
                        <th>Cloud</th>
                        <th>Region</th>
                        <th>Tier</th>
                    </tr>
                </thead>
                <tbody id="spisBody"></tbody>
            </table>
            <table id="connectionsTable" class="results-table" style="display:none;">
                <thead>
                    <tr>
                        <th>Connection Name</th>
                        <th>Type</th>
                        <th style="text-align: center;">Actions</th>
                    </tr>
                </thead>
                <tbody id="connectionsBody"></tbody>
            </table>
            <table id="processorsTable" class="results-table" style="display:none;">
                <thead>
                    <tr>
                        <th>Processor Name</th>
                        <th>State</th>
                        <th style="text-align: center;">Actions</th>
                    </tr>
                </thead>
                <tbody id="processorsBody"></tbody>
            </table>
        </div>
    </div>

    <!-- Modals -->
    <div id="loadConfigModal" class="modal">
        <div class="modal-content">
            <div class="modal-header"><h2>Load Configuration</h2></div>
            <div class="modal-body">
                <p>Paste configuration text below or select a file.</p>
                <textarea id="configText" class="json-body" placeholder="## Example ##\n\npublic_key=your-public-key\nprivate_key=your-private-key\nproject_id=your-project-id\nspi_name=your-instance-name\napi_host=cloud.mongodb.com"></textarea>
            </div>
            <div class="modal-footer">
                <button type="button" id="loadFromTextBtn">Load from Text</button>
                <label for="configFile" class="file-input-label">Load from .env file</label>
                <input type="file" id="configFile" accept=".txt,.properties,.env">
                <button type="button" class="cancel-btn">Cancel</button>
            </div>
        </div>
    </div>

    <div id="createProcessorModal" class="modal">
        <div class="modal-content">
            <form id="createProcessorForm">
                <div class="modal-header"><h2>Create New Stream Processor</h2></div>
                <div class="modal-body">
                    <p>Enter the full JSON body for the new processor below.</p>
                    <textarea id="processorBody" class="json-body" required placeholder='{ "name": "my-processor", "pipeline": [...] }'></textarea>
                    <div id="processorModalError" class="modal-error-message"></div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="cancel-btn">Cancel</button>
                    <button type="submit">Submit Processor</button>
                </div>
            </form>
        </div>
    </div>
    
    <div id="createSpiModal" class="modal">
        <div class="modal-content">
            <form id="createSpiForm">
                <div class="modal-header"><h2>Create New Stream Processing Instance</h2></div>
                <div class="modal-body">
                    <p>Enter the full JSON body for the new instance below.</p>
                    <textarea id="spiBody" class="json-body" required placeholder='{ "name": "my-new-instance", "provider": "AWS", "region": "US_EAST_1" }'></textarea>
                    <div id="spiModalError" class="modal-error-message"></div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="cancel-btn">Cancel</button>
                    <button type="submit">Submit Instance</button>
                </div>
            </form>
        </div>
    </div>

    <div id="createConnectionModal" class="modal">
        <div class="modal-content">
            <form id="createConnectionForm">
                <div class="modal-header"><h2>Create New Connection</h2></div>
                <div class="modal-body">
                    <p>Enter the full JSON body for the new connection below.</p>
                    <textarea id="connectionBody" class="json-body" required placeholder='{ "name": "my-connection", "type": "Kafka", ... }'></textarea>
                    <div id="connectionModalError" class="modal-error-message"></div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="cancel-btn">Cancel</button>
                    <button type="submit">Submit Connection</button>
                </div>
            </form>
        </div>
    </div>

    <div id="statsModal" class="modal">
        <div class="modal-content">
            <div class="modal-header"><h2 id="statsModalTitle">Processor Stats</h2></div>
            <div class="modal-body"><pre id="statsJsonOutput" class="json-output"></pre></div>
            <div class="modal-footer">
                <button type="button" id="copyStatsBtn">Copy</button>
                <button type="button" class="cancel-btn">Close</button>
            </div>
        </div>
    </div>

    <div id="connectionDetailsModal" class="modal">
        <div class="modal-content">
            <div class="modal-header"><h2 id="connectionDetailsTitle">Connection Details</h2></div>
            <div class="modal-body"><pre id="connectionJsonOutput" class="json-output"></pre></div>
            <div class="modal-footer">
                <button type="button" id="copyConnectionBtn">Copy</button>
                <button type="button" class="cancel-btn">Close</button>
            </div>
        </div>
    </div>


    <script>
        // --- DOM Elements ---
        const apiForm = document.getElementById('apiForm');
        const processorsTable = document.getElementById('processorsTable');
        const processorsBody = document.getElementById('processorsBody');
        const connectionsTable = document.getElementById('connectionsTable');
        const connectionsBody = document.getElementById('connectionsBody');
        const spisTable = document.getElementById('spisTable');
        const spisBody = document.getElementById('spisBody');
        const spinner = document.getElementById('spinner');
        const errorMessage = document.getElementById('errorMessage');
        
        const loadConfigModal = document.getElementById('loadConfigModal');
        const createProcessorModal = document.getElementById('createProcessorModal');
        const createProcessorForm = document.getElementById('createProcessorForm');
        const processorModalError = document.getElementById('processorModalError');
        
        const createSpiModal = document.getElementById('createSpiModal');
        const createSpiForm = document.getElementById('createSpiForm');
        const spiModalError = document.getElementById('spiModalError');
        
        const createConnectionModal = document.getElementById('createConnectionModal');
        const createConnectionForm = document.getElementById('createConnectionForm');
        const connectionModalError = document.getElementById('connectionModalError');

        const statsModal = document.getElementById('statsModal');
        const statsJsonOutput = document.getElementById('statsJsonOutput');
        const statsModalTitle = document.getElementById('statsModalTitle');
        
        const connectionDetailsModal = document.getElementById('connectionDetailsModal');
        const connectionJsonOutput = document.getElementById('connectionJsonOutput');
        const connectionDetailsTitle = document.getElementById('connectionDetailsTitle');

        // --- Helper Functions ---
        function getFormCredentials() {
            return {
                public_key: document.getElementById('publicKey').value,
                private_key: document.getElementById('privateKey').value,
                project_id: document.getElementById('projectId').value,
                instance_name: document.getElementById('instanceName').value,
                atlas_host: document.getElementById('atlasHost').value
            };
        }
        
        function handleApiError(result, errorElement) {
            let errorText = 'Error: ' + (result.error || 'Unknown server error');
            if (result.details) {
                const details = typeof result.details === 'string' ? result.details : JSON.stringify(result.details, null, 2);
                errorText += '\\n\\nDetails:\\n' + details;
            }
            if (result.debug_info) {
                errorText += `\\n\\n--- DEBUG INFO ---\\nMethod: ${result.debug_info.method}\\nURL: ${result.debug_info.url}\\nHeaders: ${JSON.stringify(result.debug_info.headers, null, 2)}`;
            }
            errorElement.textContent = errorText;
            errorElement.style.display = 'block';
        }

        function clearOutput() {
            processorsTable.style.display = 'none';
            processorsBody.innerHTML = '';
            connectionsTable.style.display = 'none';
            connectionsBody.innerHTML = '';
            spisTable.style.display = 'none';
            spisBody.innerHTML = '';
            errorMessage.style.display = 'none';
        }

        function parseAndPopulateConfig(configText) {
            const lines = configText.split('\\n');
            lines.forEach(line => {
                const parts = line.split('=');
                if (parts.length === 2) {
                    const key = parts[0].trim();
                    const value = parts[1].trim();
                    switch (key) {
                        case 'public_key':
                            document.getElementById('publicKey').value = value;
                            break;
                        case 'private_key':
                            document.getElementById('privateKey').value = value;
                            break;
                        case 'project_id':
                            document.getElementById('projectId').value = value;
                            break;
                        case 'spi_name':
                            document.getElementById('instanceName').value = value;
                            break;
                        case 'api_host':
                            document.getElementById('atlasHost').value = value;
                            break;
                    }
                }
            });
            loadConfigModal.style.display = 'none';
        }

        // --- Core API Functions ---
        async function listProcessors() {
            spinner.style.display = 'block';
            clearOutput();

            try {
                const response = await fetch('/api/fetch_data', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(getFormCredentials())
                });
                const result = await response.json();
                if (response.ok) {
                    if (result.results && result.results.length > 0) {
                        result.results.forEach(processor => {
                            const row = processorsBody.insertRow();
                            row.insertCell(0).textContent = processor.name;
                            const stateCell = row.insertCell(1);
                            stateCell.textContent = processor.state;
                            stateCell.className = `state-${processor.state}`;
                            const actionsCell = row.insertCell(2);
                            actionsCell.className = 'actions-cell';
                            actionsCell.innerHTML = `
                                <button class="action-btn start-btn" data-name="${processor.name}" data-action="start">Start</button>
                                <button class="action-btn stop-btn" data-name="${processor.name}" data-action="stop">Stop</button>
                                <button class="action-btn stats-btn" data-name="${processor.name}" data-action="stats">Stats</button>
                                <button class="action-btn delete-btn" data-name="${processor.name}" data-action="delete">Delete</button>
                            `;
                        });
                        processorsTable.style.display = 'table';
                    } else {
                        errorMessage.textContent = 'API returned successfully, but no stream processors were found.';
                        errorMessage.style.display = 'block';
                    }
                } else {
                    handleApiError(result, errorMessage);
                }
            } catch (error) {
                handleApiError({ error: 'A network or client-side error occurred', details: error.message }, errorMessage);
            } finally {
                spinner.style.display = 'none';
            }
        }

        async function listConnections() {
            spinner.style.display = 'block';
            clearOutput();

            try {
                const response = await fetch('/api/list_connections', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(getFormCredentials())
                });
                const result = await response.json();
                if (response.ok) {
                    if (result.results && result.results.length > 0) {
                        result.results.forEach(connection => {
                            const row = connectionsBody.insertRow();
                            row.insertCell(0).textContent = connection.name;
                            row.insertCell(1).textContent = connection.type;
                            const actionsCell = row.insertCell(2);
                            actionsCell.className = 'actions-cell';
                            actionsCell.innerHTML = `
                                <button class="action-btn view-btn" data-name="${connection.name}" data-action="view">View</button>
                                <button class="action-btn delete-btn" data-name="${connection.name}" data-action="delete">Delete</button>
                            `;
                        });
                        connectionsTable.style.display = 'table';
                    } else {
                        errorMessage.textContent = 'API returned successfully, but no connections were found.';
                        errorMessage.style.display = 'block';
                    }
                } else {
                    handleApiError(result, errorMessage);
                }
            } catch (error) {
                handleApiError({ error: 'A network or client-side error occurred', details: error.message }, errorMessage);
            } finally {
                spinner.style.display = 'none';
            }
        }
        
        async function listSpis() {
            spinner.style.display = 'block';
            clearOutput();

            try {
                const response = await fetch('/api/list_spis', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(getFormCredentials())
                });
                const result = await response.json();
                if (response.ok) {
                    if (result.results && result.results.length > 0) {
                        result.results.forEach(instance => {
                            const row = spisBody.insertRow();
                            row.insertCell(0).textContent = instance.name || 'N/A';
                            row.insertCell(1).textContent = instance.dataProcessRegion?.cloudProvider || 'N/A';
                            row.insertCell(2).textContent = instance.dataProcessRegion?.region || 'N/A';
                            row.insertCell(3).textContent = instance.streamConfig?.tier || 'N/A';
                        });
                        spisTable.style.display = 'table';
                    } else {
                        errorMessage.textContent = 'API returned successfully, but no stream instances were found.';
                        errorMessage.style.display = 'block';
                    }
                } else {
                    handleApiError(result, errorMessage);
                }
            } catch (error) {
                handleApiError({ error: 'A network or client-side error occurred', details: error.message }, errorMessage);
            } finally {
                spinner.style.display = 'none';
            }
        }

        async function handleProcessorAction(event) {
            if (!event.target.classList.contains('action-btn')) return;
            const button = event.target;
            const processorName = button.dataset.name;
            const action = button.dataset.action;

            if (action === 'delete' && !confirm(`Are you sure you want to delete the processor "${processorName}"? This cannot be undone.`)) return;

            if (action === 'stats') {
                await getProcessorStats(processorName);
                return;
            }
            
            spinner.style.display = 'block';
            errorMessage.style.display = 'none';
            const payload = { ...getFormCredentials(), processor_name: processorName, action: action };

            try {
                const response = await fetch('/api/manage_processor', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await response.json();
                if (response.ok) {
                    await listProcessors();
                } else {
                    handleApiError(result, errorMessage);
                    spinner.style.display = 'none';
                }
            } catch (error) {
                handleApiError({ error: 'A network or client-side error occurred', details: error.message }, errorMessage);
                spinner.style.display = 'none';
            }
        }

        async function handleConnectionAction(event) {
            if (!event.target.classList.contains('action-btn')) return;
            const button = event.target;
            const connectionName = button.dataset.name;
            const action = button.dataset.action;

            if (action === 'delete' && !confirm(`Are you sure you want to delete the connection "${connectionName}"? This cannot be undone.`)) return;
            
            spinner.style.display = 'block';
            errorMessage.style.display = 'none';
            
            const payload = { ...getFormCredentials(), connection_name: connectionName, action: action };

            try {
                let endpoint = '';
                if (action === 'view') {
                    endpoint = '/api/get_connection_details';
                } else if (action === 'delete') {
                    endpoint = '/api/manage_connection';
                } else {
                    return;
                }

                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const result = await response.json();

                if (response.ok) {
                    if (action === 'view') {
                        connectionDetailsTitle.textContent = `Details for: ${connectionName}`;
                        connectionJsonOutput.textContent = JSON.stringify(result, null, 2);
                        connectionDetailsModal.style.display = 'flex';
                    } else if (action === 'delete') {
                        await listConnections();
                    }
                } else {
                    handleApiError(result, errorMessage);
                }
            } catch (error) {
                handleApiError({ error: 'A network or client-side error occurred', details: error.message }, errorMessage);
            } finally {
                spinner.style.display = 'none';
            }
        }
        
        async function getProcessorStats(processorName) {
            spinner.style.display = 'block';
            errorMessage.style.display = 'none';
            const payload = { ...getFormCredentials(), processor_name: processorName };

            try {
                const response = await fetch('/api/get_processor_stats', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await response.json();
                if (response.ok) {
                    statsModalTitle.textContent = `Stats for: ${processorName}`;
                    statsJsonOutput.textContent = JSON.stringify(result, null, 2);
                    statsModal.style.display = 'flex';
                } else {
                    handleApiError(result, errorMessage);
                }
            } catch (error) {
                handleApiError({ error: 'A network or client-side error occurred', details: error.message }, errorMessage);
            } finally {
                spinner.style.display = 'none';
            }
        }
        
        async function deleteSpi() {
            const instanceName = document.getElementById('instanceName').value;
            if (!instanceName) {
                alert('Please enter a Stream Instance Name to delete.');
                return;
            }
            if (!confirm(`Are you sure you want to delete the Stream Processing Instance "${instanceName}"? This is irreversible.`)) {
                return;
            }

            spinner.style.display = 'block';
            errorMessage.style.display = 'none';
            const payload = getFormCredentials();

            try {
                const response = await fetch('/api/delete_spi', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await response.json();
                if (response.ok) {
                    alert(`Successfully deleted instance: ${instanceName}`);
                    clearOutput();
                } else {
                    handleApiError(result, errorMessage);
                }
            } catch (error) {
                handleApiError({ error: 'A network or client-side error occurred', details: error.message }, errorMessage);
            } finally {
                spinner.style.display = 'none';
            }
        }

        // --- Event Listeners ---
        apiForm.addEventListener('submit', (event) => {
            event.preventDefault();
            listProcessors();
        });

        document.getElementById('listConnectionsBtn').addEventListener('click', listConnections);
        document.getElementById('listSpisBtn').addEventListener('click', listSpis);
        document.getElementById('deleteSpiBtn').addEventListener('click', deleteSpi);
        
        processorsBody.addEventListener('click', handleProcessorAction);
        connectionsBody.addEventListener('click', handleConnectionAction);

        document.getElementById('clearBtn').addEventListener('click', clearOutput);

        // --- Modal Event Listeners ---
        document.getElementById('loadConfigBtn').addEventListener('click', () => {
            loadConfigModal.style.display = 'flex';
        });

        document.getElementById('loadFromTextBtn').addEventListener('click', () => {
            const configText = document.getElementById('configText').value;
            parseAndPopulateConfig(configText);
        });

        document.getElementById('configFile').addEventListener('change', (event) => {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    parseAndPopulateConfig(e.target.result);
                };
                reader.readAsText(file);
            }
        });

        document.getElementById('createBtn').addEventListener('click', () => {
            createProcessorModal.style.display = 'flex';
            processorModalError.style.display = 'none';
        });

        createProcessorForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const processorBodyText = document.getElementById('processorBody').value;
            let processorBody;
            try {
                processorBody = JSON.parse(processorBodyText);
                processorModalError.style.display = 'none';
            } catch (e) {
                handleApiError({ error: 'Invalid JSON', details: e.message }, processorModalError);
                return;
            }
            const payload = { ...getFormCredentials(), processor_body: processorBody };
            try {
                const response = await fetch('/api/create_processor', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await response.json();
                if (response.ok) {
                    createProcessorModal.style.display = 'none';
                    document.getElementById('processorBody').value = '';
                    await listProcessors();
                } else {
                    handleApiError(result, processorModalError);
                }
            } catch(error) {
                handleApiError({ error: 'A network or client-side error occurred', details: error.message }, processorModalError);
            }
        });

        document.getElementById('createSpiBtn').addEventListener('click', () => {
            createSpiModal.style.display = 'flex';
            spiModalError.style.display = 'none';
        });

        createSpiForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const spiBodyText = document.getElementById('spiBody').value;
            let spiBody;
            try {
                spiBody = JSON.parse(spiBodyText);
                spiModalError.style.display = 'none';
            } catch (e) {
                handleApiError({ error: 'Invalid JSON', details: e.message }, spiModalError);
                return;
            }
            const payload = { ...getFormCredentials(), spi_body: spiBody };
            try {
                const response = await fetch('/api/create_spi', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await response.json();
                if (response.ok) {
                    createSpiModal.style.display = 'none';
                    document.getElementById('spiBody').value = '';
                    alert('Stream Processing Instance created successfully!');
                } else {
                    handleApiError(result, spiModalError);
                }
            } catch(error) {
                handleApiError({ error: 'A network or client-side error occurred', details: error.message }, spiModalError);
            }
        });

        document.getElementById('createConnectionBtn').addEventListener('click', () => {
            createConnectionModal.style.display = 'flex';
            connectionModalError.style.display = 'none';
        });

        createConnectionForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const connectionBodyText = document.getElementById('connectionBody').value;
            let connectionBody;
            try {
                connectionBody = JSON.parse(connectionBodyText);
                connectionModalError.style.display = 'none';
            } catch (e) {
                handleApiError({ error: 'Invalid JSON', details: e.message }, connectionModalError);
                return;
            }
            const payload = { ...getFormCredentials(), connection_body: connectionBody };
            try {
                const response = await fetch('/api/create_connection', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await response.json();
                if (response.ok) {
                    createConnectionModal.style.display = 'none';
                    document.getElementById('connectionBody').value = '';
                    alert('Connection created successfully!');
                } else {
                    handleApiError(result, connectionModalError);
                }
            } catch(error) {
                handleApiError({ error: 'A network or client-side error occurred', details: error.message }, connectionModalError);
            }
        });

        // Generic Modal Cancel/Close Listeners
        document.querySelectorAll('.cancel-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                btn.closest('.modal').style.display = 'none';
            });
        });

        // Copy Button Listeners
        function setupCopyButton(buttonId, sourceElementId) {
            document.getElementById(buttonId).addEventListener('click', () => {
                const textToCopy = document.getElementById(sourceElementId).textContent;
                const textArea = document.createElement('textarea');
                textArea.value = textToCopy;
                document.body.appendChild(textArea);
                textArea.select();
                try {
                    document.execCommand('copy');
                    const copyBtn = document.getElementById(buttonId);
                    copyBtn.textContent = 'Copied!';
                    setTimeout(() => { copyBtn.textContent = 'Copy'; }, 2000);
                } catch (err) {
                    console.error('Failed to copy text: ', err);
                }
                document.body.removeChild(textArea);
            });
        }
        setupCopyButton('copyStatsBtn', 'statsJsonOutput');
        setupCopyButton('copyConnectionBtn', 'connectionJsonOutput');

    </script>
</body>
</html>
"""

# --- Flask Routes ---

@app.route('/')
def index():
    """Renders the main HTML page."""
    return render_template_string(HTML_TEMPLATE)

def make_atlas_request(method, url, public_key, private_key, accept_header, json_body=None, content_type_header=None):
    """Helper function to make requests to the Atlas API."""
    if content_type_header is None:
        content_type_header = "application/json"
        
    headers = {"Accept": accept_header, "Content-Type": content_type_header}
    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            auth=HTTPDigestAuth(public_key, private_key),
            json=json_body,
            timeout=30
        )
        response.raise_for_status()
        if response.status_code == 204:
            return jsonify({"success": True, "message": "Action completed successfully."}), 200
        return jsonify(response.json())
    except requests.exceptions.HTTPError as http_err:
        error_details = {"error": f"HTTP Error: {http_err.response.status_code} {http_err.response.reason}"}
        try:
            error_details['details'] = http_err.response.json()
        except json.JSONDecodeError:
            error_details['details'] = http_err.response.text
        
        if http_err.request:
            request_headers = {k: v for k, v in http_err.request.headers.items()}
            error_details['debug_info'] = {
                'method': http_err.request.method,
                'url': http_err.request.url,
                'headers': request_headers
            }
            
        return jsonify(error_details), http_err.response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "A network error occurred.", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected server error occurred.", "details": str(e)}), 500

def get_request_data(request):
    """Helper to extract and validate common fields from the request JSON."""
    data = request.get_json()
    if not data: return None, jsonify({"error": "Invalid request format. Expected JSON."}), 400
    
    public_key = data.get('public_key')
    private_key = data.get('private_key')
    project_id = data.get('project_id')
    atlas_host = data.get('atlas_host', 'cloud.mongodb.com')
    
    if not all([public_key, private_key, project_id, atlas_host]):
        return None, jsonify({"error": "Missing required fields."}), 400
        
    return data, None, None

@app.route('/api/fetch_data', methods=['POST'])
def fetch_data():
    """API endpoint to fetch all stream processors."""
    data, error_response, status_code = get_request_data(request)
    if error_response: return error_response, status_code
    
    instance_name = data.get('instance_name')
    if not instance_name:
        return jsonify({"error": "Missing 'instance_name' for fetching processors."}), 400

    url = f"https://{data['atlas_host']}/api/atlas/v2/groups/{data['project_id']}/streams/{instance_name}/processors"
    accept_header = "application/vnd.atlas.2024-05-30+json"
    return make_atlas_request('GET', url, data['public_key'], data['private_key'], accept_header)

@app.route('/api/manage_processor', methods=['POST'])
def manage_processor():
    """API endpoint to Start, Stop, or Delete a stream processor."""
    data, error_response, status_code = get_request_data(request)
    if error_response: return error_response, status_code

    instance_name = data.get('instance_name')
    processor_name = data.get('processor_name')
    action = data.get('action')

    if not all([instance_name, processor_name, action]):
        return jsonify({"error": "Missing required fields for processor management."}), 400

    base_url = f"https://{data['atlas_host']}/api/atlas/v2/groups/{data['project_id']}/streams/{instance_name}/processor/{processor_name}"
    
    if action == 'start':
        url = f"{base_url}:start"
        method = 'POST'
    elif action == 'stop':
        url = f"{base_url}:stop"
        method = 'POST'
    elif action == 'delete':
        url = base_url
        method = 'DELETE'
    else:
        return jsonify({"error": "Invalid action specified."}), 400
    
    accept_header = "application/vnd.atlas.2024-05-30+json"
    return make_atlas_request(method, url, data['public_key'], data['private_key'], accept_header)

@app.route('/api/create_processor', methods=['POST'])
def create_processor():
    """API endpoint to create a new stream processor."""
    data, error_response, status_code = get_request_data(request)
    if error_response: return error_response, status_code

    instance_name = data.get('instance_name')
    processor_body = data.get('processor_body')
    if not all([instance_name, processor_body]):
        return jsonify({"error": "Missing instance_name or processor_body for create."}), 400

    url = f"https://{data['atlas_host']}/api/atlas/v2/groups/{data['project_id']}/streams/{instance_name}/processor"
    accept_header = "application/vnd.atlas.2024-05-30+json"
    return make_atlas_request('POST', url, data['public_key'], data['private_key'], accept_header, json_body=processor_body)

@app.route('/api/get_processor_stats', methods=['POST'])
def get_processor_stats():
    """API endpoint to get stats for a single stream processor."""
    data, error_response, status_code = get_request_data(request)
    if error_response: return error_response, status_code

    instance_name = data.get('instance_name')
    processor_name = data.get('processor_name')
    if not all([instance_name, processor_name]):
        return jsonify({"error": "Missing instance_name or processor_name for stats task."}), 400

    url = f"https://{data['atlas_host']}/api/atlas/v2/groups/{data['project_id']}/streams/{instance_name}/processor/{processor_name}"
    accept_header = "application/vnd.atlas.2024-05-30+json"
    return make_atlas_request('GET', url, data['public_key'], data['private_key'], accept_header)

@app.route('/api/create_spi', methods=['POST'])
def create_spi():
    """API endpoint to create a new stream processing instance."""
    data, error_response, status_code = get_request_data(request)
    if error_response: return error_response, status_code

    spi_body = data.get('spi_body')
    if not spi_body or not isinstance(spi_body, dict):
        return jsonify({"error": "Missing or invalid 'spi_body' in request."}), 400

    url = f"https://{data['atlas_host']}/api/atlas/v2/groups/{data['project_id']}/streams"
    accept_header = "application/vnd.atlas.2023-02-01+json"
    return make_atlas_request('POST', url, data['public_key'], data['private_key'], accept_header, json_body=spi_body)

@app.route('/api/delete_spi', methods=['POST'])
def delete_spi():
    """API endpoint to delete a stream processing instance."""
    data, error_response, status_code = get_request_data(request)
    if error_response: return error_response, status_code

    instance_name = data.get('instance_name')
    if not instance_name:
        return jsonify({"error": "Missing 'instance_name' to delete."}), 400

    url = f"https://{data['atlas_host']}/api/atlas/v2/groups/{data['project_id']}/streams/{instance_name}"
    accept_header = "application/vnd.atlas.2023-02-01+json"
    return make_atlas_request('DELETE', url, data['public_key'], data['private_key'], accept_header)

@app.route('/api/create_connection', methods=['POST'])
def create_connection():
    """API endpoint to create a new stream connection."""
    data, error_response, status_code = get_request_data(request)
    if error_response: return error_response, status_code

    instance_name = data.get('instance_name')
    connection_body = data.get('connection_body')
    if not all([instance_name, connection_body]):
        return jsonify({"error": "Missing instance_name or connection_body for create."}), 400

    url = f"https://{data['atlas_host']}/api/atlas/v2/groups/{data['project_id']}/streams/{instance_name}/connections"
    accept_header = "application/vnd.atlas.2023-02-01+json"
    content_type_header = "application/vnd.atlas.2023-02-01+json"
    return make_atlas_request('POST', url, data['public_key'], data['private_key'], accept_header, json_body=connection_body, content_type_header=content_type_header)

@app.route('/api/list_connections', methods=['POST'])
def list_connections():
    """API endpoint to list all connections for a stream instance."""
    data, error_response, status_code = get_request_data(request)
    if error_response: return error_response, status_code

    instance_name = data.get('instance_name')
    if not instance_name:
        return jsonify({"error": "Missing 'instance_name' for listing connections."}), 400

    url = f"https://{data['atlas_host']}/api/atlas/v2/groups/{data['project_id']}/streams/{instance_name}/connections"
    accept_header = "application/vnd.atlas.2023-02-01+json"
    return make_atlas_request('GET', url, data['public_key'], data['private_key'], accept_header)

@app.route('/api/get_connection_details', methods=['POST'])
def get_connection_details():
    """API endpoint to get details for a single connection."""
    data, error_response, status_code = get_request_data(request)
    if error_response: return error_response, status_code

    instance_name = data.get('instance_name')
    connection_name = data.get('connection_name')
    if not all([instance_name, connection_name]):
        return jsonify({"error": "Missing instance_name or connection_name for details task."}), 400

    url = f"https://{data['atlas_host']}/api/atlas/v2/groups/{data['project_id']}/streams/{instance_name}/connections/{connection_name}"
    accept_header = "application/vnd.atlas.2023-02-01+json"
    return make_atlas_request('GET', url, data['public_key'], data['private_key'], accept_header)

@app.route('/api/manage_connection', methods=['POST'])
def manage_connection():
    """API endpoint to delete a connection."""
    data, error_response, status_code = get_request_data(request)
    if error_response: return error_response, status_code

    instance_name = data.get('instance_name')
    connection_name = data.get('connection_name')
    action = data.get('action')

    if not all([instance_name, connection_name, action]):
        return jsonify({"error": "Missing required fields for connection management."}), 400

    if action == 'delete':
        url = f"https://{data['atlas_host']}/api/atlas/v2/groups/{data['project_id']}/streams/{instance_name}/connections/{connection_name}"
        method = 'DELETE'
    else:
        return jsonify({"error": "Invalid action specified for connection."}), 400
    
    accept_header = "application/vnd.atlas.2023-02-01+json"
    return make_atlas_request(method, url, data['public_key'], data['private_key'], accept_header)

@app.route('/api/list_spis', methods=['POST'])
def list_spis():
    """API endpoint to list all stream processing instances in a project."""
    data, error_response, status_code = get_request_data(request)
    if error_response: return error_response, status_code

    url = f"https://{data['atlas_host']}/api/atlas/v2/groups/{data['project_id']}/streams"
    accept_header = "application/vnd.atlas.2023-02-01+json"
    return make_atlas_request('GET', url, data['public_key'], data['private_key'], accept_header)


# --- Main Execution Block ---

if __name__ == '__main__':
    load_dotenv()
    tls_cert_path = os.getenv('TLS_CERT_PATH')
    tls_key_path = os.getenv('TLS_KEY_PATH')

    # Check if both paths are provided and the files exist
    if tls_cert_path and tls_key_path and os.path.exists(tls_cert_path) and os.path.exists(tls_key_path):
        # Start with TLS (HTTPS)
        ssl_context = (tls_cert_path, tls_key_path)
        print("TLS certificate and key found. Starting secure Flask server (HTTPS)...")
        print("Access the application at: https://localhost:5000")
        app.run(host='0.0.0.0', port=5000, ssl_context=ssl_context, debug=False)
    else:
        # Start without TLS (HTTP)
        print("Warning: TLS certificate/key not found or invalid.")
        print("Starting insecure Flask server (HTTP)...")
        print("Access the application at: http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=False)

