// Production-level enhancements for Azul AI Campaign Generator

// Error handling and retry logic
class CampaignGenerator {
    constructor() {
        this.maxRetries = 3;
        this.retryDelay = 2000;
        this.currentRetry = 0;
        this.isGenerating = false;
        this.abortController = null;
        
        this.initializeEventListeners();
        this.setupPerformanceMonitoring();
        this.setupErrorReporting();
    }
    
    initializeEventListeners() {
        // Enhanced form validation
        const urlInput = document.getElementById('urlInput');
        const generateBtn = document.getElementById('generateBtn');
        
        if (urlInput) {
            urlInput.addEventListener('input', this.validateUrl.bind(this));
            urlInput.addEventListener('paste', this.handlePaste.bind(this));
        }
        
        if (generateBtn) {
            generateBtn.addEventListener('click', this.handleGenerate.bind(this));
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyboard.bind(this));
        
        // Page visibility handling
        document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
        
        // Network status monitoring
        window.addEventListener('online', this.handleOnline.bind(this));
        window.addEventListener('offline', this.handleOffline.bind(this));
    }
    
    validateUrl(event) {
        const url = event.target.value;
        const generateBtn = document.getElementById('generateBtn');
        const errorDiv = document.getElementById('urlError') || this.createErrorDiv();
        
        // Clear previous errors
        errorDiv.textContent = '';
        errorDiv.classList.add('hidden');
        
        if (!url) {
            generateBtn.disabled = true;
            return;
        }
        
        try {
            const urlObj = new URL(url);
            
            // Check for valid protocols
            if (!['http:', 'https:'].includes(urlObj.protocol)) {
                throw new Error('Only HTTP and HTTPS URLs are supported');
            }
            
            // Check for localhost or private IPs in production
            if (this.isProduction() && this.isLocalUrl(urlObj.hostname)) {
                throw new Error('Local URLs are not supported in production');
            }
            
            generateBtn.disabled = false;
            event.target.classList.remove('border-red-500');
            event.target.classList.add('border-green-500');
            
        } catch (error) {
            generateBtn.disabled = true;
            event.target.classList.remove('border-green-500');
            event.target.classList.add('border-red-500');
            
            errorDiv.textContent = error.message;
            errorDiv.classList.remove('hidden');
        }
    }
    
    createErrorDiv() {
        const errorDiv = document.createElement('div');
        errorDiv.id = 'urlError';
        errorDiv.className = 'text-red-600 text-sm mt-2 hidden';
        
        const urlInput = document.getElementById('urlInput');
        urlInput.parentNode.appendChild(errorDiv);
        
        return errorDiv;
    }
    
    isProduction() {
        return window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
    }
    
    isLocalUrl(hostname) {
        const localPatterns = [
            /^localhost$/,
            /^127\./,
            /^192\.168\./,
            /^10\./,
            /^172\.(1[6-9]|2[0-9]|3[0-1])\./
        ];
        
        return localPatterns.some(pattern => pattern.test(hostname));
    }
    
    handlePaste(event) {
        // Clean pasted URLs
        setTimeout(() => {
            const url = event.target.value.trim();
            if (url && !url.startsWith('http')) {
                event.target.value = 'https://' + url;
                this.validateUrl({ target: event.target });
            }
        }, 10);
    }
    
    handleKeyboard(event) {
        // Enter key to generate
        if (event.key === 'Enter' && event.target.id === 'urlInput') {
            event.preventDefault();
            this.handleGenerate();
        }
        
        // Escape key to cancel
        if (event.key === 'Escape' && this.isGenerating) {
            this.cancelGeneration();
        }
    }
    
    handleVisibilityChange() {
        if (document.hidden && this.isGenerating) {
            // Pause or adjust generation when tab is hidden
            console.log('Tab hidden during generation');
        }
    }
    
    handleOnline() {
        this.showNotification('Connection restored', 'success');
        // Retry failed requests if any
    }
    
    handleOffline() {
        this.showNotification('Connection lost. Please check your internet.', 'error');
        if (this.isGenerating) {
            this.cancelGeneration();
        }
    }
    
    async handleGenerate() {
        if (this.isGenerating) return;
        
        const urlInput = document.getElementById('urlInput');
        const url = urlInput.value.trim();
        
        if (!url) {
            this.showNotification('Please enter a valid URL', 'error');
            return;
        }
        
        this.currentRetry = 0;
        await this.generateWithRetry(url);
    }
    
    async generateWithRetry(url) {
        try {
            this.isGenerating = true;
            this.abortController = new AbortController();
            
            this.showLoading();
            this.trackEvent('campaign_generation_started', { url });
            
            const startTime = performance.now();
            
            const response = await fetch('/api/generate-campaign-ai', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url }),
                signal: this.abortController.signal,
                timeout: 120000 // 2 minute timeout
            });
            
            const endTime = performance.now();
            const duration = endTime - startTime;
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.hideLoading();
            this.displayResults(data);
            
            this.trackEvent('campaign_generation_success', { 
                url, 
                duration,
                features_used: data.features_used 
            });
            
            this.showNotification('Campaign generated successfully!', 'success');
            
        } catch (error) {
            console.error('Generation error:', error);
            
            if (error.name === 'AbortError') {
                this.showNotification('Generation cancelled', 'info');
                return;
            }
            
            if (this.currentRetry < this.maxRetries && !this.isNetworkError(error)) {
                this.currentRetry++;
                this.showNotification(`Retrying... (${this.currentRetry}/${this.maxRetries})`, 'warning');
                
                await this.delay(this.retryDelay);
                await this.generateWithRetry(url);
                return;
            }
            
            this.hideLoading();
            this.handleError(error, url);
            
        } finally {
            this.isGenerating = false;
            this.abortController = null;
        }
    }
    
    isNetworkError(error) {
        return error.message.includes('fetch') || 
               error.message.includes('network') ||
               error.message.includes('timeout');
    }
    
    cancelGeneration() {
        if (this.abortController) {
            this.abortController.abort();
        }
        this.isGenerating = false;
        this.hideLoading();
        this.showNotification('Generation cancelled', 'info');
    }
    
    handleError(error, url) {
        let userMessage = 'An error occurred while generating your campaign.';
        let suggestions = [];
        
        if (error.message.includes('timeout')) {
            userMessage = 'The request timed out. The website might be slow to respond.';
            suggestions = ['Try a different website', 'Check your internet connection'];
        } else if (error.message.includes('403') || error.message.includes('blocked')) {
            userMessage = 'This website blocks automated access.';
            suggestions = ['Try a different website', 'Use a publicly accessible site'];
        } else if (error.message.includes('404')) {
            userMessage = 'The website could not be found.';
            suggestions = ['Check the URL spelling', 'Ensure the website is online'];
        } else if (error.message.includes('network')) {
            userMessage = 'Network connection error.';
            suggestions = ['Check your internet connection', 'Try again in a moment'];
        }
        
        this.showErrorModal(userMessage, suggestions, error.message);
        
        this.trackEvent('campaign_generation_error', { 
            url, 
            error: error.message,
            retry_count: this.currentRetry 
        });
    }
    
    showErrorModal(message, suggestions, technicalError) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-md mx-4">
                <div class="flex items-center mb-4">
                    <div class="text-red-500 text-2xl mr-3">⚠️</div>
                    <h3 class="text-lg font-semibold text-gray-800">Generation Failed</h3>
                </div>
                <p class="text-gray-600 mb-4">${message}</p>
                ${suggestions.length > 0 ? `
                    <div class="mb-4">
                        <h4 class="font-medium text-gray-800 mb-2">Suggestions:</h4>
                        <ul class="list-disc list-inside text-sm text-gray-600">
                            ${suggestions.map(s => `<li>${s}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                <details class="mb-4">
                    <summary class="text-sm text-gray-500 cursor-pointer">Technical Details</summary>
                    <p class="text-xs text-gray-400 mt-2 font-mono">${technicalError}</p>
                </details>
                <div class="flex space-x-3">
                    <button onclick="this.closest('.fixed').remove()" 
                            class="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded">
                        Close
                    </button>
                    <button onclick="this.closest('.fixed').remove(); window.campaignGenerator.handleGenerate()" 
                            class="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded">
                        Try Again
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Auto-remove after 30 seconds
        setTimeout(() => {
            if (modal.parentNode) {
                modal.remove();
            }
        }, 30000);
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            warning: 'bg-yellow-500',
            info: 'bg-blue-500'
        };
        
        notification.className = `fixed top-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 transform translate-x-full transition-transform duration-300`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Slide in
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);
        
        // Slide out and remove
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }
    
    showLoading() {
        const loadingState = document.getElementById('loadingState');
        const resultsSection = document.getElementById('resultsSection');
        const generateBtn = document.getElementById('generateBtn');
        const btnText = document.getElementById('btnText');
        const btnSpinner = document.getElementById('btnSpinner');
        
        if (loadingState) loadingState.classList.remove('hidden');
        if (resultsSection) resultsSection.classList.add('hidden');
        if (generateBtn) generateBtn.disabled = true;
        if (btnText) btnText.textContent = 'Generating...';
        if (btnSpinner) btnSpinner.classList.remove('hidden');
        
        this.startProgressAnimation();
    }
    
    hideLoading() {
        const loadingState = document.getElementById('loadingState');
        const generateBtn = document.getElementById('generateBtn');
        const btnText = document.getElementById('btnText');
        const btnSpinner = document.getElementById('btnSpinner');
        
        if (loadingState) loadingState.classList.add('hidden');
        if (generateBtn) generateBtn.disabled = false;
        if (btnText) btnText.textContent = 'Generate AI Campaign';
        if (btnSpinner) btnSpinner.classList.add('hidden');
        
        this.stopProgressAnimation();
    }
    
    startProgressAnimation() {
        const progressBar = document.getElementById('progressBar');
        const loadingText = document.getElementById('loadingText');
        
        if (!progressBar || !loadingText) return;
        
        const steps = [
            { progress: 20, text: 'Scraping website content...' },
            { progress: 40, text: 'Analyzing brand with Qwen AI...' },
            { progress: 60, text: 'Generating campaign strategy...' },
            { progress: 80, text: 'Creating video ad...' },
            { progress: 95, text: 'Finalizing campaign...' }
        ];
        
        let currentStep = 0;
        
        this.progressInterval = setInterval(() => {
            if (currentStep < steps.length) {
                const step = steps[currentStep];
                progressBar.style.width = `${step.progress}%`;
                loadingText.textContent = step.text;
                currentStep++;
            }
        }, 3000);
    }
    
    stopProgressAnimation() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
        
        const progressBar = document.getElementById('progressBar');
        if (progressBar) {
            progressBar.style.width = '100%';
        }
    }
    
    displayResults(data) {
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.classList.remove('hidden');
            
            // Enhanced result display with animations
            this.animateResultsIn();
            
            // Display video data with enhanced features
            if (data.video_data && data.video_data.success) {
                this.displayVideoAd(data.video_data);
            }
            
            // Display other campaign data
            if (window.displayBrandAnalysis) {
                window.displayBrandAnalysis(data.brand_brief);
            }
            if (window.displayCampaignStrategy) {
                window.displayCampaignStrategy(data.campaign_strategy);
            }
            if (window.displaySocialMediaContent) {
                window.displaySocialMediaContent(data.campaign_strategy.social_media_posts);
            }
            if (window.displayPerformanceScore) {
                window.displayPerformanceScore(data.performance_score);
            }
            
            // Smooth scroll to results
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
    
    animateResultsIn() {
        const sections = document.querySelectorAll('#resultsSection > div');
        sections.forEach((section, index) => {
            section.style.opacity = '0';
            section.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                section.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                section.style.opacity = '1';
                section.style.transform = 'translateY(0)';
            }, index * 200);
        });
    }
    
    displayVideoAd(videoData) {
        // Enhanced video display with production features
        if (window.displayVideoAd) {
            window.displayVideoAd(videoData);
        }
        
        // Add video analytics tracking
        const video = document.getElementById('generatedVideo');
        if (video && videoData.video_url) {
            video.addEventListener('play', () => {
                this.trackEvent('video_play', { url: videoData.video_url });
            });
            
            video.addEventListener('ended', () => {
                this.trackEvent('video_complete', { url: videoData.video_url });
            });
        }
    }
    
    setupPerformanceMonitoring() {
        // Monitor page load performance
        window.addEventListener('load', () => {
            const perfData = performance.getEntriesByType('navigation')[0];
            this.trackEvent('page_load', {
                load_time: perfData.loadEventEnd - perfData.loadEventStart,
                dom_ready: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart
            });
        });
        
        // Monitor memory usage
        if ('memory' in performance) {
            setInterval(() => {
                const memory = performance.memory;
                if (memory.usedJSHeapSize > memory.jsHeapSizeLimit * 0.9) {
                    console.warn('High memory usage detected');
                }
            }, 30000);
        }
    }
    
    setupErrorReporting() {
        // Global error handler
        window.addEventListener('error', (event) => {
            this.trackEvent('javascript_error', {
                message: event.message,
                filename: event.filename,
                line: event.lineno,
                column: event.colno
            });
        });
        
        // Unhandled promise rejection handler
        window.addEventListener('unhandledrejection', (event) => {
            this.trackEvent('unhandled_promise_rejection', {
                reason: event.reason?.toString() || 'Unknown'
            });
        });
    }
    
    trackEvent(eventName, data = {}) {
        // Analytics tracking (can be extended with Google Analytics, etc.)
        console.log(`Event: ${eventName}`, data);
        
        // Store in localStorage for debugging
        try {
            const events = JSON.parse(localStorage.getItem('azul_events') || '[]');
            events.push({
                event: eventName,
                data,
                timestamp: new Date().toISOString(),
                url: window.location.href,
                userAgent: navigator.userAgent
            });
            
            // Keep only last 100 events
            if (events.length > 100) {
                events.splice(0, events.length - 100);
            }
            
            localStorage.setItem('azul_events', JSON.stringify(events));
        } catch (e) {
            console.warn('Failed to store event:', e);
        }
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.campaignGenerator = new CampaignGenerator();
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CampaignGenerator;
}

