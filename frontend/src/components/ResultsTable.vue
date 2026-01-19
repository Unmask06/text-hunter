<script setup>
/**
 * ResultsTable.vue - Interactive data table for match results
 */
import { ref, computed } from 'vue';

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
  <div class="glass-card overflow-hidden">
    <!-- Header -->
    <div class="p-4 border-b border-white/5 flex items-center justify-between">
      <div>
        <h2 class="text-lg font-semibold text-primary-100">Extraction Results</h2>
        <p v-if="totalCount > 0" class="text-sm mt-1">
          <span class="text-accent-400 font-semibold">{{ totalCount }} total matches found</span>
          <span class="text-primary-500"> · </span>
          <span class="text-primary-400">Showing top {{ Math.min(10, matches.length) }}</span>
        </p>
        <p v-else-if="matches.length > 0" class="text-sm text-primary-400 mt-1">
          {{ matches.length }} matches found
        </p>
      </div>
      
      <div v-if="isLoading" class="flex items-center gap-2 text-primary-400">
        <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="text-sm">Processing...</span>
      </div>
    </div>
    
    <!-- Table -->
    <div class="overflow-x-auto">
      <table v-if="matches.length > 0" class="data-table">
        <thead>
          <tr>
            <th>Source File</th>
            <th>Project ID</th>
            <th>Sheet No</th>
            <th>Page</th>
            <th>Match Found</th>
            <th>Context</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(match, index) in paginatedMatches"
            :key="index"
            class="fade-in"
          >
            <td class="font-medium text-primary-200">{{ match.source_file }}</td>
            <td>{{ match.project_id || '-' }}</td>
            <td>{{ match.sheet_no || '-' }}</td>
            <td class="text-center">{{ match.page }}</td>
            <td>
              <code class="text-accent-400 font-mono text-sm bg-surface-800 px-2 py-1 rounded">
                {{ match.match_found }}
              </code>
            </td>
            <td class="text-primary-400 text-sm max-w-xs truncate" :title="match.context">
              <span v-html="highlightMatch(match.context, match.match_found)"></span>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- Empty State -->
      <div v-else class="p-12 text-center">
        <div class="w-16 h-16 mx-auto rounded-full bg-surface-700 flex items-center justify-center mb-4">
          <svg class="w-8 h-8 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <p class="text-primary-400">No matches found</p>
        <p class="text-primary-500 text-sm mt-1">
          Upload PDFs and run extraction to see results
        </p>
      </div>
    </div>
    
    <!-- Pagination -->
    <div v-if="totalPages > 1" class="p-4 border-t border-white/5 flex items-center justify-between">
      <button
        class="px-3 py-1.5 rounded-lg bg-surface-700 text-primary-300 hover:bg-surface-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        :disabled="currentPage === 1"
        @click="goToPage(currentPage - 1)"
      >
        Previous
      </button>
      
      <div class="flex items-center gap-2">
        <button
          v-for="page in totalPages"
          :key="page"
          :class="[
            'w-8 h-8 rounded-lg transition-colors',
            page === currentPage
              ? 'bg-primary-600 text-white'
              : 'bg-surface-700 text-primary-400 hover:bg-surface-600'
          ]"
          @click="goToPage(page)"
        >
          {{ page }}
        </button>
      </div>
      
      <button
        class="px-3 py-1.5 rounded-lg bg-surface-700 text-primary-300 hover:bg-surface-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        :disabled="currentPage === totalPages"
        @click="goToPage(currentPage + 1)"
      >
        Next
      </button>
    </div>
  </div>
</template>
