<script setup lang="ts">
/**
 * App.vue - Main application component
 * PDFHunter - Extract text patterns and detect P&ID symbols from PDF documents
 */
import { computed, onMounted, onUnmounted, ref } from "vue";
import FileList from "./components/FileList.vue";
import FileUpload from "./components/FileUpload.vue";
import LicenseCheck from "./components/LicenseCheck.vue";
import RegexConfig from "./components/RegexConfig.vue";
import ResultsTable from "./components/ResultsTable.vue";
import SymbolDetector from "./components/SymbolDetector.vue";
import type { MatchResult } from "./client/types.gen";
import {
  exportExcel,
  extractAllMatches,
  extractMatches,
} from "./services/api.ts";
import {
  deletePdf,
  FileStatus,
  getAllExtractedText,
  getAllPdfs,
  getPdfById,
  type PdfRecord,
  storeExtractedText,
  updatePdfStatus,
} from "./services/db.ts";

// Active tab: 'text' | 'vision'
const activeTab = ref("text");
// MatchResult type is imported from client/types.gen above

// State
const files = ref<PdfRecord[]>([]);
const matches = ref<MatchResult[]>([]);
const allMatches = ref<MatchResult[]>([]);
const totalCount = ref(0);
const isExtracting = ref(false);
const isExporting = ref(false);
const currentConfig = ref({ keywordRegex: "", fileIdentifierRegex: null as string | null });
const isLoadingFiles = ref(false);
const backendStatus = ref<"online" | "offline">("offline");

// Web Worker for PDF processing
let pdfWorker: Worker | null = null;

// Computed
const hasReadyFiles = computed(() =>
  files.value.some((f) => f.status === FileStatus.READY),
);

const canExport = computed(
  () => allMatches.value.length > 0 && !isExporting.value,
);

// Initialize
onMounted(async () => {
  await loadFiles();
  initPdfWorker();
  // Backend status check deferred until after license validation
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

  pdfWorker.onmessage = async (event: MessageEvent) => {
    const { type, pdfId, pageCount, pages, error } = event.data as {
      type: string;
      pdfId: number;
      pageCount: number;
      pages: Record<string, string>;
      error: string;
    };

    if (type === "complete") {
      for (const [pageNo, text] of Object.entries(pages)) {
        await storeExtractedText(pdfId, parseInt(pageNo), text);
      }
      await updatePdfStatus(pdfId, FileStatus.READY, { pageCount });
      await loadFiles();
    } else if (type === "error") {
      console.error("PDF extraction error:", error);
      await updatePdfStatus(pdfId, FileStatus.ERROR);
      await loadFiles();
    }
  };
}

async function handleFileAdded({ id, name }: { id: number; name: string }) {
  await loadFiles();
  const pdf = await getPdfById(id);
  if (pdf && pdf.blob) {
    await updatePdfStatus(id, FileStatus.PROCESSING);
    await loadFiles();
    pdfWorker!.postMessage({
      type: "extract",
      pdfId: id,
      pdfData: pdf.blob,
    });
  }
}

async function handleDeleteFile(id: number) {
  await deletePdf(id);
  await loadFiles();
}

async function handleExtract(config: { keywordRegex: string; fileIdentifierRegex: string | null }) {
  if (!hasReadyFiles.value) return;

  isExtracting.value = true;
  matches.value = [];
  allMatches.value = [];
  totalCount.value = 0;
  currentConfig.value = config;

  try {
    const textContent = await getAllExtractedText();
    if (Object.keys(textContent).length === 0) {
      console.warn("No text content available");
      return;
    }

    const payload = {
      filenames: Object.keys(textContent),
      keyword_regex: config.keywordRegex,
      file_identifier_regex: config.fileIdentifierRegex,
      text_content: textContent,
    };

    const result = await extractMatches(payload);
    matches.value = result.matches;
    totalCount.value = result.total_count;

    if (result.total_count > 10) {
      const allResult = await extractAllMatches(payload);
      allMatches.value = allResult.matches;
    } else {
      allMatches.value = result.matches;
    }
  } catch (e) {
    console.error("Extraction error:", e);
    alert("Extraction failed: " + (e instanceof Error ? e.message : String(e)));
  } finally {
    isExtracting.value = false;
  }
}

async function handleExport() {
  if (!canExport.value) return;
  isExporting.value = true;

  try {
    await exportExcel(allMatches.value, true);
  } catch (e) {
    console.error("Export error:", e);
    alert("Export failed: " + (e instanceof Error ? e.message : String(e)));
  } finally {
    isExporting.value = false;
  }
}

/**
 * Open the exported Excel file with default application.
 * Only available on desktop.
 */
async function handleOpenFile() {
  // Web mode: file is downloaded automatically, no file path to open
  console.log("File downloaded successfully");
}

function handleLicenseResult(valid: boolean) {
  if (!valid) {
    console.error("License validation failed - app functionality may be limited");
  } else {
    checkBackendStatusWithRetry();
  }
}

async function checkBackendStatusWithRetry() {
  const { checkHealth } = await import("./services/api.ts");
  const maxRetries = 8;
  const retryDelay = 500;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const result = await checkHealth();
      console.log("Backend health:", result);
      backendStatus.value = "online";
      return;
    } catch (error: any) {
      console.log(`Backend check attempt ${attempt}/${maxRetries} failed:`, error?.message);
      if (attempt >= maxRetries) {
        console.error("Backend offline after all retries:", error?.response?.status, error?.code);
        backendStatus.value = "offline";
      } else {
        await new Promise(resolve => setTimeout(resolve, retryDelay));
      }
    }
  }
}
</script>

<template>
  <LicenseCheck @validated="handleLicenseResult">
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
              <h1 class="app-title">PDFHunter</h1>
              <div class="status-indicator">
                <div :class="['status-dot', backendStatus === 'online' ? 'status-online' : 'status-offline']" :title="backendStatus === 'online' ? 'API Online' : 'API Offline'"></div>
              </div>
            </div>          </div>

          <div class="flex items-center gap-4">
            <a href="/docs/" target="_blank" class="btn-docs" title="Open Documentation">
              <span class="flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                Docs
              </span>
            </a>
            <!-- Export button (text tab only) -->
            <button
              v-if="activeTab === 'text' && allMatches.length > 0"
              class="btn-export"
              :disabled="isExporting"
              @click="handleExport"
            >
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

      <!-- Tab navigation -->
      <nav class="tab-nav">
        <div class="container mx-auto px-6 flex gap-1">
          <button
            :class="['tab-btn', activeTab === 'text' ? 'tab-active' : 'tab-inactive']"
            @click="activeTab = 'text'"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Text Extraction
          </button>
          <button
            :class="['tab-btn', activeTab === 'vision' ? 'tab-active' : 'tab-inactive']"
            @click="activeTab = 'vision'"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            Symbol Detection
            <span class="tab-badge">NEW</span>
          </button>
        </div>
      </nav>

      <!-- Main Content -->
      <main class="container mx-auto flex-1 px-6 py-8">
        <!-- Text Extraction Tab -->
        <div v-show="activeTab === 'text'" class="grid grid-cols-1 lg:grid-cols-12 gap-8">
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
          <section class="lg:col-span-9 space-y-8">
            <RegexConfig :disabled="!hasReadyFiles" @extract="handleExtract" />
            <ResultsTable :matches="matches" :total-count="totalCount" :is-loading="isExtracting" />
          </section>
        </div>

        <!-- Symbol Detection Tab -->
        <div v-show="activeTab === 'vision'">
          <SymbolDetector />
        </div>

      </main>

      <!-- Footer -->
      <footer class="main-footer">
        <div class="container mx-auto px-6 py-8 flex flex-col md:flex-row items-center justify-between gap-6">
          <div class="flex flex-col gap-2">
            <p class="copyright">&copy; {{ new Date().getFullYear() }} PDFHunter. All rights reserved.</p>
            <p class="text-xs text-text-muted">Text extraction · P&ID symbol detection · Oil & Gas</p>
          </div>
        </div>
      </footer>

    </div>
  </LicenseCheck>
</template>

<style scoped>
@reference "@/style.css";

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
</style>
