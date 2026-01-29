<script setup>
/**
 * ResultsTable.vue - Interactive data table for match results
 */
import { computed, ref } from 'vue';

const props = defineProps({
  matches: {
    type: Array,
    required: true,
  },
  totalCount: {
    type: Number,
    default: 0,
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
});

// Pagination
const currentPage = ref(1);
const pageSize = ref(10);

const totalPages = computed(() =>
  Math.ceil(props.matches.length / pageSize.value)
);

const paginatedMatches = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return props.matches.slice(start, start + pageSize.value);
});

function goToPage(page) {
  currentPage.value = Math.max(1, Math.min(page, totalPages.value));
}

// Highlight the match within context
function highlightMatch(context, match) {
  if (!context || !match) return context;
  const escaped = match.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return context.replace(
    new RegExp(`(${escaped})`, 'gi'),
    '<span class="match-highlight">$1</span>'
  );
}
</script>

<template>
  <div class="results-container">
    <!-- Header -->
    <div class="header-section">
      <div>
        <h2 class="results-title">Extraction Results</h2>
        <p v-if="totalCount > 0" class="results-subtitle">
          <span class="count-accent">{{ totalCount }} total matches found</span>
          <span class="divider"> · </span>
          <span class="view-info">Showing top {{ Math.min(10, matches.length) }}</span>
        </p>
        <p v-else-if="matches.length > 0" class="results-subtitle">
          {{ matches.length }} matches found
        </p>
      </div>

      <div v-if="isLoading" class="loading-spinner">
        <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
          </path>
        </svg>
        <span>Processing...</span>
      </div>
    </div>

    <!-- Table Content -->
    <div class="table-wrapper">
      <div v-if="isLoading" class="table-loader">
        <div class="flex flex-col items-center gap-4">
          <svg class="w-10 h-10 animate-spin text-indigo-500" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
            </path>
          </svg>
          <p class="text-slate-400 font-medium">Loading results...</p>
        </div>
      </div>

      <table v-else-if="matches.length > 0" class="results-table">
        <thead>
          <tr>
            <th>Source File</th>
            <th>Project ID</th>
            <th>Sheet No</th>
            <th class="text-center">Page</th>
            <th>Match Found</th>
            <th>Context</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(match, index) in paginatedMatches" :key="index" class="table-row">
            <td class="font-medium text-slate-100">{{ match.source_file }}</td>
            <td>{{ match.project_id || '-' }}</td>
            <td>{{ match.sheet_no || '-' }}</td>
            <td class="text-center">{{ match.page }}</td>
            <td>
              <code class="match-pill">
                {{ match.match_found }}
              </code>
            </td>
            <td class="max-w-xs truncate" :title="match.context">
              <span v-html="highlightMatch(match.context, match.match_found)"></span>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-else class="empty-results">
        <div class="empty-icon-wrapper">
          <svg class="w-10 h-10 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <p class="empty-text">No matches found</p>
        <p class="empty-hint">
          Upload PDFs and run extraction to see results
        </p>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination-footer">
      <button class="nav-btn" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">
        Previous
      </button>

      <div class="page-indicators">
        <button v-for="page in totalPages" :key="page" :class="['page-btn', page === currentPage ? 'active' : '']"
          @click="goToPage(page)">
          {{ page }}
        </button>
      </div>

      <button class="nav-btn" :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">
        Next
      </button>
    </div>
  </div>
</template>

<style scoped>
@reference "@/style.css";

.results-container {
  @apply bg-slate-900/80 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden;
}

.header-section {
  @apply p-5 border-b border-white/5 flex items-center justify-between bg-slate-800/20;
}

.results-title {
  @apply text-lg font-bold text-slate-100;
}

.results-subtitle {
  @apply text-sm mt-1;
}

.count-accent {
  @apply text-cyan-400 font-semibold;
}

.divider {
  @apply text-slate-700 mx-1;
}

.view-info {
  @apply text-slate-500;
}

.loading-spinner {
  @apply flex items-center gap-2 text-indigo-400 text-sm font-medium;
}

.table-wrapper {
  @apply overflow-x-auto;
}

.table-loader {
  @apply py-20 text-center;
}

.results-table {
  @apply w-full border-collapse;
}

.results-table th {
  @apply px-4 py-4 text-left font-bold uppercase text-[10px] tracking-widest text-slate-500 border-b border-white/10 bg-slate-800/30;
}

.table-row {
  @apply transition-colors hover:bg-slate-800/40;
}

.table-row td {
  @apply px-4 py-4 text-sm border-b border-white/5 text-slate-400;
}

.match-pill {
  @apply font-mono text-xs text-cyan-400 bg-cyan-500/10 px-2 py-1 rounded border border-cyan-500/20;
}

:deep(.match-highlight) {
  @apply px-1 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-bold border border-indigo-500/20;
}

.empty-results {
  @apply py-20 text-center;
}

.empty-icon-wrapper {
  @apply w-20 h-20 mx-auto rounded-3xl bg-slate-800/50 flex items-center justify-center mb-6 border border-white/5;
}

.empty-text {
  @apply text-slate-300 font-semibold text-lg;
}

.empty-hint {
  @apply text-slate-500 text-sm mt-2;
}

.pagination-footer {
  @apply p-4 border-t border-white/5 flex items-center justify-between bg-slate-800/10;
}

.nav-btn {
  @apply px-4 py-2 rounded-lg bg-slate-800 text-slate-300 font-medium text-sm transition-all;
  @apply hover:bg-slate-700 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed border border-white/5;
}

.page-indicators {
  @apply flex items-center gap-2;
}

.page-btn {
  @apply w-9 h-9 rounded-lg transition-all text-sm font-medium text-slate-400 border border-transparent;
  @apply hover:bg-white/5 hover:text-slate-200;
}

.page-btn.active {
  @apply bg-indigo-600 text-white shadow-lg shadow-indigo-500/20 border-white/10;
}
</style>
