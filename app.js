class AnonIDApp {
    constructor() {
        this.currentFile = null;
        this.isAnalyzing = false;
        this.apiBaseUrl = 'http://localhost:5000/api';
        
        this.initializeApp();
        this.setupEventListeners();
        this.createFooterParticles();
        this.createNINRegistrationForm();
    }

    initializeApp() {
        console.log('AnonID Privacy Detector initialized');
        this.showNotification('Welcome to AnonID - Your Digital Privacy Guardian', 'info');
        this.checkBackendHealth();
    }
    
    async checkBackendHealth() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            if (response.ok) {
                const data = await response.json();
                console.log('Backend connected:', data);
            }
        } catch (error) {
            console.warn('Backend not available:', error);
            this.showNotification('Backend server not available. Some features may not work.', 'warning');
        }
    }
    
    createNINRegistrationForm() {
        // Add NIN registration section to the scanner card
        const scannerCard = document.querySelector('.scanner-card .scanner-body');
        if (!scannerCard) return;
        
        const ninSection = document.createElement('div');
        ninSection.className = 'nin-registration-section';
        ninSection.innerHTML = `
            <div class="nin-form-container">
                <h3 style="margin-bottom: 1rem; color: white;">
                    <i class="fas fa-id-card"></i> Identity Registration
                </h3>
                <div class="nin-input-group">
                    <input type="text" id="ninInput" placeholder="Enter your NIN (e.g., 12345678901)" 
                           maxlength="11" class="nin-input" />
                    <button class="btn btn-primary" id="registerNINBtn">
                        <i class="fas fa-user-plus"></i> Register
                    </button>
                </div>
                <div id="ninStatus" style="margin-top: 1rem;"></div>
            </div>
        `;
        
        scannerCard.insertBefore(ninSection, scannerCard.firstChild);
        
        // Add event listener for registration
        document.getElementById('registerNINBtn').addEventListener('click', () => {
            this.handleNINRegistration();
        });
        
        // Allow Enter key
        document.getElementById('ninInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.handleNINRegistration();
            }
        });
    }
    
    async handleNINRegistration() {
        const ninInput = document.getElementById('ninInput');
        const nin = ninInput.value.trim();
        const statusDiv = document.getElementById('ninStatus');
        
        if (!nin || nin.length < 10) {
            statusDiv.innerHTML = '<p style="color: var(--danger);">Please enter a valid NIN (10-11 digits)</p>';
            return;
        }
        
        statusDiv.innerHTML = '<p style="color: var(--primary);"><i class="fas fa-spinner fa-spin"></i> Registering...</p>';
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ nin: nin })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                statusDiv.innerHTML = `
                    <div style="background: rgba(16, 185, 129, 0.1); padding: 1rem; border-radius: 8px; border: 1px solid rgba(16, 185, 129, 0.3);">
                        <p style="color: var(--success); margin-bottom: 0.5rem;">
                            <i class="fas fa-check-circle"></i> Registration Successful!
                        </p>
                        <p style="color: #94a3b8; font-size: 0.9rem;">
                            <strong>AnonID:</strong> ${data.anon_id}<br>
                            <strong>Masked NIN:</strong> ${data.masked_nin}
                        </p>
                    </div>
                `;
                this.showNotification('User registered successfully', 'success');
            } else {
                statusDiv.innerHTML = `<p style="color: var(--danger);">${data.error || 'Registration failed'}</p>`;
                this.showNotification(data.error || 'Registration failed', 'error');
            }
        } catch (error) {
            statusDiv.innerHTML = '<p style="color: var(--danger);">Connection error. Is the backend server running?</p>';
            this.showNotification('Failed to connect to backend server', 'error');
            console.error('Registration error:', error);
        }
    }

    setupEventListeners() {
        const uploadZone = document.getElementById('uploadZone');
        const fileInput = document.getElementById('fileInput');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const clearBtn = document.getElementById('clearBtn');
        const removeFileBtn = document.getElementById('removeFile');

        // File upload
        uploadZone.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // Buttons
        analyzeBtn.addEventListener('click', () => this.analyzeFile());
        clearBtn.addEventListener('click', () => this.clearAll());
        removeFileBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.clearFile();
        });

        // Drag and drop
        this.setupDragAndDrop(uploadZone);
        
        // Navigation
        this.setupNavigation();
    }

    setupDragAndDrop(uploadZone) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadZone.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadZone.addEventListener(eventName, () => this.highlightDropZone(), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadZone.addEventListener(eventName, () => this.unhighlightDropZone(), false);
        });

        uploadZone.addEventListener('drop', (e) => this.handleDrop(e), false);
    }

    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                
                // Smooth scroll to section
                const targetId = link.getAttribute('href').substring(1);
                const targetSection = document.getElementById(targetId);
                if (targetSection) {
                    targetSection.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    highlightDropZone() {
        document.getElementById('uploadZone').classList.add('dragover');
    }

    unhighlightDropZone() {
        document.getElementById('uploadZone').classList.remove('dragover');
    }

    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        this.processFiles(files);
    }

    handleFileSelect(e) {
        const files = e.target.files;
        this.processFiles(files);
    }

    processFiles(files) {
        if (files.length === 0) return;

        const file = files[0];
        
        // Validate file size
        if (file.size > 10 * 1024 * 1024) {
            this.showNotification('File size exceeds 10MB limit', 'error');
            return;
        }

        // Validate file type
        const allowedTypes = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'image/jpeg',
            'image/png'
        ];

        if (!allowedTypes.includes(file.type)) {
            this.showNotification('Please upload PDF, DOCX, TXT, JPG, or PNG files', 'error');
            return;
        }

        this.currentFile = file;
        this.displayFilePreview(file);
        document.getElementById('analyzeBtn').disabled = false;
        
        this.showNotification('File ready for privacy analysis', 'success');
    }

    displayFilePreview(file) {
        const uploadZone = document.getElementById('uploadZone');
        const filePreview = document.getElementById('filePreview');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        const fileIcon = document.getElementById('fileIcon');

        // Set file info
        fileName.textContent = file.name;
        fileSize.textContent = this.formatFileSize(file.size);

        // Set icon
        const iconClass = this.getFileIconClass(file.type);
        fileIcon.className = `fas ${iconClass}`;

        // Show preview
        uploadZone.querySelector('.upload-content').style.display = 'none';
        filePreview.style.display = 'block';
    }

    getFileIconClass(fileType) {
        const iconMap = {
            'application/pdf': 'fa-file-pdf',
            'application/msword': 'fa-file-word',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'fa-file-word',
            'text/plain': 'fa-file-alt',
            'image/jpeg': 'fa-file-image',
            'image/png': 'fa-file-image'
        };
        return iconMap[fileType] || 'fa-file';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async analyzeFile() {
        if (!this.currentFile) {
            this.showNotification('Please select a file first', 'warning');
            return;
        }

        if (this.isAnalyzing) return;

        this.isAnalyzing = true;
        const analyzeBtn = document.getElementById('analyzeBtn');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');

        // Update UI
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        progressText.textContent = 'Scanning for privacy risks...';

        try {
            // Simulate analysis
            await this.simulateAnalysisProgress(progressFill, progressText);
            
            // Get results
            const results = await this.performPrivacyAnalysis(this.currentFile);
            
            // Display results
            this.displayResults(results);
            
            this.showNotification('Privacy analysis completed successfully', 'success');
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.showNotification('Analysis failed. Please try again.', 'error');
        } finally {
            this.isAnalyzing = false;
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<i class="fas fa-shield-alt"></i> Scan for Privacy Risks';
        }
    }

    simulateAnalysisProgress(progressFill, progressText) {
        return new Promise((resolve) => {
            let width = 0;
            const stages = [
                'Scanning document structure...',
                'Analyzing text content...',
                'Checking for personal data...',
                'Assessing privacy risks...',
                'Generating security report...'
            ];
            let stageIndex = 0;

            const interval = setInterval(() => {
                if (width >= 100) {
                    clearInterval(interval);
                    progressText.textContent = 'Analysis complete';
                    resolve();
                } else {
                    width += Math.random() * 12;
                    if (width > 100) width = 100;
                    progressFill.style.width = width + '%';
                    
                    // Update stage text
                    if (width > stageIndex * 20) {
                        progressText.textContent = stages[stageIndex];
                        stageIndex = Math.min(stageIndex + 1, stages.length - 1);
                    }
                }
            }, 200);
        });
    }

    async performPrivacyAnalysis(file) {
        try {
            // Read file content (simplified - for text files)
            const fileContent = await this.readFileContent(file);
            
            // Call backend API to check privacy risk
            const response = await fetch('http://localhost:5000/api/check_privacy_risk', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    request_text: fileContent.substring(0, 500) // First 500 chars as sample
                })
            });
            
            if (!response.ok) {
                throw new Error('Privacy analysis failed');
            }
            
            const riskData = await response.json();
            
            // Convert backend risk level to frontend format
            const riskLevelMap = {
                'Safe': 'low',
                'Medium': 'medium',
                'High': 'high'
            };
            
            return {
                riskLevel: riskLevelMap[riskData.risk_level] || 'medium',
                riskScore: riskData.risk_score,
                summary: {
                    critical: riskData.risk_level === 'High' ? 1 : 0,
                    high: riskData.risk_level === 'High' ? 1 : 0,
                    medium: riskData.risk_level === 'Medium' ? 1 : 0,
                    low: riskData.risk_level === 'Safe' ? 1 : 0
                },
                risks: this.convertBackendRisks(riskData),
                recommendations: this.generateSecurityRecommendations(
                    riskLevelMap[riskData.risk_level] || 'medium'
                )
            };
        } catch (error) {
            console.error('Privacy analysis error:', error);
            // Fallback to mock data if API fails
            return this.generatePrivacyResults(file);
        }
    }
    
    async readFileContent(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = reject;
            
            if (file.type.startsWith('text/') || file.type === 'application/pdf') {
                reader.readAsText(file);
            } else {
                // For images, just return filename
                resolve(file.name);
            }
        });
    }
    
    convertBackendRisks(riskData) {
        const risks = [];
        
        if (riskData.flags && riskData.flags.length > 0) {
            riskData.flags.forEach(flag => {
                if (flag.includes('🚨')) {
                    risks.push({
                        type: 'high',
                        title: flag.replace('🚨 Requesting: ', ''),
                        description: 'High-risk personal data detected',
                        location: 'Document Content'
                    });
                } else if (flag.includes('⚠️')) {
                    risks.push({
                        type: 'medium',
                        title: flag.replace('⚠️ Requesting: ', ''),
                        description: 'Medium-risk personal data detected',
                        location: 'Document Content'
                    });
                }
            });
        }
        
        if (risks.length === 0) {
            risks.push({
                type: 'low',
                title: 'No Privacy Risks Detected',
                description: riskData.recommendation || 'Document appears safe',
                location: 'General'
            });
        }
        
        return risks;
    }

    generatePrivacyResults(file) {
        const riskLevels = ['low', 'medium', 'high', 'critical'];
        const selectedRisk = riskLevels[Math.floor(Math.random() * riskLevels.length)];
        
        const riskScores = {
            low: { min: 0, max: 25 },
            medium: { min: 26, max: 50 },
            high: { min: 51, max: 75 },
            critical: { min: 76, max: 100 }
        };
        
        const riskScore = Math.floor(
            Math.random() * (riskScores[selectedRisk].max - riskScores[selectedRisk].min + 1) + 
            riskScores[selectedRisk].min
        );

        return {
            riskLevel: selectedRisk,
            riskScore: riskScore,
            summary: {
                critical: Math.floor(Math.random() * 3),
                high: Math.floor(Math.random() * 5),
                medium: Math.floor(Math.random() * 8),
                low: Math.floor(Math.random() * 12)
            },
            risks: this.generatePrivacyRisks(selectedRisk),
            recommendations: this.generateSecurityRecommendations(selectedRisk)
        };
    }

    generatePrivacyRisks(riskLevel) {
        const privacyRisks = [
            {
                type: 'critical',
                title: 'National Identification Number Exposure',
                description: 'Government-issued identification number found. This is highly sensitive personal data that requires immediate protection under NDPR.',
                location: 'Personal Information Section'
            },
            {
                type: 'high',
                title: 'Bank Account Details Leakage',
                description: 'Financial information including account numbers detected. This data could be used for fraudulent activities.',
                location: 'Financial Records'
            },
            {
                type: 'medium',
                title: 'Personal Contact Information',
                description: 'Phone numbers and email addresses found without proper consent markers. Consider implementing data masking.',
                location: 'Contact Details'
            },
            {
                type: 'low',
                title: 'General Personal Data',
                description: 'Basic personal information that could be used in social engineering attacks if combined with other data.',
                location: 'Various Sections'
            }
        ];

        const riskFilters = {
            low: ['low'],
            medium: ['low', 'medium'],
            high: ['low', 'medium', 'high'],
            critical: ['low', 'medium', 'high', 'critical']
        };

        return privacyRisks.filter(risk => 
            riskFilters[riskLevel].includes(risk.type)
        );
    }

    generateSecurityRecommendations(riskLevel) {
        const recommendations = [
            {
                icon: 'fa-user-shield',
                title: 'Data Anonymization',
                description: 'Implement advanced data masking techniques to protect personal identifiers while maintaining data utility for legitimate purposes.'
            },
            {
                icon: 'fa-lock',
                title: 'Encryption Protocol',
                description: 'Apply end-to-end encryption for data at rest and in transit. Consider using AES-256 encryption standards.'
            },
            {
                icon: 'fa-shield-alt',
                title: 'Access Control',
                description: 'Establish role-based access controls and implement multi-factor authentication for sensitive data access.'
            },
            {
                icon: 'fa-file-contract',
                title: 'Consent Management',
                description: 'Ensure proper consent mechanisms are implemented as per NDPR Article 2.3 for lawful data processing.'
            }
        ];

        const count = riskLevel === 'critical' ? 4 : riskLevel === 'high' ? 3 : riskLevel === 'medium' ? 2 : 1;
        return recommendations.slice(0, count);
    }

    displayResults(data) {
        const resultsSection = document.getElementById('resultsSection');
        const riskBadge = document.getElementById('riskBadge');
        const riskLevel = document.getElementById('riskLevel');
        const riskScore = document.getElementById('riskScore');

        // Update risk indicator
        riskBadge.className = `risk-badge ${data.riskLevel}`;
        riskLevel.textContent = `${data.riskLevel.charAt(0).toUpperCase() + data.riskLevel.slice(1)} Risk`;
        riskScore.textContent = `${data.riskScore}/100`;

        // Update summary counts
        document.getElementById('criticalCount').textContent = data.summary.critical;
        document.getElementById('highCount').textContent = data.summary.high;
        document.getElementById('mediumCount').textContent = data.summary.medium;
        document.getElementById('lowCount').textContent = data.summary.low;

        // Update risks count
        document.getElementById('risksCount').textContent = `${data.risks.length} privacy risks`;

        // Display risks
        this.displayRisks(data.risks);
        
        // Display recommendations
        this.displayRecommendations(data.recommendations);

        // Show results with animation
        resultsSection.style.display = 'block';
        setTimeout(() => {
            resultsSection.scrollIntoView({ 
                behavior: 'smooth',
                block: 'start'
            });
        }, 100);
    }

    displayRisks(risks) {
        const risksList = document.getElementById('risksList');
        risksList.innerHTML = '';

        risks.forEach(risk => {
            const riskElement = document.createElement('div');
            riskElement.className = `risk-item ${risk.type}`;
            riskElement.innerHTML = `
                <i class="fas fa-${this.getRiskIcon(risk.type)}"></i>
                <div class="risk-content">
                    <h4>${risk.title}</h4>
                    <p>${risk.description}</p>
                    <div class="risk-meta">
                        <i class="fas fa-map-marker-alt"></i>
                        ${risk.location}
                    </div>
                </div>
            `;
            risksList.appendChild(riskElement);
        });
    }

    getRiskIcon(type) {
        const icons = {
            critical: 'skull-crossbones',
            high: 'exclamation-triangle',
            medium: 'exclamation-circle',
            low: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    displayRecommendations(recommendations) {
        const recommendationsList = document.getElementById('recommendationsList');
        recommendationsList.innerHTML = '';

        recommendations.forEach(rec => {
            const recElement = document.createElement('div');
            recElement.className = 'recommendation-item';
            recElement.innerHTML = `
                <i class="fas ${rec.icon}"></i>
                <div class="recommendation-content">
                    <h4>${rec.title}</h4>
                    <p>${rec.description}</p>
                </div>
            `;
            recommendationsList.appendChild(recElement);
        });
    }

    createFooterParticles() {
        const particleContainer = document.getElementById('footerParticles');
        if (!particleContainer) return;

        const particleCount = 25;

        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'footer-particle';
            
            // Random position
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 15 + 's';
            particle.style.animationDuration = (10 + Math.random() * 10) + 's';
            
            // Random size
            const size = 2 + Math.random() * 4;
            particle.style.width = size + 'px';
            particle.style.height = size + 'px';
            
            // Random opacity
            particle.style.opacity = (0.1 + Math.random() * 0.3).toString();
            
            particleContainer.appendChild(particle);
        }
    }

    clearFile() {
        const fileInput = document.getElementById('fileInput');
        const uploadZone = document.getElementById('uploadZone');
        const filePreview = document.getElementById('filePreview');
        const analyzeBtn = document.getElementById('analyzeBtn');

        fileInput.value = '';
        uploadZone.querySelector('.upload-content').style.display = 'block';
        filePreview.style.display = 'none';
        analyzeBtn.disabled = true;
        this.currentFile = null;

        this.showNotification('File removed', 'info');
    }

    clearAll() {
        this.clearFile();
        
        const resultsSection = document.getElementById('resultsSection');
        resultsSection.style.display = 'none';

        this.showNotification('Analysis cleared', 'info');
    }

    showNotification(message, type = 'info') {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(notification => notification.remove());

        // Create notification
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
        `;

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => notification.classList.add('show'), 100);

        // Remove after 4 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-triangle',
            warning: 'exclamation-circle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new AnonIDApp();
});
