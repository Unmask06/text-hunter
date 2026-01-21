<script setup>
/**
 * FileList.vue - List of uploaded PDF files with status indicators
 */
import { computed } from 'vue';

const props = defineProps({
  files: {
    type: Array,
    required: true,
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['delete-file']);

function getStatusBadgeClass(status) {
  return {
    badge: true,
    'badge-pending': status === 'pending',
    'badge-processing': status === 'processing',
    'badge-ready': status === 'ready',
    'badge-error': status === 'error',
  };
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function handleDelete(file) {
  emit('delete-file', file.id);
}
</script>

<template>
  <div class="space-y-2">
    <div class="flex items-center justify-between mb-3">
      <h3 class="text-sm font-semibold text-primary-300 uppercase tracking-wide">
        Files ({{ files.length }})
      </h3>
      <div v-if="isLoading" class="flex items-center gap-2 text-primary-400 text-xs">
        <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span>Loading...</span>
      </div>
    </div>
    
    <div
      v-if="isLoading && files.length === 0"
      class="flex items-center gap-2 text-primary-500 text-sm italic"
    >
      <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      Loading files...
    </div>
    
    <div v-else-if="files.length === 0" class="text-primary-500 text-sm italic">
      No files uploaded yet
    </div>
    
    <TransitionGroup name="list" tag="div" class="space-y-2">
      <div
        v-for="file in files"
        :key="file.id"
        class="glass-card p-3 flex items-center gap-3 fade-in"
      >
        <!-- PDF Icon -->
        <div class="w-10 h-10 rounded-lg bg-error-500/20 flex items-center justify-center shrink-0">
          <svg class="w-5 h-5 text-error-500" fill="currentColor" viewBox="0 0 20 20">
            <path
              fill-rule="evenodd"
              d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"
              clip-rule="evenodd"
            />
          </svg>
        </div>
        
        <!-- File Info -->
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-primary-100 truncate">
            {{ file.name }}
          </p>
          <div class="flex items-center gap-2 mt-1">
            <span class="text-xs text-primary-400">
              {{ formatFileSize(file.size) }}
            </span>
            <span v-if="file.pageCount" class="text-xs text-primary-400">
              · {{ file.pageCount }} pages
            </span>
          </div>
        </div>
        
        <!-- Status Badge -->
        <div :class="getStatusBadgeClass(file.status)">
          {{ file.status }}
        </div>
        
        <!-- Delete Button -->
        <button
          class="p-1.5 rounded-lg hover:bg-error-500/20 text-primary-400 hover:text-error-500 transition-colors"
          @click="handleDelete(file)"
          title="Delete file"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>
