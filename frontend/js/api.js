/**
 * API Client - Handles all backend communication
 */
class APIClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
    }

    /**
     * Generic fetch wrapper with error handling
     */
    async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }

    /**
     * Execute search query
     */
    async query(queryText, useRerank = true, useLLM = false, nResults = 10) {
        return await this.request('/api/query', {
            method: 'POST',
            body: JSON.stringify({
                query: queryText,
                use_rerank: useRerank,
                use_llm: useLLM,
                n_results: nResults
            })
        });
    }

    /**
     * Execute search query with streaming
     * @param {string} queryText 
     * @param {boolean} useRerank 
     * @param {boolean} useLLM 
     * @param {number} nResults 
     * @param {function} onChunk - Callback(type, payload)
     * @returns {Promise<void>}
     */
    async queryStream(queryText, useRerank = true, useLLM = false, nResults = 10, onChunk) {
        const response = await fetch(`${this.baseURL}/api/query-stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream'
            },
            body: JSON.stringify({
                query: queryText,
                use_rerank: useRerank,
                use_llm: useLLM,
                n_results: nResults
            })
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });

            // Parse SSE format: data: JSON\n\n
            const lines = buffer.split('\n\n');
            buffer = lines.pop(); // Keep incomplete chunk in buffer

            for (const line of lines) {
                if (line.trim().startsWith('data: ')) {
                    const jsonStr = line.trim().slice(6);
                    try {
                        const data = JSON.parse(jsonStr);
                        onChunk(data.type, data.payload);
                    } catch (e) {
                        console.error('Error parsing SSE data:', e, jsonStr);
                    }
                }
            }
        }
    }

    /**
     * Ingest knowledge base
     */
    async ingest(kbFolder, chunkSize, overlap, batchSize, ingestDocx) {
        return await this.request('/api/ingest', {
            method: 'POST',
            body: JSON.stringify({
                kb_folder: kbFolder,
                chunk_size: chunkSize,
                overlap: overlap,
                batch_size: batchSize,
                ingest_docx: ingestDocx
            })
        });
    }

    /**
     * Reset database
     */
    async reset() {
        return await this.request('/api/reset', {
            method: 'POST'
        });
    }

    /**
     * Get configuration
     */
    async getConfig() {
        return await this.request('/api/config', {
            method: 'GET'
        });
    }

    /**
     * Update configuration
     */
    async updateConfig(config) {
        return await this.request('/api/config', {
            method: 'PUT',
            body: JSON.stringify(config)
        });
    }

    /**
     * Open file
     */
    async openFile(path) {
        return await this.request('/api/open-file', {
            method: 'POST',
            body: JSON.stringify({ path })
        });
    }

    /**
     * Open folder
     */
    async openFolder(path) {
        return await this.request('/api/open-folder', {
            method: 'POST',
            body: JSON.stringify({ path })
        });
    }

    /**
     * Select folder dialog
     */
    async selectFolder() {
        return await this.request('/api/select-folder', {
            method: 'POST'
        });
    }

    /**
     * Reset KB folder to default
     */
    async resetKBFolder() {
        return await this.request('/api/reset-kb-folder', {
            method: 'POST'
        });
    }
}

// Export singleton instance
const apiClient = new APIClient();
