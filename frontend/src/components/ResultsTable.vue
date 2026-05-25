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
  <div class="bg-bg-card/80 backdrop-blur-xl border border-border-default rounded-2xl shadow-xl overflow-hidden">
    <!-- Header -->
    <div class="p-space-6 border-b border-border-subtle flex items-center justify-between bg-bg-input/20">
      <div>
        <h2 class="text-lg font-bold text-text-primary">Extraction Results</h2>
        <p v-if="totalCount > 0" class="text-sm mt-space-1">
          <span class="text-cyan-400 font-semibold">{{ totalCount }} total matches found</span>
          <span class="text-text-muted mx-space-1"> · </span>
          <span class="text-text-muted">Showing top {{ Math.min(10, matches.length) }}</span>
        </p>
        <p v-else-if="matches.length > 0" class="text-sm mt-space-1 text-text-muted">
          {{ matches.length }} matches found
        </p>
      </div>

      <div v-if="isLoading" class="flex items-center gap-space-2 text-accent-400 text-sm font-medium">
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
    <div class="overflow-x-auto">
      <div v-if="isLoading" class="py-space-20 text-center">
        <div class="flex flex-col items-center gap-space-4">
          <svg class="w-10 h-10 animate-spin text-accent-500" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
            </path>
          </svg>
          <p class="text-text-secondary font-medium">Loading results...</p>
        </div>
      </div>

      <table v-else-if="matches.length > 0" class="w-full border-collapse">
        <thead>
          <tr>
            <th class="px-space-4 py-space-4 text-left font-bold uppercase text-[10px] tracking-widest text-text-muted border-b border-border-default bg-bg-input/30">Source File</th>
            <th class="px-space-4 py-space-4 text-left font-bold uppercase text-[10px] tracking-widest text-text-muted border-b border-border-default bg-bg-input/30">Project ID</th>
            <th class="px-space-4 py-space-4 text-left font-bold uppercase text-[10px] tracking-widest text-text-muted border-b border-border-default bg-bg-input/30">Sheet No</th>
            <th class="px-space-4 py-space-4 text-center font-bold uppercase text-[10px] tracking-widest text-text-muted border-b border-border-default bg-bg-input/30">Page</th>
            <th class="px-space-4 py-space-4 text-left font-bold uppercase text-[10px] tracking-widest text-text-muted border-b border-border-default bg-bg-input/30">Match Found</th>
            <th class="px-space-4 py-space-4 text-left font-bold uppercase text-[10px] tracking-widest text-text-muted border-b border-border-default bg-bg-input/30">Context</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(match, index) in paginatedMatches" :key="index" class="transition-colors hover:bg-bg-input/40">
            <td class="px-space-4 py-space-4 text-sm border-b border-border-subtle text-text-primary font-medium">{{ match.source_file }}</td>
            <td class="px-space-4 py-space-4 text-sm border-b border-border-subtle text-text-secondary">{{ match.project_id || '-' }}</td>
            <td class="px-space-4 py-space-4 text-sm border-b border-border-subtle text-text-secondary">{{ match.sheet_no || '-' }}</td>
            <td class="px-space-4 py-space-4 text-sm border-b border-border-subtle text-text-secondary text-center">{{ match.page }}</td>
            <td class="px-space-4 py-space-4 text-sm border-b border-border-subtle">
              <code class="font-mono text-xs text-cyan-400 bg-cyan-400/10 px-space-2 py-space-1 rounded border border-cyan-400/20">
                {{ match.match_found }}
              </code>
            </td>
            <td class="px-space-4 py-space-4 text-sm border-b border-border-subtle text-text-secondary max-w-xs truncate" :title="match.context">
              <span v-html="highlightMatch(match.context, match.match_found)"></span>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-else class="py-space-20 text-center">
        <div class="w-20 h-20 mx-auto rounded-3xl bg-bg-input/50 flex items-center justify-center mb-space-6 border border-border-subtle">
          <svg class="w-10 h-10 text-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <p class="text-text-secondary font-semibold text-lg">No matches found</p>
        <p class="text-text-muted text-sm mt-space-2">
          Upload PDFs and run extraction to see results
        </p>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="p-space-4 border-t border-border-subtle flex items-center justify-between bg-bg-input/10">
      <button
        class="px-space-4 py-space-2 rounded-lg bg-bg-input text-text-secondary font-medium text-sm transition-all hover:bg-bg-input-hover hover:text-text-primary disabled:opacity-30 disabled:cursor-not-allowed border border-border-default"
        :disabled="currentPage === 1"
        @click="goToPage(currentPage - 1)"
      >
        Previous
      </button>

      <div class="flex items-center gap-space-2">
        <button
          v-for="page in totalPages"
          :key="page"
          :class="[
            'w-9 h-9 rounded-lg transition-all text-sm font-medium border',
            page === currentPage
              ? 'bg-accent-600 text-white shadow-accent border-white/10'
              : 'text-text-muted border-transparent hover:bg-white/5 hover:text-text-secondary',
          ]"
          @click="goToPage(page)"
        >
          {{ page }}
        </button>
      </div>

      <button
        class="px-space-4 py-space-2 rounded-lg bg-bg-input text-text-secondary font-medium text-sm transition-all hover:bg-bg-input-hover hover:text-text-primary disabled:opacity-30 disabled:cursor-not-allowed border border-border-default"
        :disabled="currentPage === totalPages"
        @click="goToPage(currentPage + 1)"
      >
        Next
      </button>
    </div>
  </div>
</template>

<style scoped>
@reference "@/style.css";

:deep(.match-highlight) {
  @apply px-1 py-0.5 rounded bg-accent-500/20 text-accent-300 font-bold border border-accent-500/20;
}
</style>
