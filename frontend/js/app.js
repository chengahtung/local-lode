/**
 * Local Lode Application - Main application class
 */
class LocalLodeApp {
    constructor() {
        this.state = stateManager;
        this.api = apiClient;
        this.ui = uiManager;

        this.init();
    }

    /**
     * Initialize application
     */
    async init() {
        console.log('🚀 Local Lode initializing...');

        // Initialize Theme
        this.initTheme();

        // Subscribe to state changes
        this.state.subscribe(state => this.onStateChange(state));

        // Setup event listeners
        this.setupEventListeners();

        // Load initial configuration
        await this.loadConfig();

        console.log('✅ Local Lode ready!');
    }

    /**
     * Setup all event listeners
     */
    setupEventListeners() {
        // Query controls
        this.ui.elements.sendBtn.addEventListener('click', () => this.handleQuery());
        this.ui.elements.clearBtn.addEventListener('click', () => this.handleClear());

        // Enter key to submit (Shift+Enter for new line)
        this.ui.elements.queryInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleQuery();
            }
        });

        // Sidebar controls
        this.ui.elements.ingestBtn.addEventListener('click', () => this.handleIngest());
        this.ui.elements.resetBtn.addEventListener('click', () => this.ui.showResetConfirm());
        this.ui.elements.confirmResetBtn.addEventListener('click', () => this.handleReset());
        this.ui.elements.cancelResetBtn.addEventListener('click', () => this.ui.hideResetConfirm());

        // KB folder controls
        this.ui.elements.browseBtn.addEventListener('click', () => this.handleSelectFolder());
        this.ui.elements.resetKBBtn.addEventListener('click', () => this.handleResetKBFolder());

        // Theme toggle
        this.ui.elements.themeToggle.addEventListener('click', () => this.toggleTheme());

        // Sidebar interactions (Mobile)
        if (this.ui.elements.sidebarToggle) {
            this.ui.elements.sidebarToggle.addEventListener('click', () => this.ui.toggleSidebar());
        }
        if (this.ui.elements.sidebarOverlay) {
            this.ui.elements.sidebarOverlay.addEventListener('click', () => this.ui.toggleSidebar(false));
        }
    }

    /**
     * Initialize theme
     */
    initTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        this.updateThemeIcon(savedTheme);
    }

    /**
     * Toggle theme
     */
    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        this.updateThemeIcon(newTheme);
    }

    /**
     * Update theme icon
     */
    updateThemeIcon(theme) {
        this.ui.elements.themeIcon.textContent = theme === 'dark' ? '🌙' : '☀️';
    }

    /**
     * Handle folder selection
     */
    async handleSelectFolder() {
        try {
            const data = await this.api.selectFolder();
            if (data.selected_folder) {
                // Update input field
                this.ui.elements.kbFolder.value = data.selected_folder;

                // Update config on backend to persist it
                await this.api.updateConfig({ kb_folder: data.selected_folder });
                console.log(`📂 Knowledge base folder updated: ${data.selected_folder}`);
            }
        } catch (error) {
            console.error('Failed to select folder:', error);
            this.state.setError(`Failed to select folder: ${error.message}`);
        }
    }

    /**
     * Handle resetting KB folder to default
     */
    async handleResetKBFolder() {
        try {
            const config = await this.api.resetKBFolder();
            // Update UI
            this.ui.elements.kbFolder.value = config.kb_folder;
            console.log(`✅ KB folder reset to default: ${config.kb_folder}`);
        } catch (error) {
            console.error('Failed to reset KB folder:', error);
            this.state.setError(`Failed to reset KB folder: ${error.message}`);
        }
    }

    /**
     * Handle state changes
     */
    onStateChange(state) {
        // Update UI based on state
        if (state.loading) {
            this.ui.showLoading();
        } else {
            this.ui.hideLoading();
        }

        if (state.error) {
            this.ui.showError(state.error);
        }

        if (state.results) {
            this.ui.renderResults(state.results);
        }

        if (state.llmResponse) {
            this.ui.showLLMResponse(state.llmResponse);
        }
    }

    /**
     * Load configuration from backend
     */
    async loadConfig() {
        try {
            const config = await this.api.getConfig();
            this.state.updateConfig(config);
            this.ui.setSidebarConfig(config);
        } catch (error) {
            console.error('Failed to load config:', error);
            // Use default values if config load fails
        }
    }

    /**
     * Handle search query
     */
    async handleQuery() {
        const query = this.ui.getQueryInput();

        if (!query) {
            this.ui.showError('Please enter a search query');
            return;
        }

        try {
            this.state.setLoading(true);
            this.state.clearError();

            const useRerank = this.ui.elements.useRerank.checked;
            const useLLM = this.ui.elements.useLLM.checked;

            console.log(`🔍 Querying: "${query.substring(0, 50)}..."`);
            console.log(`   Rerank: ${useRerank}, LLM: ${useLLM}`);

            // Clear previous response if any
            if (useLLM) {
                this.state.setLLMResponse("");
            }

            let fullLLMResponse = "";

            await this.api.queryStream(query, useRerank, useLLM, 10, (type, payload) => {
                if (type === 'results') {
                    console.log(`✅ Got ${payload.total_results} results`);
                    this.state.setResults(payload.results);
                } else if (type === 'chunk') {
                    // console.log('Chunk:', payload);
                    fullLLMResponse += payload;
                    // Parse markdown here if needed, or let UI handle it. 
                    // Since UI.showLLMResponse parses it, we just update the state.
                    this.state.setLLMResponse(fullLLMResponse);
                } else if (type === 'error') {
                    console.error('Stream error:', payload);
                    this.state.setError(`Stream error: ${payload}`);
                }
            });

        } catch (error) {
            console.error('Query failed:', error);
            this.state.setError(`Query failed: ${error.message}`);
        } finally {
            this.state.setLoading(false);
        }
    }

    /**
     * Handle clear button
     */
    handleClear() {
        this.ui.clearQueryInput();
        this.ui.clearResults();
        this.state.clearResults();
    }

    /**
     * Handle knowledge base ingestion
     */
    async handleIngest() {
        const config = this.ui.getSidebarConfig();

        if (!confirm(`Ingest knowledge base from "${config.kb_folder}"?\n\nThis may take a while for large knowledge bases.`)) {
            return;
        }

        try {
            this.ui.elements.ingestBtn.disabled = true;
            this.ui.elements.ingestBtn.textContent = '⏳ Ingesting...';

            console.log('📥 Starting ingestion...');
            console.log('Config:', config);

            const response = await this.api.ingest(
                config.kb_folder,
                config.chunk_size,
                config.overlap,
                config.batch_size,
                config.ingest_docx
            );

            console.log('✅ Ingestion complete:', response);

            alert(`✅ ${response.message}`);

        } catch (error) {
            console.error('Ingestion failed:', error);
            alert(`❌ Ingestion failed: ${error.message}`);
        } finally {
            this.ui.elements.ingestBtn.disabled = false;
            this.ui.elements.ingestBtn.innerHTML = '<span class="btn-icon">📥</span> Ingest KB';
        }
    }

    /**
     * Handle database reset
     */
    async handleReset() {
        try {
            this.ui.elements.confirmResetBtn.disabled = true;
            this.ui.elements.confirmResetBtn.textContent = 'Resetting...';

            console.log('🗑️ Resetting database...');

            const response = await this.api.reset();

            console.log('✅ Reset complete:', response);

            alert(`✅ ${response.message}`);

            this.ui.hideResetConfirm();
            this.handleClear();

        } catch (error) {
            console.error('Reset failed:', error);
            alert(`❌ Reset failed: ${error.message}`);
        } finally {
            this.ui.elements.confirmResetBtn.disabled = false;
            this.ui.elements.confirmResetBtn.textContent = 'Confirm';
            this.ui.hideResetConfirm();
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new LocalLodeApp();
});
