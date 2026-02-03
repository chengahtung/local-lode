/**
 * State Manager - Manages application state
 */
class StateManager {
    constructor() {
        this.state = {
            results: [],
            llmResponse: null,
            loading: false,
            error: null,
            config: {
                kb_folder: 'kb',
                chunk_size: 100000,
                overlap: 200,
                batch_size: 64
            }
        };

        this.listeners = [];
    }

    /**
     * Get current state
     */
    getState() {
        return { ...this.state };
    }

    /**
     * Update state and notify listeners
     */
    setState(updates) {
        this.state = { ...this.state, ...updates };
        this.notifyListeners();
    }

    /**
     * Subscribe to state changes
     */
    subscribe(listener) {
        this.listeners.push(listener);
        return () => {
            this.listeners = this.listeners.filter(l => l !== listener);
        };
    }

    /**
     * Notify all listeners of state change
     */
    notifyListeners() {
        this.listeners.forEach(listener => listener(this.state));
    }

    /**
     * Set results
     */
    setResults(results) {
        this.setState({ results });
    }

    /**
     * Set LLM response
     */
    setLLMResponse(llmResponse) {
        this.setState({ llmResponse });
    }

    /**
     * Set loading state
     */
    setLoading(loading) {
        this.setState({ loading });
    }

    /**
     * Set error
     */
    setError(error) {
        this.setState({ error });
    }

    /**
     * Clear error
     */
    clearError() {
        this.setState({ error: null });
    }

    /**
     * Update configuration
     */
    updateConfig(config) {
        this.setState({ config: { ...this.state.config, ...config } });
    }

    /**
     * Clear results
     */
    clearResults() {
        this.setState({ results: [], llmResponse: null, error: null });
    }
}

// Export singleton instance
const stateManager = new StateManager();
