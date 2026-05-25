<script setup>
/**
 * FileUpload.vue - Drag-and-drop PDF upload zone
 */
import { computed, ref } from 'vue';
import { addPdfFile } from '../services/db';

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['file-added', 'file-error']);

// Max file size: 50MB (configurable)
const MAX_FILE_SIZE_MB = 50;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

const isDragOver = ref(false);
const isUploading = ref(false);
const errorMessage = ref('');

const dropZoneClasses = computed(() => [
  'border-2 border-dashed rounded-2xl p-space-8 text-center transition-all duration-base',
  'bg-bg-card/50',
  props.disabled
    ? 'border-border-subtle cursor-not-allowed opacity-50'
    : isDragOver.value
      ? 'border-accent-500 bg-accent-500/5'
      : 'border-border-default hover:border-accent-500/50',
]);

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function handleDragOver(event) {
  if (props.disabled) return;
  event.preventDefault();
  isDragOver.value = true;
}

function handleDragLeave() {
  if (props.disabled) return;
  isDragOver.value = false;
}

async function handleDrop(event) {
  if (props.disabled) return;
  event.preventDefault();
  isDragOver.value = false;

  const files = Array.from(event.dataTransfer.files).filter(
    file => file.type === 'application/pdf'
  );

  await processFiles(files);
}

async function handleFileSelect(event) {
  if (props.disabled) return;
  const files = Array.from(event.target.files);
  await processFiles(files);
  event.target.value = ''; // Reset input
}

async function processFiles(files) {
  if (files.length === 0) return;

  isUploading.value = true;
  errorMessage.value = '';

  const oversizedFiles = [];
  const validFiles = [];

  // Check file sizes
  for (const file of files) {
    if (file.size > MAX_FILE_SIZE_BYTES) {
      oversizedFiles.push(`${file.name} (${formatFileSize(file.size)})`);
    } else {
      validFiles.push(file);
    }
  }

  // Show error for oversized files
  if (oversizedFiles.length > 0) {
    errorMessage.value = `Files exceeding ${MAX_FILE_SIZE_MB}MB limit: ${oversizedFiles.join(', ')}`;
    emit('file-error', errorMessage.value);
  }

  // Process valid files
  for (const file of validFiles) {
    try {
      const id = await addPdfFile(file);
      emit('file-added', { id, name: file.name });
    } catch (error) {
      console.error('Failed to add file:', error);
      errorMessage.value = `Failed to add ${file.name}: ${error.message}`;
    }
  }

  isUploading.value = false;

  // Clear error after 5 seconds
  if (errorMessage.value) {
    setTimeout(() => {
      errorMessage.value = '';
    }, 5000);
  }
}
</script>

<template>
  <div :class="dropZoneClasses" @dragover="handleDragOver" @dragleave="handleDragLeave" @drop="handleDrop">
    <div class="flex flex-col items-center gap-space-3">
      <!-- Upload icon -->
      <div class="w-10 h-10 rounded-full bg-bg-input flex items-center justify-center">
        <svg class="w-5 h-5 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
      </div>

      <div class="text-center">
        <p class="text-text-secondary font-medium text-sm">
          {{ props.disabled ? 'Upload disabled - backend offline' : (isUploading ? 'Uploading...' : 'Drop PDF files here') }}
        </p>
        <p v-if="!props.disabled" class="text-text-muted text-xs mt-space-1">or click to browse</p>
      </div>

      <!-- Error message -->
      <div v-if="errorMessage" class="text-error text-xs bg-error-bg px-space-4 py-space-2 rounded-lg max-w-full">
        {{ errorMessage }}
      </div>

      <label
        :class="[
          'px-space-5 py-space-2 rounded-lg font-semibold text-sm cursor-pointer transition-all active:scale-95',
          props.disabled
            ? 'bg-bg-input text-text-disabled cursor-not-allowed'
            : 'bg-accent-600 text-white hover:bg-accent-500 shadow-accent',
        ]"
      >
        <span>{{ props.disabled ? 'Disabled' : 'Select Files' }}</span>
        <input type="file" accept=".pdf" multiple :disabled="props.disabled" class="hidden"
          @change="handleFileSelect" />
      </label>
    </div>
  </div>
</template>
