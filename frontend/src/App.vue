<template>
    <div id="app">
        <header class="header">
            <h1>🧠 LLM Knowledge Extractor</h1>
            <p>Extract insights and structured data from your text using AI</p>
        </header>

        <main class="main-content">
            <section class="input-section">
                <h2>Analyze Text</h2>
                <form @submit.prevent="analyzeText" class="input-form">
                    <textarea
                        v-model="inputText"
                        placeholder="Enter your text here... (article, blog post, document, etc.)"
                        class="text-input"
                        rows="8"
                        required
                    ></textarea>
                    <button
                        type="submit"
                        :disabled="isLoading || !inputText.trim()"
                        class="analyze-btn"
                    >
                        {{ isLoading ? 'Analyzing...' : 'Analyze Text' }}
                    </button>
                </form>

                <div v-if="error" class="error">
                    {{ error }}
                </div>
            </section>

            <section class="search-section">
                <h2>Search Past Analyses</h2>
                <div class="search-form">
                    <input
                        v-model="searchTopic"
                        placeholder="Search by topic..."
                        class="search-input"
                        @keyup.enter="searchAnalyses"
                    />
                    <input
                        v-model="searchKeyword"
                        placeholder="Search by keyword..."
                        class="search-input"
                        @keyup.enter="searchAnalyses"
                    />
                    <button @click="searchAnalyses" class="search-btn">
                        Search
                    </button>
                    <button @click="loadAllAnalyses" class="load-all-btn">
                        Load All
                    </button>
                </div>
            </section>

            <section class="results-section">
                <h2>
                    {{ currentAnalysis ? 'Current Analysis' : 'Past Analyses' }}
                </h2>

                <div v-if="currentAnalysis" class="analysis-card current">
                    <div class="analysis-header">
                        <h3>
                            {{ currentAnalysis.title || 'Latest Analysis' }}
                        </h3>
                        <span
                            class="sentiment"
                            :class="currentAnalysis.sentiment"
                        >
                            {{ currentAnalysis.sentiment.toUpperCase() }}
                        </span>
                    </div>

                    <div class="analysis-content">
                        <div class="summary">
                            <h4>Summary</h4>
                            <p>{{ currentAnalysis.summary }}</p>
                        </div>

                        <div class="metadata">
                            <div class="topics">
                                <h4>Topics</h4>
                                <div class="tags">
                                    <span
                                        v-for="topic in currentAnalysis.topics"
                                        :key="topic"
                                        class="tag"
                                    >
                                        {{ topic }}
                                    </span>
                                </div>
                            </div>

                            <div class="keywords">
                                <h4>Keywords</h4>
                                <div class="tags">
                                    <span
                                        v-for="keyword in currentAnalysis.keywords"
                                        :key="keyword"
                                        class="tag keyword"
                                    >
                                        {{ keyword }}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <details class="original-text">
                            <summary>View Original Text</summary>
                            <p>{{ currentAnalysis.original_text }}</p>
                        </details>
                    </div>
                </div>

                <div v-if="analyses.length > 0" class="analyses-list">
                    <div
                        v-for="analysis in analyses"
                        :key="analysis.id"
                        class="analysis-card"
                    >
                        <div class="analysis-header">
                            <h3>
                                {{
                                    analysis.title || `Analysis #${analysis.id}`
                                }}
                            </h3>
                            <div class="meta-info">
                                <span
                                    class="sentiment"
                                    :class="analysis.sentiment"
                                >
                                    {{ analysis.sentiment.toUpperCase() }}
                                </span>
                                <span class="date">{{
                                    formatDate(analysis.created_at)
                                }}</span>
                            </div>
                        </div>

                        <div class="analysis-content">
                            <div class="summary">
                                <p>{{ analysis.summary }}</p>
                            </div>

                            <div class="metadata">
                                <div class="topics">
                                    <strong>Topics:</strong>
                                    <span
                                        v-for="topic in analysis.topics"
                                        :key="topic"
                                        class="tag small"
                                    >
                                        {{ topic }}
                                    </span>
                                </div>

                                <div class="keywords">
                                    <strong>Keywords:</strong>
                                    <span
                                        v-for="keyword in analysis.keywords"
                                        :key="keyword"
                                        class="tag small keyword"
                                    >
                                        {{ keyword }}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div
                    v-else-if="!isLoading && !currentAnalysis"
                    class="no-results"
                >
                    <p>
                        No analyses found. Submit some text above to get
                        started!
                    </p>
                </div>
            </section>
        </main>
    </div>
</template>

<script>
import axios from 'axios'

export default {
    name: 'App',
    data() {
        return {
            inputText: '',
            searchTopic: '',
            searchKeyword: '',
            currentAnalysis: null,
            analyses: [],
            isLoading: false,
            error: null,
            apiBaseUrl: 'http://localhost:8000',
        }
    },
    methods: {
        async analyzeText() {
            if (!this.inputText.trim()) {
                this.error = 'Please enter some text to analyze'
                return
            }

            this.isLoading = true
            this.error = null
            this.currentAnalysis = null

            try {
                const response = await axios.post(
                    `${this.apiBaseUrl}/analyze`,
                    {
                        text: this.inputText,
                    },
                )

                this.currentAnalysis = response.data
                this.inputText = ''

                this.loadAllAnalyses()
            } catch (error) {
                console.error('Analysis failed:', error)
                this.error =
                    error.response?.data?.detail ||
                    'Failed to analyze text. Please try again.'
            } finally {
                this.isLoading = false
            }
        },

        async searchAnalyses() {
            this.isLoading = true
            this.error = null
            this.currentAnalysis = null

            try {
                const params = new URLSearchParams()
                if (this.searchTopic.trim())
                    params.append('topic', this.searchTopic)
                if (this.searchKeyword.trim())
                    params.append('keyword', this.searchKeyword)

                const response = await axios.get(
                    `${this.apiBaseUrl}/search?${params}`,
                )
                this.analyses = response.data
            } catch (error) {
                console.error('Search failed:', error)
                this.error = 'Failed to search analyses. Please try again.'
            } finally {
                this.isLoading = false
            }
        },

        async loadAllAnalyses() {
            try {
                const response = await axios.get(`${this.apiBaseUrl}/analyses`)
                this.analyses = response.data
            } catch (error) {
                console.error('Failed to load analyses:', error)
                this.error = 'Failed to load past analyses.'
            }
        },

        formatDate(dateString) {
            const date = new Date(dateString)
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
        },
    },

    mounted() {
        this.loadAllAnalyses()
    },
}
</script>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto',
        'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans',
        'Helvetica Neue', sans-serif;
    background-color: #f5f7fa;
    color: #333;
    line-height: 1.6;
}

#app {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

.header {
    text-align: center;
    padding: 2rem 0;
    border-bottom: 2px solid #e1e8ed;
    margin-bottom: 2rem;
}

.header h1 {
    color: #2c3e50;
    margin: 0 0 0.5rem 0;
    font-size: 2.5rem;
}

.header p {
    color: #7f8c8d;
    font-size: 1.2rem;
    margin: 0;
}

.main-content {
    display: grid;
    gap: 2rem;
}

section {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

h2 {
    color: #2c3e50;
    margin-top: 0;
    margin-bottom: 1.5rem;
    border-bottom: 2px solid #3498db;
    padding-bottom: 0.5rem;
}

.input-form {
    display: grid;
    gap: 1rem;
}

.text-input {
    width: 100%;
    padding: 1rem;
    border: 2px solid #e1e8ed;
    border-radius: 8px;
    font-size: 1rem;
    font-family: inherit;
    resize: vertical;
    transition: border-color 0.3s;
}

.text-input:focus {
    outline: none;
    border-color: #3498db;
}

.analyze-btn {
    background: #3498db;
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 8px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.3s;
    justify-self: start;
}

.analyze-btn:hover:not(:disabled) {
    background: #2980b9;
}

.analyze-btn:disabled {
    background: #bdc3c7;
    cursor: not-allowed;
}

.search-form {
    display: grid;
    grid-template-columns: 1fr 1fr auto auto;
    gap: 1rem;
    align-items: center;
}

.search-input {
    padding: 0.75rem;
    border: 2px solid #e1e8ed;
    border-radius: 6px;
    font-size: 1rem;
    transition: border-color 0.3s;
}

.search-input:focus {
    outline: none;
    border-color: #3498db;
}

.search-btn,
.load-all-btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.3s;
}

.search-btn {
    background: #27ae60;
    color: white;
}

.search-btn:hover {
    background: #219a52;
}

.load-all-btn {
    background: #95a5a6;
    color: white;
}

.load-all-btn:hover {
    background: #7f8c8d;
}

.analysis-card {
    border: 1px solid #e1e8ed;
    border-radius: 10px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    background: white;
    transition: transform 0.2s, box-shadow 0.2s;
}

.analysis-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.analysis-card.current {
    border: 2px solid #3498db;
    background: #f8fbff;
}

.analysis-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    flex-wrap: wrap;
    gap: 1rem;
}

.analysis-header h3 {
    margin: 0;
    color: #2c3e50;
    flex: 1;
}

.meta-info {
    display: flex;
    gap: 1rem;
    align-items: center;
}

.sentiment {
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
}

.sentiment.positive {
    background: #d5f4e6;
    color: #27ae60;
}

.sentiment.negative {
    background: #fadbd8;
    color: #e74c3c;
}

.sentiment.neutral {
    background: #e8f4fd;
    color: #3498db;
}

.date {
    color: #7f8c8d;
    font-size: 0.9rem;
}

.analysis-content {
    display: grid;
    gap: 1.5rem;
}

.summary h4 {
    margin: 0 0 0.5rem 0;
    color: #34495e;
}

.summary p {
    margin: 0;
    color: #2c3e50;
    font-size: 1.1rem;
    line-height: 1.6;
}

.metadata {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
}

.metadata h4 {
    margin: 0 0 0.75rem 0;
    color: #34495e;
    font-size: 1rem;
}

.tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.tag {
    background: #3498db;
    color: white;
    padding: 0.4rem 0.8rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
}

.tag.small {
    padding: 0.25rem 0.6rem;
    font-size: 0.8rem;
}

.tag.keyword {
    background: #e67e22;
}

.original-text {
    margin-top: 1rem;
    border: 1px solid #e1e8ed;
    border-radius: 8px;
    padding: 1rem;
}

.original-text summary {
    cursor: pointer;
    font-weight: 600;
    color: #3498db;
    margin-bottom: 1rem;
}

.original-text p {
    margin: 1rem 0 0 0;
    color: #555;
    white-space: pre-wrap;
    line-height: 1.6;
}

.error {
    background: #fadbd8;
    color: #e74c3c;
    padding: 1rem;
    border-radius: 8px;
    margin-top: 1rem;
    border: 1px solid #f1948a;
}

.no-results {
    text-align: center;
    color: #7f8c8d;
    font-style: italic;
    padding: 2rem;
}

@media (max-width: 768px) {
    .search-form {
        grid-template-columns: 1fr;
    }

    .metadata {
        grid-template-columns: 1fr;
        gap: 1rem;
    }

    .analysis-header {
        flex-direction: column;
        align-items: flex-start;
    }

    .meta-info {
        align-self: stretch;
        justify-content: space-between;
    }

    .header h1 {
        font-size: 2rem;
    }

    #app {
        padding: 0 1rem;
    }

    section {
        padding: 1.5rem;
    }
}
</style>
