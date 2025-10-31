/**
 * Electronic Signature Modal Component
 * 21 CFR Part 11 Compliant Signature Capture
 * 
 * Usage:
 *   showSignatureModal({
 *     action: 'Approve Change Control CC-2025-001',
 *     event_id: 123,
 *     event_type: 'change_control',
 *     onSuccess: function(signature) { ... },
 *     onCancel: function() { ... }
 *   });
 */

class SignatureModal {
    constructor() {
        this.modal = null;
        this.config = null;
        this.init();
    }

    init() {
        // Create modal HTML if it doesn't exist
        if (!document.getElementById('signatureModal')) {
            this.createModalHTML();
        }
        this.modal = new bootstrap.Modal(document.getElementById('signatureModal'));
        this.attachEventListeners();
    }

    createModalHTML() {
        const modalHTML = `
            <div class="modal fade" id="signatureModal" tabindex="-1" aria-labelledby="signatureModalLabel" aria-hidden="true" data-bs-backdrop="static" data-bs-keyboard="false">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content bg-dark border-primary">
                        <div class="modal-header border-primary">
                            <h5 class="modal-title text-primary" id="signatureModalLabel">
                                <i class="fas fa-pen-fancy me-2"></i>Electronic Signature Required
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <!-- FDA Part 11 Notice -->
                            <div class="alert alert-info border-info mb-3">
                                <small>
                                    <i class="fas fa-info-circle me-2"></i>
                                    <strong>21 CFR Part 11 Notice:</strong> By signing this document electronically, you acknowledge that 
                                    your electronic signature is legally binding and has the same effect as a handwritten signature.
                                </small>
                            </div>

                            <!-- Action Description -->
                            <div class="mb-3">
                                <label class="form-label text-light-purple fw-bold">Action Being Signed:</label>
                                <div class="p-3 bg-dark-purple border border-purple rounded">
                                    <p class="mb-0 text-white" id="signatureAction"></p>
                                </div>
                            </div>

                            <!-- Password Re-entry (Identity Verification) -->
                            <div class="mb-3">
                                <label for="signaturePassword" class="form-label text-light-purple fw-bold">
                                    Re-enter Your Password <span class="text-danger">*</span>
                                </label>
                                <small class="text-muted d-block mb-2">
                                    Required to verify your identity per §11.200
                                </small>
                                <div class="input-group">
                                    <span class="input-group-text bg-dark-purple border-purple">
                                        <i class="fas fa-lock text-primary"></i>
                                    </span>
                                    <input 
                                        type="password" 
                                        class="form-control bg-dark border-purple text-white" 
                                        id="signaturePassword" 
                                        placeholder="Enter your password"
                                        required
                                        autocomplete="current-password"
                                    >
                                    <button class="btn btn-outline-secondary" type="button" id="togglePassword">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                </div>
                                <div class="invalid-feedback" id="passwordError"></div>
                            </div>

                            <!-- Reason for Signing (Required by FDA) -->
                            <div class="mb-3">
                                <label for="signatureReason" class="form-label text-light-purple fw-bold">
                                    Reason for Signing <span class="text-danger">*</span>
                                </label>
                                <small class="text-muted d-block mb-2">
                                    Required to document meaning of signature per §11.50
                                </small>
                                <textarea 
                                    class="form-control bg-dark border-purple text-white" 
                                    id="signatureReason" 
                                    rows="3" 
                                    placeholder="Example: Reviewed and approved all changes. Testing completed successfully."
                                    required
                                    maxlength="500"
                                ></textarea>
                                <small class="text-muted">
                                    <span id="reasonCharCount">0</span>/500 characters
                                </small>
                                <div class="invalid-feedback" id="reasonError"></div>
                            </div>

                            <!-- Signature Details (Auto-captured) -->
                            <div class="alert alert-dark border-secondary">
                                <small class="text-muted">
                                    <strong>Auto-captured signature components:</strong><br>
                                    <i class="fas fa-user me-2"></i>User: <span id="signingUser"></span><br>
                                    <i class="fas fa-clock me-2"></i>Timestamp: <span id="signingTimestamp"></span><br>
                                    <i class="fas fa-network-wired me-2"></i>IP Address: <span id="signingIP"></span><br>
                                    <i class="fas fa-fingerprint me-2"></i>Signature Hash: <span class="text-primary">Generated upon signing</span>
                                </small>
                            </div>

                            <!-- Loading Spinner -->
                            <div class="text-center d-none" id="signatureLoading">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">Processing signature...</span>
                                </div>
                                <p class="text-muted mt-2">Processing signature...</p>
                            </div>
                        </div>
                        <div class="modal-footer border-primary">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" id="signatureCancel">
                                <i class="fas fa-times me-2"></i>Cancel
                            </button>
                            <button type="button" class="btn btn-primary" id="signatureSubmit">
                                <i class="fas fa-pen-fancy me-2"></i>Sign Electronically
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    attachEventListeners() {
        // Toggle password visibility
        document.getElementById('togglePassword')?.addEventListener('click', () => {
            const passwordInput = document.getElementById('signaturePassword');
            const icon = document.querySelector('#togglePassword i');
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.replace('fa-eye', 'fa-eye-slash');
            } else {
                passwordInput.type = 'password';
                icon.classList.replace('fa-eye-slash', 'fa-eye');
            }
        });

        // Character counter for reason
        document.getElementById('signatureReason')?.addEventListener('input', (e) => {
            document.getElementById('reasonCharCount').textContent = e.target.value.length;
        });

        // Submit signature
        document.getElementById('signatureSubmit')?.addEventListener('click', () => {
            this.submitSignature();
        });

        // Cancel signature
        document.getElementById('signatureCancel')?.addEventListener('click', () => {
            if (this.config?.onCancel) {
                this.config.onCancel();
            }
        });

        // Enter key submits
        document.getElementById('signaturePassword')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.submitSignature();
        });
    }

    show(config) {
        this.config = config;

        // Set action description
        document.getElementById('signatureAction').textContent = config.action || 'No action specified';

        // Set user info
        document.getElementById('signingUser').textContent = config.username || 'Current User';
        
        // Set timestamp (current time)
        const now = new Date();
        document.getElementById('signingTimestamp').textContent = now.toLocaleString();

        // Set IP (will be captured server-side, show placeholder)
        document.getElementById('signingIP').textContent = 'Will be captured automatically';

        // Clear previous inputs
        document.getElementById('signaturePassword').value = '';
        document.getElementById('signatureReason').value = '';
        document.getElementById('reasonCharCount').textContent = '0';

        // Clear errors
        document.getElementById('signaturePassword').classList.remove('is-invalid');
        document.getElementById('signatureReason').classList.remove('is-invalid');

        // Show modal
        this.modal.show();

        // Focus password field
        setTimeout(() => {
            document.getElementById('signaturePassword')?.focus();
        }, 500);
    }

    hide() {
        this.modal.hide();
    }

    validateForm() {
        let isValid = true;

        // Validate password
        const password = document.getElementById('signaturePassword').value.trim();
        if (!password) {
            document.getElementById('signaturePassword').classList.add('is-invalid');
            document.getElementById('passwordError').textContent = 'Password is required to verify your identity';
            isValid = false;
        } else {
            document.getElementById('signaturePassword').classList.remove('is-invalid');
        }

        // Validate reason
        const reason = document.getElementById('signatureReason').value.trim();
        if (!reason) {
            document.getElementById('signatureReason').classList.add('is-invalid');
            document.getElementById('reasonError').textContent = 'Reason for signing is required per 21 CFR Part 11';
            isValid = false;
        } else if (reason.length < 10) {
            document.getElementById('signatureReason').classList.add('is-invalid');
            document.getElementById('reasonError').textContent = 'Please provide a more detailed reason (minimum 10 characters)';
            isValid = false;
        } else {
            document.getElementById('signatureReason').classList.remove('is-invalid');
        }

        return isValid;
    }

    async submitSignature() {
        // Validate form
        if (!this.validateForm()) {
            return;
        }

        // Show loading
        document.getElementById('signatureLoading').classList.remove('d-none');
        document.getElementById('signatureSubmit').disabled = true;
        document.getElementById('signatureCancel').disabled = true;

        try {
            const password = document.getElementById('signaturePassword').value;
            const reason = document.getElementById('signatureReason').value;

            // Call API to create signature
            const response = await fetch('/api/signature/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    event_id: this.config.event_id,
                    event_type: this.config.event_type,
                    action: this.config.action,
                    reason: reason,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Success - hide modal and call callback
                this.hide();
                
                // Show success toast
                this.showToast('success', 'Electronic Signature Created', 
                    `Signature recorded at ${new Date(data.signature.timestamp).toLocaleString()}`);

                // Call success callback
                if (this.config?.onSuccess) {
                    this.config.onSuccess(data.signature);
                }
            } else {
                // Error - show message
                throw new Error(data.message || 'Failed to create signature');
            }

        } catch (error) {
            console.error('Signature error:', error);
            
            // Show error
            if (error.message.includes('password')) {
                document.getElementById('signaturePassword').classList.add('is-invalid');
                document.getElementById('passwordError').textContent = 'Incorrect password. Please try again.';
            } else {
                this.showToast('error', 'Signature Failed', error.message);
            }

        } finally {
            // Hide loading
            document.getElementById('signatureLoading').classList.add('d-none');
            document.getElementById('signatureSubmit').disabled = false;
            document.getElementById('signatureCancel').disabled = false;
        }
    }

    showToast(type, title, message) {
        // Create toast notification
        const toastHTML = `
            <div class="toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        <strong>${title}</strong><br>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;

        // Add to toast container or create one
        let container = document.getElementById('toastContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toastContainer';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }

        container.insertAdjacentHTML('beforeend', toastHTML);
        const toastElement = container.lastElementChild;
        const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 5000 });
        toast.show();

        // Remove after hiding
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }
}

// Create global instance
const signatureModal = new SignatureModal();

// Global function for easy access
function showSignatureModal(config) {
    signatureModal.show(config);
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SignatureModal, showSignatureModal };
}
