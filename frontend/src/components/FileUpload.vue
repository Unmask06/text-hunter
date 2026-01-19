<script setup>
/**
 * FileUpload.vue - Drag-and-drop PDF upload zone
 */
import { ref, computed } from 'vue';
import { addPdfFile, FileStatus } from '../services/db.js';

const emit = defineEmits(['file-added', 'file-error']);

// Max file size: 50MB (configurable)
const MAX_FILE_SIZE_MB = 50;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

const isDragOver = ref(false);
const isUploading = ref(false);
const errorMessage = ref('');

const dropZoneClasses = computed(() => ({
  'drop-zone': true,
  'drag-over': isDragOver.value,
}));

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function handleDragOver(event) {
  event.preventDefault();
  isDragOver.value = true;
}

function handleDragLeave() {
  isDragOver.value = false;
}

async function handleDrop(event) {
  event.preventDefault();
  isDragOver.value = false;
  
  const files = Array.from(event.dataTransfer.files).filter(
    file => file.type === 'application/pdf'
  );
  
  await processFiles(files);
}

async function handleFileSelect(event) {
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
  <div
    :class="dropZoneClasses"
    @dragover="handleDragOver"
    @dragleave="handleDragLeave"
    @drop="handleDrop"
  >
    <div class="flex flex-col items-center gap-4">
      <!-- Upload icon -->
      <div class="w-16 h-16 rounded-full bg-primary-800/50 flex items-center justify-center">
        <svg
          class="w-8 h-8 text-primary-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>
      </div>
      
      <div class="text-center">
        <p class="text-primary-200 font-medium">
          {{ isUploading ? 'Uploading...' : 'Drop PDF files here' }}
        </p>
        <p class="text-primary-400 text-sm mt-1">or click to browse</p>
        <p class="text-primary-500 text-xs mt-2">Max file size: {{ MAX_FILE_SIZE_MB }}MB</p>
      </div>
      
      <!-- Error message -->
      <div
        v-if="errorMessage"
        class="text-error-500 text-sm bg-error-500/10 px-4 py-2 rounded-lg max-w-full"
      >
        {{ errorMessage }}
      </div>
      
      <label class="btn-primary cursor-pointer">
        <span>Select Files</span>
        <input
          type="file"
          accept=".pdf"
          multiple
          class="hidden"
          @change="handleFileSelect"
        />
      </label>
    </div>
  </div>
</template>
