<script setup>
/**
 * App.vue - Main application component
 * TextHunter - Hunt and extract text patterns from PDF documents
 */
import { ref, computed, onMounted, onUnmounted } from 'vue';
import FileUpload from './components/FileUpload.vue';
import FileList from './components/FileList.vue';
import RegexConfig from './components/RegexConfig.vue';
import ResultsTable from './components/ResultsTable.vue';
import { 
  getAllPdfs, 
  deletePdf, 
  updatePdfStatus, 
  storeExtractedText,
  getAllExtractedText,
  getPdfById,
  FileStatus 
} from './services/db.js';
import { extractMatches, extractAllMatches, exportExcel } from './services/api.js';

// State
const files = ref([]);
const matches = ref([]);
const allMatches = ref([]);
const totalCount = ref(0);
const isExtracting = ref(false);
const isExporting = ref(false);
const currentConfig = ref({ keywordRegex: '', fileIdentifierRegex: null });
const backendStatus = ref('checking'); // 'checking', 'online', 'offline'

// Web Worker for PDF processing
let pdfWorker = null;

// Computed
const hasReadyFiles = computed(() => 
  files.value.some(f => f.status === FileStatus.READY)
);

const canExport = computed(() => 
  allMatches.value.length > 0 && !isExporting.value
);

// Initialize
onMounted(async () => {
  // Load existing files from IndexedDB
  await loadFiles();
  
  // Initialize PDF worker
  initPdfWorker();
  
  // Check backend status
  checkBackendStatus();
});

onUnmounted(() => {
  if (pdfWorker) {
    pdfWorker.terminate();
  }
});

async function loadFiles() {
  files.value = await getAllPdfs();
}

function initPdfWorker() {
  pdfWorker = new Worker(
    new URL('./workers/pdf.worker.js', import.meta.url),
    { type: 'module' }
  );
  
  pdfWorker.onmessage = async (event) => {
    const { type, pdfId, pageCount, pages, error } = event.data;
    
    if (type === 'complete') {
      // Store extracted text
      for (const [pageNo, text] of Object.entries(pages)) {
        await storeExtractedText(pdfId, parseInt(pageNo), text);
      }
      
      // Update file status
      await updatePdfStatus(pdfId, FileStatus.READY, { pageCount });
      await loadFiles();
    } else if (type === 'error') {
      console.error('PDF extraction error:', error);
      await updatePdfStatus(pdfId, FileStatus.ERROR);
      await loadFiles();
    }
  };
}

async function checkBackendStatus() {
  try {
    const response = await fetch('/api/health');
    if (response.ok) {
      backendStatus.value = 'online';
    } else {
      backendStatus.value = 'offline';
    }
  } catch {
    backendStatus.value = 'offline';
  }
}

async function handleFileAdded({ id, name }) {
  await loadFiles();
  
  // Start processing
  const pdf = await getPdfById(id);
  if (pdf && pdf.blob) {
    await updatePdfStatus(id, FileStatus.PROCESSING);
    await loadFiles();
    
    pdfWorker.postMessage({
      type: 'extract',
      pdfId: id,
      pdfData: pdf.blob,
    });
  }
}

async function handleDeleteFile(id) {
  await deletePdf(id);
  await loadFiles();
}

async function handleExtract(config) {
  if (!hasReadyFiles.value) return;
  
  isExtracting.value = true;
  matches.value = [];
  allMatches.value = [];
  totalCount.value = 0;
  currentConfig.value = config;
  
  try {
    // Get all extracted text from ready PDFs
    const textContent = await getAllExtractedText();
    
    if (Object.keys(textContent).length === 0) {
      console.warn('No text content available');
      return;
    }
    
    // Call backend for preview
    const payload = {
      filenames: Object.keys(textContent),
      keyword_regex: config.keywordRegex,
      file_identifier_regex: config.fileIdentifierRegex,
      text_content: textContent,
    };
    
    const result = await extractMatches(payload);
    matches.value = result.matches;
    totalCount.value = result.total_count;
    
    // Fetch all matches for export
    if (result.total_count > 10) {
      const allResult = await extractAllMatches(payload);
      allMatches.value = allResult.matches;
    } else {
      allMatches.value = result.matches;
    }
  } catch (error) {
    console.error('Extraction error:', error);
    alert('Extraction failed: ' + (error.response?.data?.detail || error.message));
  } finally {
    isExtracting.value = false;
  }
}

async function handleExport() {
  if (!canExport.value) return;
  
  isExporting.value = true;
  
  try {
    await exportExcel(allMatches.value, true);
  } catch (error) {
    console.error('Export error:', error);
    alert('Export failed: ' + error.message);
  } finally {
    isExporting.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <!-- Header -->
    <header class="glass-card m-4 mb-0 p-4 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <!-- Logo -->
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-500 to-primary-600 flex items-center justify-center">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <div>
          <h1 class="text-xl font-bold text-primary-100">TextHunter</h1>
          <p class="text-sm text-primary-400">Hunt and extract text patterns from PDFs</p>
        </div>
      </div>
      
      <!-- Backend Status -->
      <div class="flex items-center gap-2">
        <span
          :class="[
            'w-2 h-2 rounded-full',
            backendStatus === 'online' ? 'bg-success-500' : 
            backendStatus === 'offline' ? 'bg-error-500' : 'bg-warning-500 animate-pulse'
          ]"
        ></span>
        <span class="text-sm text-primary-400">
          {{ backendStatus === 'online' ? 'Backend Online' : 
             backendStatus === 'offline' ? 'Backend Offline' : 'Checking...' }}
        </span>
      </div>
    </header>
    
    <!-- Main Content -->
    <div class="flex-1 flex gap-4 p-4">
      <!-- Left Sidebar -->
      <aside class="w-80 shrink-0 flex flex-col gap-4">
        <FileUpload @file-added="handleFileAdded" />
        <div class="glass-card p-4 flex-1 overflow-y-auto">
          <FileList :files="files" @delete-file="handleDeleteFile" />
        </div>
      </aside>
      
      <!-- Main Workspace -->
      <main class="flex-1 flex flex-col gap-4">
        <!-- Config Panel -->
        <RegexConfig 
          :disabled="!hasReadyFiles || isExtracting || backendStatus !== 'online'"
          @extract="handleExtract"
          @update:config="config => currentConfig = config"
        />
        
        <!-- Results Table -->
        <div class="flex-1">
          <ResultsTable 
            :matches="matches"
            :total-count="totalCount"
            :is-loading="isExtracting"
          />
        </div>
      </main>
    </div>
    
    <!-- Footer / Export Bar -->
    <footer class="glass-card m-4 mt-0 p-4 flex items-center justify-between">
      <div class="text-sm text-primary-400">
        <span v-if="allMatches.length > 0">
          {{ allMatches.length }} matches ready for export
        </span>
        <span v-else>
          Configure regex and extract to see results
        </span>
      </div>
      
      <button
        class="btn-accent flex items-center gap-2"
        :disabled="!canExport"
        @click="handleExport"
      >
        <svg v-if="isExporting" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        {{ isExporting ? 'Exporting...' : 'Export to Excel' }}
      </button>
    </footer>
  </div>
</template>
