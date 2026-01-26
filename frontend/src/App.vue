<script setup>
/**
 * App.vue - Main application component
 * TextHunter - Hunt and extract text patterns from PDF documents
 */
import { computed, onMounted, onUnmounted, ref } from "vue";
import FileList from "./components/FileList.vue";
import FileUpload from "./components/FileUpload.vue";
import RegexConfig from "./components/RegexConfig.vue";
import ResultsTable from "./components/ResultsTable.vue";
import {
  checkHealth,
  exportExcel,
  extractAllMatches,
  extractMatches,
} from "./services/api.js";
import {
  deletePdf,
  FileStatus,
  getAllExtractedText,
  getAllPdfs,
  getPdfById,
  storeExtractedText,
  updatePdfStatus,
} from "./services/db.js";

// State
const files = ref([]);
const matches = ref([]);
const allMatches = ref([]);
const totalCount = ref(0);
const isExtracting = ref(false);
const isExporting = ref(false);
const currentConfig = ref({ keywordRegex: "", fileIdentifierRegex: null });
const backendStatus = ref("checking"); // 'checking', 'online', 'offline'
const isLoadingFiles = ref(false);

// Web Worker for PDF processing
let pdfWorker = null;

// Computed
const hasReadyFiles = computed(() =>
  files.value.some((f) => f.status === FileStatus.READY),
);

const canExport = computed(
  () => allMatches.value.length > 0 && !isExporting.value,
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
  isLoadingFiles.value = true;
  try {
    files.value = await getAllPdfs();
  } finally {
    isLoadingFiles.value = false;
  }
}

function initPdfWorker() {
  pdfWorker = new Worker(new URL("./workers/pdf.worker.js", import.meta.url), {
    type: "module",
  });

  pdfWorker.onmessage = async (event) => {
    const { type, pdfId, pageCount, pages, error } = event.data;

    if (type === "complete") {
      // Store extracted text
      for (const [pageNo, text] of Object.entries(pages)) {
        await storeExtractedText(pdfId, parseInt(pageNo), text);
      }

      // Update file status
      await updatePdfStatus(pdfId, FileStatus.READY, { pageCount });
      await loadFiles();
    } else if (type === "error") {
      console.error("PDF extraction error:", error);
      await updatePdfStatus(pdfId, FileStatus.ERROR);
      await loadFiles();
    }
  };
}

async function checkBackendStatus() {
  try {
    await checkHealth();
    backendStatus.value = "online";
  } catch {
    backendStatus.value = "offline";
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
      type: "extract",
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
      console.warn("No text content available");
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
    console.error("Extraction error:", error);
    alert(
      "Extraction failed: " + (error.response?.data?.detail || error.message),
    );
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
    console.error("Export error:", error);
    alert("Export failed: " + error.message);
  } finally {
    isExporting.value = false;
  }
}
</script>

<template>
  <div class="app-layout">
    <!-- Header -->
    <header class="main-header">
      <div class="container mx-auto flex items-center justify-between px-6">
        <div class="flex items-center gap-4">
          <div class="logo-container">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <div>
            <h1 class="app-title">TextHunter</h1>
            <div class="status-indicator">
              <div :class="['status-dot', backendStatus === 'online' ? 'status-online' : 'status-offline']"></div>
              <span class="text-[10px] font-bold uppercase tracking-widest">
                {{ backendStatus === 'online' ? 'API Online' : 'API Offline' }}
              </span>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-4">
          <button v-if="allMatches.length > 0" class="btn-export" :disabled="isExporting" @click="handleExport">
            <span class="flex items-center gap-2">
              <svg v-if="isExporting" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                </path>
              </svg>
              <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              {{ isExporting ? 'Exporting...' : 'Export to Excel' }}
            </span>
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto flex-1 grid grid-cols-1 lg:grid-cols-12 gap-8 px-6 py-8">
      <!-- Left Column: Controls -->
      <aside class="lg:col-span-3 space-y-6">
        <section>
          <FileUpload :disabled="backendStatus === 'offline'" @file-added="handleFileAdded" />
        </section>

        <section>
          <FileList :files="files" :is-loading="isLoadingFiles" @delete-file="handleDeleteFile" />
        </section>
      </aside>

      <!-- Right Column: Results -->
      <section class="lg:col-span-8 space-y-8">
        <section>
          <RegexConfig :disabled="!hasReadyFiles" @extract="handleExtract" />
        </section>
        <ResultsTable :matches="matches" :total-count="totalCount" :is-loading="isExtracting" />
      </section>
    </main>

    <!-- Footer -->
    <footer class="main-footer">
      <div class="container mx-auto px-6 py-8 flex flex-col md:flex-row items-center justify-between gap-6">
        <div class="flex flex-col gap-2">
          <p class="copyright">
            &copy; {{ new Date().getFullYear() }} TextHunter. All rights reserved.
          </p>
          <p class="text-xs text-slate-600">Built for high-performance PDF data extraction</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
@reference "@/style.css";

.app-layout {
  @apply min-h-screen flex flex-col bg-slate-950 text-slate-400 font-sans selection:bg-indigo-500/30;
}

.main-header {
  @apply py-4 border-b border-white/5 bg-slate-900/40 backdrop-blur-md sticky top-0 z-50;
}

.logo-container {
  @apply w-12 h-12 rounded-2xl bg-linear-to-br from-indigo-500 to-cyan-500 shadow-lg shadow-indigo-500/20 flex items-center justify-center;
}

.app-title {
  @apply text-2xl font-black text-white tracking-tight leading-none;
}

.status-indicator {
  @apply flex items-center gap-2 mt-1;
}

.status-dot {
  @apply w-2 h-2 rounded-full;
}

.status-online {
  @apply bg-emerald-500;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
}

.status-offline {
  @apply bg-red-500;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
}

.btn-export {
  @apply px-5 py-2.5 rounded-xl bg-slate-800 text-white font-semibold text-sm transition-all;
  @apply hover:bg-slate-700 active:transform active:scale-95 disabled:opacity-50 border border-white/5;
}

.main-footer {
  @apply mt-auto border-t border-white/5 bg-slate-900/20 backdrop-blur-sm;
}

.copyright {
  @apply text-sm font-semibold text-slate-500;
}
</style>
