.app-layout {
  @apply min-h-screen flex flex-col bg-bg-page text-text-tertiary font-sans selection:bg-accent-500/30;
}

.main-header {
  @apply py-space-4 border-b border-border-subtle bg-bg-base/40 backdrop-blur-md sticky top-0 z-50;
}

.logo-container {
  @apply w-12 h-12 rounded-2xl bg-linear-to-br from-accent-500 to-cyan-500 shadow-lg shadow-accent-500/20 flex items-center justify-center;
}

.app-title {
  @apply text-2xl font-bold text-text-primary tracking-tight leading-none;
}

.status-indicator {
  @apply flex items-center gap-2 mt-1;
}

.status-dot {
  @apply w-2 h-2 rounded-full;
}

.status-online {
  @apply bg-success;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
}

.status-offline {
  @apply bg-error;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
}

/* Tab navigation */
.tab-nav {
  @apply border-b border-border-subtle bg-bg-base/30;
}

.tab-btn {
  @apply inline-flex items-center gap-2 px-5 py-3 text-sm font-semibold transition-all relative;
}

.tab-active {
  @apply text-text-primary border-b-2 border-accent-500;
}

.tab-inactive {
  @apply text-text-muted hover:text-text-secondary;
}

.tab-badge {
  @apply inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-black uppercase tracking-wider
         bg-accent-600/70 text-accent-200 leading-none;
}

.btn-docs {
  @apply px-5 py-2.5 rounded-xl bg-accent-600 text-white font-semibold text-sm transition-all;
  @apply hover:bg-accent-500 active:transform active:scale-95 border border-border-subtle;
}

.btn-export {
  @apply px-5 py-2.5 rounded-xl bg-bg-input text-white font-semibold text-sm transition-all;
  @apply hover:bg-bg-input-hover active:transform active:scale-95 disabled:opacity-50 border border-border-subtle;
}

.main-footer {
  @apply mt-auto border-t border-border-subtle bg-bg-base/20 backdrop-blur-sm;
}

.copyright {
  @apply text-sm font-semibold text-text-muted;
}