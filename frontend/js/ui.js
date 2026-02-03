/**
 * UI Manager - Handles all UI updates and rendering
 */
class UIManager {
    constructor() {
        this.elements = {
            // Query elements
            queryInput: document.getElementById('query-input'),
            sendBtn: document.getElementById('send-btn'),
            clearBtn: document.getElementById('clear-btn'),
            useLLM: document.getElementById('use-llm'),
            useRerank: document.getElementById('use-rerank'),

            // Loading and messages
            loading: document.getElementById('loading'),
            errorMessage: document.getElementById('error-message'),
            llmResponse: document.getElementById('llm-response'),
            llmContent: document.getElementById('llm-content'),

            // Results
            resultsHeader: document.getElementById('results-header'),
            resultsContainer: document.getElementById('results-container'),

            // Sidebar controls
            kbFolder: document.getElementById('kb-folder'),
            browseBtn: document.getElementById('browse-btn'),
            resetKBBtn: document.getElementById('reset-kb-btn'),
            chunkSize: document.getElementById('chunk-size'),
            overlap: document.getElementById('overlap'),
            batchSize: document.getElementById('batch-size'),
            ingestDocx: document.getElementById('ingest-docx'),
            ingestBtn: document.getElementById('ingest-btn'),
            resetBtn: document.getElementById('reset-btn'),
            resetConfirm: document.getElementById('reset-confirm'),
            confirmResetBtn: document.getElementById('confirm-reset-btn'),
            cancelResetBtn: document.getElementById('cancel-reset-btn'),

            themeToggle: document.getElementById('theme-toggle'),
            themeIcon: document.getElementById('theme-icon'),

            // Layout
            sidebar: document.querySelector('.sidebar'),
            sidebarToggle: document.getElementById('sidebar-toggle'),
            sidebarOverlay: document.getElementById('sidebar-overlay'),
            sidebarIcon: document.getElementById('sidebar-icon'),
            appContainer: document.querySelector('.app-container')
        };
    }

    /**
     * Toggle sidebar visibility
     */
    toggleSidebar(show) {
        const isMobile = window.innerWidth <= 768;

        if (isMobile) {
            // Mobile: Toggle Overlay Drawer
            if (show === undefined) {
                this.elements.sidebar.classList.toggle('active');
                this.elements.sidebarOverlay.classList.toggle('active');
            } else if (show) {
                this.elements.sidebar.classList.add('active');
                this.elements.sidebarOverlay.classList.add('active');
            } else {
                this.elements.sidebar.classList.remove('active');
                this.elements.sidebarOverlay.classList.remove('active');
            }
        } else {
            // Desktop: Toggle Collapsible Sidebar
            if (show === undefined) {
                this.elements.appContainer.classList.toggle('sidebar-collapsed');
            } else if (show) {
                this.elements.appContainer.classList.remove('sidebar-collapsed');
            } else {
                this.elements.appContainer.classList.add('sidebar-collapsed');
            }

            // Update Icon - Removed as user prefers static hamburger
            // const isCollapsed = this.elements.appContainer.classList.contains('sidebar-collapsed');
            // this.elements.sidebarIcon.textContent = isCollapsed ? '▶' : '◀';
        }
    }

    /**
     * Show loading state
     */
    showLoading() {
        this.elements.loading.style.display = 'flex';
        this.elements.sendBtn.disabled = true;
        this.hideError();
    }

    /**
     * Hide loading state
     */
    hideLoading() {
        this.elements.loading.style.display = 'none';
        this.elements.sendBtn.disabled = false;
    }

    /**
     * Show error message
     */
    showError(message) {
        this.elements.errorMessage.textContent = message;
        this.elements.errorMessage.style.display = 'block';
    }

    /**
     * Hide error message
     */
    hideError() {
        this.elements.errorMessage.style.display = 'none';
    }

    /**
     * Show LLM response
     */
    showLLMResponse(response) {
        if (response) {
            // Check if marked is available
            const htmlContent = (typeof marked !== 'undefined')
                ? marked.parse(response)
                : response;

            this.elements.llmContent.innerHTML = htmlContent;
            this.elements.llmResponse.style.display = 'block';
        } else {
            this.elements.llmResponse.style.display = 'none';
        }
    }

    /**
     * Render search results
     */
    renderResults(results) {
        if (!results || results.length === 0) {
            this.elements.resultsHeader.style.display = 'none';
            this.elements.resultsContainer.innerHTML = '';
            return;
        }

        this.elements.resultsHeader.style.display = 'block';
        this.elements.resultsContainer.innerHTML = '';

        results.forEach(result => {
            const card = this.createResultCard(result);
            this.elements.resultsContainer.appendChild(card);
        });
    }

    /**
     * Create a result card element
     */
    createResultCard(result) {
        const card = document.createElement('div');
        card.className = 'result-card';

        // Header with title and actions
        const header = document.createElement('div');
        header.className = 'result-header';

        const title = document.createElement('div');
        title.className = 'result-title';
        title.textContent = `${result.rank}. ${result.title}`;

        const actions = document.createElement('div');
        actions.className = 'result-actions';

        // Open folder button
        const openFolderBtn = document.createElement('button');
        openFolderBtn.className = 'btn btn-sm btn-secondary';
        openFolderBtn.innerHTML = '📂 Folder';
        openFolderBtn.onclick = () => this.handleOpenFolder(result);

        // Open file button
        const openFileBtn = document.createElement('button');
        openFileBtn.className = 'btn btn-sm btn-secondary';
        openFileBtn.innerHTML = '📄 File';
        openFileBtn.onclick = () => this.handleOpenFile(result);

        actions.appendChild(openFolderBtn);
        actions.appendChild(openFileBtn);

        header.appendChild(title);
        header.appendChild(actions);

        // Meta information
        const meta = document.createElement('div');
        meta.className = 'result-meta';

        const similarity = document.createElement('span');
        similarity.textContent = result.similarity !== null
            ? `Similarity: ${result.similarity.toFixed(4)}`
            : 'Similarity: N/A';

        const source = document.createElement('span');
        source.textContent = `Source: ${result.source}`;

        meta.appendChild(similarity);
        meta.appendChild(source);

        // Snippet
        const snippet = document.createElement('div');
        snippet.className = 'result-snippet';
        snippet.textContent = result.snippet;

        // Expandable sections
        const snippetExpandable = this.createExpandable('View snippet', result.snippet);
        const documentExpandable = this.createExpandable('Full document', result.document, true);
        const metadataExpandable = this.createExpandable('Metadata', JSON.stringify(result.metadata, null, 2), true);

        card.appendChild(header);
        card.appendChild(meta);
        card.appendChild(snippetExpandable);
        card.appendChild(documentExpandable);
        card.appendChild(metadataExpandable);

        return card;
    }

    /**
     * Create expandable section
     */
    createExpandable(title, content, isCode = false) {
        const container = document.createElement('div');
        container.className = 'expandable';

        const header = document.createElement('div');
        header.className = 'expandable-header';
        header.innerHTML = `<span>▶</span> <span>${title}</span>`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'expandable-content';
        contentDiv.style.display = 'none';

        if (isCode) {
            const pre = document.createElement('pre');
            pre.textContent = content;
            contentDiv.appendChild(pre);
        } else {
            contentDiv.textContent = content;
        }

        header.onclick = () => {
            const isOpen = contentDiv.style.display === 'block';
            contentDiv.style.display = isOpen ? 'none' : 'block';
            header.querySelector('span:first-child').textContent = isOpen ? '▶' : '▼';
        };

        container.appendChild(header);
        container.appendChild(contentDiv);

        return container;
    }

    /**
     * Handle open file
     */
    async handleOpenFile(result) {
        try {
            const path = result.metadata.source_file_full;
            if (path) {
                await apiClient.openFile(path);
            }
        } catch (error) {
            console.error('Failed to open file:', error);
            this.showError(`Failed to open file: ${error.message}`);
        }
    }

    /**
     * Handle open folder
     */
    async handleOpenFolder(result) {
        try {
            const path = result.metadata.folder;
            if (path) {
                await apiClient.openFolder(path);
            }
        } catch (error) {
            console.error('Failed to open folder:', error);
            this.showError(`Failed to open folder: ${error.message}`);
        }
    }

    /**
     * Clear all results
     */
    clearResults() {
        this.elements.resultsContainer.innerHTML = '';
        this.elements.resultsHeader.style.display = 'none';
        this.elements.llmResponse.style.display = 'none';
        this.hideError();
    }

    /**
     * Get query input value
     */
    getQueryInput() {
        return this.elements.queryInput.value.trim();
    }

    /**
     * Clear query input
     */
    clearQueryInput() {
        this.elements.queryInput.value = '';
    }

    /**
     * Get sidebar config values
     */
    getSidebarConfig() {
        return {
            kb_folder: this.elements.kbFolder.value,
            chunk_size: parseInt(this.elements.chunkSize.value),
            overlap: parseInt(this.elements.overlap.value),
            batch_size: parseInt(this.elements.batchSize.value),
            ingest_docx: this.elements.ingestDocx.checked
        };
    }

    /**
     * Set sidebar config values
     */
    setSidebarConfig(config) {
        this.elements.kbFolder.value = config.kb_folder || 'kb';
        this.elements.chunkSize.value = config.chunk_size || 100000;
        this.elements.overlap.value = config.overlap || 200;
        this.elements.batchSize.value = config.batch_size || 64;
    }

    /**
     * Show reset confirmation
     */
    showResetConfirm() {
        this.elements.resetConfirm.style.display = 'block';
    }

    /**
     * Hide reset confirmation
     */
    hideResetConfirm() {
        this.elements.resetConfirm.style.display = 'none';
    }
}

// Export singleton instance
const uiManager = new UIManager();
