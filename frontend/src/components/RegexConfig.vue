<style scoped>
@reference "@/style.css";

.config-card {
    @apply bg-bg-card/80 backdrop-blur-xl border border-border-default rounded-2xl shadow-2xl;
}

.toggle-group {
    @apply flex bg-bg-input rounded-lg p-1;
}

.toggle-btn {
    @apply flex-1 px-3 py-2 rounded-md font-medium transition-all duration-200 text-text-tertiary text-sm;
}

.toggle-btn.active {
    @apply bg-accent-600 text-white shadow-lg;
}

.input-label {
    @apply block text-sm font-medium text-text-secondary mb-2;
}

.input-field {
    @apply w-full px-4 py-3 rounded-lg bg-bg-input border border-border-default text-text-primary;
    @apply transition-all duration-200 focus:outline-none focus:border-accent-500 focus:ring-2 focus:ring-border-focus;
    @apply placeholder:text-text-muted disabled:opacity-50;
}

.input-field.font-mono {
    @apply font-mono;
}

.helper-text {
    @apply text-xs text-text-muted mt-1;
}

.btn-primary {
    @apply px-6 py-3 rounded-lg font-semibold text-white cursor-pointer;
    @apply bg-accent-600 border border-border-default shadow-lg;
    @apply transition-all duration-200 transform hover:-translate-y-0.5 hover:shadow-accent active:translate-y-0 disabled:opacity-50;
}

.btn-accent {
    @apply px-6 py-3 rounded-lg font-semibold text-white;
    @apply bg-cyan-600 border border-border-default shadow-lg;
    @apply transition-all duration-200 transform hover:-translate-y-0.5 hover:shadow-cyan-500/20 disabled:opacity-50;
}

.remove-btn {
    @apply px-2 py-1 text-error hover:text-red-300 bg-error-bg hover:bg-red-500/20 rounded border border-error-border transition-colors disabled:opacity-50;
}

.add-btn {
    @apply px-3 py-1 text-cyan-400 hover:text-cyan-300 bg-cyan-500/10 hover:bg-cyan-500/20 rounded border border-cyan-500/20 transition-colors disabled:opacity-50;
}

.suggested-card {
    @apply bg-bg-input rounded-xl p-4 space-y-4 border border-border-subtle;
}

.badge-label {
    @apply block text-[10px] uppercase tracking-wider font-bold text-text-muted mb-1.5;
}

.pattern-display {
    @apply block text-cyan-400 font-mono text-sm bg-bg-sunken p-3 rounded-lg border border-border-subtle;
}

.result-badge {
    @apply text-xs px-2.5 py-1 rounded-full font-medium;
}

.badge-success {
    @apply bg-success-bg text-success border border-success-border;
}

.badge-error {
    @apply bg-error-bg text-error border border-error-border;
}

.pencil-btn {
    @apply p-2 rounded-lg text-text-muted hover:text-cyan-400 hover:bg-bg-input-hover transition-colors shrink-0 disabled:opacity-50;
}

.active-pattern-section {
    @apply bg-accent-500/10 border border-accent-500/20 rounded-xl p-4;
}

.save-section {
    @apply bg-bg-input/60 rounded-xl p-4 border border-border-subtle;
}

.btn-save {
    @apply px-4 py-3 rounded-lg font-semibold text-white text-sm shrink-0;
    @apply bg-success hover:bg-emerald-500 border border-border-default;
    @apply transition-colors disabled:opacity-50;
}

.preset-grid {
    @apply grid grid-cols-1 gap-2;
}

.preset-card {
    @apply flex flex-col gap-0.5 text-left px-3 py-2.5 rounded-lg border border-border-subtle;
    @apply bg-bg-input/60 hover:bg-bg-input-hover hover:border-accent-500/40;
    @apply transition-all duration-150 disabled:opacity-50 cursor-pointer;
}

.preset-name {
    @apply text-sm font-medium text-text-secondary;
}

.preset-pattern {
    @apply text-xs text-cyan-400 font-mono truncate;
}

.preset-desc {
    @apply text-xs text-text-muted;
}

.empty-state {
    @apply text-center text-text-muted text-sm py-6 rounded-lg border border-dashed border-border-default;
}

.loading-state {
    @apply flex flex-col items-center justify-center gap-3 py-8 text-center;
}

.spinner {
    @apply w-8 h-8 border-4 border-accent-500/30 border-t-accent-500 rounded-full animate-spin;
}

.error-state {
    @apply text-center py-6 px-4 rounded-lg border border-error-border bg-error-bg;
}

.saved-pattern-row {
    @apply flex items-center gap-1 rounded-lg border border-border-subtle bg-bg-input/40 overflow-hidden;
}

.saved-pattern-main {
    @apply flex flex-col gap-0.5 text-left px-3 py-2.5 flex-1 min-w-0;
    @apply hover:bg-bg-input-hover/40 transition-colors disabled:opacity-50 cursor-pointer;
}

.action-btn {
    @apply px-2.5 py-2 text-sm font-medium shrink-0 transition-colors disabled:opacity-50;
}

.pencil-action-btn {
    @apply text-text-muted hover:text-cyan-400 hover:bg-bg-input-hover rounded;
}

.builtin-badge {
    @apply text-[10px] px-1.5 py-0.5 rounded font-medium bg-accent-500/15 text-accent-400 border border-accent-500/20;
}

.delete-btn {
    @apply text-error hover:text-red-400 hover:bg-error-bg mr-1 rounded;
}

.confirm-btn {
    @apply text-success hover:text-emerald-300 hover:bg-success-bg rounded;
}

.cancel-btn {
    @apply text-text-muted hover:text-text-secondary hover:bg-bg-input-hover mr-1 rounded;
}
</style>
