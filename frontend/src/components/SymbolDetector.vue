<script setup lang="ts">
/**
 * SymbolDetector.vue — 4-step P&ID symbol detection workflow
 *
 * Step 1: Upload legend P&ID → annotate symbols on canvas
 * Step 2: Upload target P&ID(s)
 * Step 3: Run detection
 * Step 4: View annotated results + export to Excel
 */
import { computed, nextTick, onUnmounted, ref } from "vue";
import type {
  BoundingBox,
  SymbolDetectionResult,
  SymbolDetectResponse,
  SymbolTemplate,
} from "@/client/types.gen";
import {
  detectSymbols,
  exportVisionResults,
  extractLegendTemplates,
  renderPdfPage,
} from "@/services/api.ts";

// ---------------------------------------------------------------------------
// Step 1 — Legend upload & annotation
// ---------------------------------------------------------------------------
const legendPdfB64 = ref<string | null>(null);
const legendImageB64 = ref<string | null>(null);
const legendTotalPages = ref(1);
const legendCurrentPage = ref(1);
const legendWidth = ref(0);
const legendHeight = ref(0);
const isRenderingLegend = ref(false);

const canvasRef = ref<HTMLCanvasElement | null>(null);
const drawnBoxes = ref<BoundingBox[]>([]);
const symbolNames = ref<string[]>([]);
const extractedTemplates = ref<SymbolTemplate[]>([]);
const annotatedLegendB64 = ref<string | null>(null);
const isExtractingTemplates = ref(false);

// Canvas drawing state
let isDrawing = false;
let startX = 0;
let startY = 0;

async function onLegendFileChange(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) return;
  legendPdfB64.value = await fileToBase64(file);
  legendCurrentPage.value = 1;
  drawnBoxes.value = [];
  symbolNames.value = [];
  extractedTemplates.value = [];
  annotatedLegendB64.value = null;
  await renderLegendPage();
}

async function renderLegendPage() {
  if (!legendPdfB64.value) return;
  isRenderingLegend.value = true;
  try {
    const res = await renderPdfPage(legendPdfB64.value, legendCurrentPage.value, 150);
    legendImageB64.value = res.image_b64;
    legendWidth.value = res.width;
    legendHeight.value = res.height;
    legendTotalPages.value = res.total_pages;
    await nextTick();
    drawCanvas();
  } finally {
    isRenderingLegend.value = false;
  }
}

async function prevLegendPage() {
  if (legendCurrentPage.value > 1) {
    legendCurrentPage.value--;
    await renderLegendPage();
  }
}

async function nextLegendPage() {
  if (legendCurrentPage.value < legendTotalPages.value) {
    legendCurrentPage.value++;
    await renderLegendPage();
  }
}

// Canvas annotation helpers
function getCanvasCoords(e: MouseEvent): { x: number; y: number } {
  const canvas = canvasRef.value!;
  const rect = canvas.getBoundingClientRect();
  const scaleX = legendWidth.value / rect.width;
  const scaleY = legendHeight.value / rect.height;
  return {
    x: Math.round((e.clientX - rect.left) * scaleX),
    y: Math.round((e.clientY - rect.top) * scaleY),
  };
}

function onMouseDown(e: MouseEvent) {
  const { x, y } = getCanvasCoords(e);
  startX = x;
  startY = y;
  isDrawing = true;
}

function onMouseMove(e: MouseEvent) {
  if (!isDrawing) return;
  const { x, y } = getCanvasCoords(e);
  drawCanvas({ x: startX, y: startY, width: x - startX, height: y - startY });
}

function onMouseUp(e: MouseEvent) {
  if (!isDrawing) return;
  isDrawing = false;
  const { x, y } = getCanvasCoords(e);
  const w = x - startX;
  const h = y - startY;
  if (Math.abs(w) > 5 && Math.abs(h) > 5) {
    drawnBoxes.value.push({
      x: w > 0 ? startX : x,
      y: h > 0 ? startY : y,
      width: Math.abs(w),
      height: Math.abs(h),
    });
    symbolNames.value.push(`Symbol ${drawnBoxes.value.length}`);
  }
  drawCanvas();
}

function drawCanvas(previewBox?: BoundingBox) {
  const canvas = canvasRef.value;
  if (!canvas || !legendImageB64.value) return;
  const ctx = canvas.getContext("2d")!;
  canvas.width = legendWidth.value;
  canvas.height = legendHeight.value;

  const img = new Image();
  img.src = `data:image/png;base64,${legendImageB64.value}`;
  img.onload = () => {
    ctx.drawImage(img, 0, 0);
    ctx.lineWidth = 3;
    // Draw saved boxes
    drawnBoxes.value.forEach((b, i) => {
      ctx.strokeStyle = "#22c55e";
      ctx.strokeRect(b.x, b.y, b.width, b.height);
      ctx.fillStyle = "#22c55e";
      ctx.font = "14px sans-serif";
      ctx.fillText(symbolNames.value[i] || `Symbol ${i + 1}`, b.x + 2, b.y - 4);
    });
    // Draw in-progress preview box
    if (previewBox) {
      ctx.strokeStyle = "#f59e0b";
      ctx.setLineDash([6, 3]);
      ctx.strokeRect(previewBox.x, previewBox.y, previewBox.width, previewBox.height);
      ctx.setLineDash([]);
    }
  };
}

function removeBox(index: number) {
  drawnBoxes.value.splice(index, 1);
  symbolNames.value.splice(index, 1);
  drawCanvas();
}

async function extractTemplates(autoMode: boolean) {
  if (!legendImageB64.value) return;
  isExtractingTemplates.value = true;
  try {
    const payload = autoMode
      ? { image_b64: legendImageB64.value }
      : {
          image_b64: legendImageB64.value,
          bounding_boxes: drawnBoxes.value,
          symbol_names: symbolNames.value,
        };
    const res = await extractLegendTemplates(payload);
    extractedTemplates.value = res.templates;
    annotatedLegendB64.value = res.annotated_image_b64;
    if (autoMode) {
      // Populate names from auto-segmented templates
      symbolNames.value = res.templates.map((t) => t.name);
    }
  } finally {
    isExtractingTemplates.value = false;
  }
}

// ---------------------------------------------------------------------------
// Step 2 — Target P&ID upload
// ---------------------------------------------------------------------------
const targetPdfB64 = ref<string | null>(null);
const targetPdfName = ref("");

async function onTargetFileChange(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) return;
  targetPdfName.value = file.name;
  targetPdfB64.value = await fileToBase64(file);
}

// ---------------------------------------------------------------------------
// Step 3 — Detection config & run
// ---------------------------------------------------------------------------
const threshold = ref(0.75);
const dpi = ref(150);
const enableRotation = ref(false);
const isDetecting = ref(false);
const detectError = ref<string | null>(null);

const canRunDetection = computed(
  () =>
    !!targetPdfB64.value &&
    extractedTemplates.value.length > 0 &&
    !isDetecting.value,
);

async function runDetection() {
  if (!canRunDetection.value || !targetPdfB64.value) return;
  isDetecting.value = true;
  detectError.value = null;
  detectionResults.value = [];
  annotatedPages.value = [];
  currentPage.value = 0;

  try {
    const res: SymbolDetectResponse = await detectSymbols({
      pdf_b64: targetPdfB64.value,
      templates: extractedTemplates.value,
      dpi: dpi.value,
      threshold: threshold.value,
      enable_rotation: enableRotation.value,
    });
    detectionResults.value = res.results;
    annotatedPages.value = res.annotated_pages_b64 ?? [];
  } catch (e: unknown) {
    detectError.value = e instanceof Error ? e.message : "Detection failed";
  } finally {
    isDetecting.value = false;
  }
}

// ---------------------------------------------------------------------------
// Step 4 — Results
// ---------------------------------------------------------------------------
const detectionResults = ref<SymbolDetectionResult[]>([]);
const annotatedPages = ref<string[]>([]);
const currentPage = ref(0);
const isExporting = ref(false);

async function handleExport() {
  if (!detectionResults.value.length) return;
  isExporting.value = true;
  try {
    await exportVisionResults(detectionResults.value);
  } finally {
    isExporting.value = false;
  }
}

// ---------------------------------------------------------------------------
// Utility
// ---------------------------------------------------------------------------
function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string | null;
      if (!result) {
        reject(new Error("FileReader result is null"));
        return;
      }
      resolve(result.includes(",") ? (result.split(",")[1] || result) : result);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

onUnmounted(() => {
  // nothing to clean up currently
});
</script>

<template>
  <div class="sd-layout space-y-8">

    <!-- Step 1: Legend Upload & Annotation -->
    <section class="sd-card">
      <div class="sd-card-header">
        <span class="sd-step-badge">1</span>
        <h2 class="sd-section-title">Upload Legend P&amp;ID</h2>
        <p class="sd-section-sub">Upload your legend sheet and draw boxes around each symbol, or use Auto-Detect.</p>
      </div>

      <div class="sd-card-body space-y-4">
        <!-- File input -->
        <label class="sd-file-label">
          <input type="file" accept=".pdf" class="hidden" @change="onLegendFileChange" />
          <span class="sd-file-btn">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            Choose Legend PDF
          </span>
        </label>

        <!-- Legend canvas -->
        <div v-if="legendImageB64" class="space-y-3">
          <!-- Page navigation -->
          <div v-if="legendTotalPages > 1" class="flex items-center gap-3 text-sm text-text-tertiary">
            <button class="sd-nav-btn" :disabled="legendCurrentPage === 1" @click="prevLegendPage">‹ Prev</button>
            <span>Page {{ legendCurrentPage }} / {{ legendTotalPages }}</span>
            <button class="sd-nav-btn" :disabled="legendCurrentPage === legendTotalPages" @click="nextLegendPage">Next ›</button>
          </div>

          <p class="text-xs text-text-muted">Draw rectangles around symbols on the canvas below.</p>

          <div class="sd-canvas-wrap" :style="{ aspectRatio: `${legendWidth} / ${legendHeight}` }">
            <canvas
              ref="canvasRef"
              class="sd-canvas"
              @mousedown="onMouseDown"
              @mousemove="onMouseMove"
              @mouseup="onMouseUp"
            />
            <div v-if="isRenderingLegend" class="sd-canvas-overlay">
              <svg class="w-6 h-6 animate-spin text-accent-400" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            </div>
          </div>

          <!-- Drawn boxes list -->
          <div v-if="drawnBoxes.length > 0" class="space-y-2">
            <p class="text-xs font-semibold text-text-tertiary uppercase tracking-wider">Annotated Symbols</p>
            <div v-for="(box, i) in drawnBoxes" :key="i" class="flex items-center gap-2">
              <input
                v-model="symbolNames[i]"
                class="sd-name-input"
                :placeholder="`Symbol ${i + 1}`"
              />
              <span class="text-xs text-text-muted">{{ box.width }}×{{ box.height }}px</span>
              <button class="sd-remove-btn" @click="removeBox(i)">✕</button>
            </div>
          </div>

          <!-- Action buttons -->
          <div class="flex gap-3 flex-wrap">
            <button
              class="sd-btn-primary"
              :disabled="drawnBoxes.length === 0 || isExtractingTemplates"
              @click="extractTemplates(false)"
            >
              <svg v-if="isExtractingTemplates" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Extract Selected Symbols
            </button>
            <button
              class="sd-btn-secondary"
              :disabled="isExtractingTemplates"
              @click="extractTemplates(true)"
            >
              Auto-Detect Symbols
            </button>
          </div>
        </div>

        <!-- Extracted templates preview -->
        <div v-if="extractedTemplates.length > 0" class="space-y-2">
          <p class="text-xs font-semibold text-text-tertiary uppercase tracking-wider">
            {{ extractedTemplates.length }} Template(s) Ready
          </p>
          <div class="flex flex-wrap gap-3">
            <div
              v-for="(tmpl, i) in extractedTemplates"
              :key="i"
              class="sd-template-chip"
            >
              <img
                :src="`data:image/png;base64,${tmpl.image_b64}`"
                :alt="tmpl.name"
                class="w-10 h-10 object-contain bg-white rounded"
              />
              <span class="text-xs text-text-secondary max-w-[80px] truncate">{{ tmpl.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Step 2: Target P&ID Upload -->
    <section class="sd-card">
      <div class="sd-card-header">
        <span class="sd-step-badge">2</span>
        <h2 class="sd-section-title">Upload Target P&amp;ID</h2>
        <p class="sd-section-sub">The PDF to scan for detected symbols.</p>
      </div>
      <div class="sd-card-body">
        <label class="sd-file-label">
          <input type="file" accept=".pdf" class="hidden" @change="onTargetFileChange" />
          <span class="sd-file-btn">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            Choose Target PDF
          </span>
        </label>
        <p v-if="targetPdfName" class="mt-2 text-sm text-text-tertiary">
          <svg class="w-4 h-4 inline mr-1 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          {{ targetPdfName }}
        </p>
      </div>
    </section>

    <!-- Step 3: Detection Config -->
    <section class="sd-card">
      <div class="sd-card-header">
        <span class="sd-step-badge">3</span>
        <h2 class="sd-section-title">Detection Settings</h2>
        <p class="sd-section-sub">Tune confidence threshold, resolution, and rotation search.</p>
      </div>
      <div class="sd-card-body space-y-4">
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <!-- Threshold -->
          <div class="space-y-1">
            <label class="sd-label">Confidence Threshold: <strong class="text-white">{{ threshold.toFixed(2) }}</strong></label>
            <input type="range" v-model.number="threshold" min="0.5" max="0.99" step="0.01" class="w-full accent-indigo-500" />
            <p class="text-xs text-text-muted">Higher = fewer false positives</p>
          </div>
          <!-- DPI -->
          <div class="space-y-1">
            <label class="sd-label">Rendering DPI</label>
            <select v-model.number="dpi" class="sd-select">
              <option :value="96">96 (faster)</option>
              <option :value="150">150 (recommended)</option>
              <option :value="200">200 (higher quality)</option>
              <option :value="300">300 (best)</option>
            </select>
            <p class="text-xs text-text-muted">Controls PDF page rendering resolution for symbol detection</p>
          </div>
          <!-- Rotation -->
          <div class="space-y-1">
            <label class="sd-label">Rotation Search</label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="enableRotation" class="accent-indigo-500 w-4 h-4" />
              <span class="text-sm text-text-secondary">Enable (0°/90°/180°/270°)</span>
            </label>
            <p class="text-xs text-text-muted">Enables 4× more checks per page</p>
          </div>
        </div>

        <button
          class="sd-btn-run"
          :disabled="!canRunDetection"
          @click="runDetection"
        >
          <svg v-if="isDetecting" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          {{ isDetecting ? 'Detecting…' : 'Run Detection' }}
        </button>

        <p v-if="detectError" class="text-sm text-error">{{ detectError }}</p>
      </div>
    </section>

    <!-- Step 4: Results -->
    <section v-if="detectionResults.length > 0 || annotatedPages.length > 0" class="sd-card">
      <div class="sd-card-header">
        <span class="sd-step-badge">4</span>
        <h2 class="sd-section-title">Detection Results</h2>
        <p class="sd-section-sub">{{ detectionResults.length }} symbol(s) found across {{ annotatedPages.length }} page(s).</p>
      </div>
      <div class="sd-card-body space-y-6">

        <!-- Annotated page viewer -->
        <div v-if="annotatedPages.length > 0" class="space-y-3">
          <div class="flex items-center gap-3">
            <p class="text-sm font-semibold text-text-secondary">Annotated Pages</p>
            <div class="flex gap-2 ml-auto">
              <button class="sd-nav-btn" :disabled="currentPage === 0" @click="currentPage--">‹ Prev</button>
              <span class="text-xs text-text-tertiary">Page {{ currentPage + 1 }} / {{ annotatedPages.length }}</span>
              <button class="sd-nav-btn" :disabled="currentPage === annotatedPages.length - 1" @click="currentPage++">Next ›</button>
            </div>
          </div>
          <img
            :src="`data:image/png;base64,${annotatedPages[currentPage]}`"
            alt="Annotated P&ID page"
            class="w-full rounded-lg border border-border-default shadow-lg"
          />
        </div>

        <!-- Results table -->
        <div class="overflow-x-auto">
          <table class="sd-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Page</th>
                <th>Position (X, Y)</th>
                <th>Size (W × H)</th>
                <th>Confidence</th>
                <th>Tags</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(r, i) in detectionResults" :key="i">
                <td class="font-medium text-text-primary">{{ r.symbol_name }}</td>
                <td>{{ r.page }}</td>
                <td>{{ r.bbox.x }}, {{ r.bbox.y }}</td>
                <td>{{ r.bbox.width }} × {{ r.bbox.height }}</td>
                <td>
                  <span :class="r.confidence >= 0.9 ? 'text-success' : r.confidence >= 0.75 ? 'text-warning' : 'text-text-tertiary'">
                    {{ (r.confidence * 100).toFixed(1) }}%
                  </span>
                </td>
                <td class="text-xs text-text-tertiary">{{ (r.associated_tags ?? []).join(", ") || "—" }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Export button -->
        <button class="sd-btn-export" :disabled="isExporting" @click="handleExport">
          <svg v-if="isExporting" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          {{ isExporting ? 'Exporting…' : 'Export to Excel' }}
        </button>

      </div>
    </section>

  </div>
</template>

<style scoped>
@reference "@/style.css";

.sd-layout {
  @apply w-full;
}

.sd-card {
  @apply rounded-2xl border border-border-default bg-bg-card/60 backdrop-blur-sm overflow-hidden;
}

.sd-card-header {
  @apply px-space-6 py-space-5 border-b border-border-subtle flex flex-col gap-1;
}

.sd-card-body {
  @apply px-space-6 py-space-5;
}

.sd-step-badge {
  @apply inline-flex items-center justify-center w-7 h-7 rounded-full bg-accent-600 text-white text-sm font-black mb-1;
}

.sd-section-title {
  @apply text-base font-bold text-text-primary;
}

.sd-section-sub {
  @apply text-xs text-text-muted;
}

.sd-file-label {
  @apply cursor-pointer inline-block;
}

.sd-file-btn {
  @apply inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-bg-input text-text-secondary text-sm font-semibold
         border border-border-default hover:bg-bg-input-hover transition-colors;
}

.sd-canvas-wrap {
  @apply relative w-full border border-border-default rounded-xl overflow-hidden cursor-crosshair;
}

.sd-canvas {
  @apply w-full h-full object-contain;
}

.sd-canvas-overlay {
  @apply absolute inset-0 flex items-center justify-center bg-black/40;
}

.sd-name-input {
  @apply flex-1 px-3 py-1.5 rounded-lg bg-bg-input border border-border-default text-sm text-text-secondary
         focus:outline-none focus:ring-1 focus:ring-accent-500;
}

.sd-remove-btn {
  @apply px-2 py-1 rounded-lg bg-error-bg text-error text-xs hover:bg-red-500/20 transition-colors;
}

.sd-template-chip {
  @apply flex flex-col items-center gap-1 p-2 rounded-xl border border-border-default bg-bg-input/60;
}

.sd-label {
  @apply block text-xs font-semibold text-text-tertiary uppercase tracking-wider;
}

.sd-select {
  @apply w-full px-3 py-2 rounded-xl bg-bg-input border border-border-default text-sm text-text-secondary
         focus:outline-none focus:ring-1 focus:ring-accent-500;
}

.sd-nav-btn {
  @apply px-3 py-1 rounded-lg bg-bg-input text-text-tertiary text-xs font-semibold border border-border-default
         hover:bg-bg-input-hover disabled:opacity-40 disabled:cursor-not-allowed transition-colors;
}

.sd-btn-primary {
  @apply inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-accent-600 text-white text-sm font-semibold
         hover:bg-accent-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors;
}

.sd-btn-secondary {
  @apply inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-bg-input-hover text-white text-sm font-semibold
         hover:bg-bg-input disabled:opacity-40 disabled:cursor-not-allowed transition-colors border border-border-default;
}

.sd-btn-run {
  @apply inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-success text-white text-sm font-bold
         hover:bg-emerald-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors shadow-lg shadow-success/30;
}

.sd-btn-export {
  @apply inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-bg-input text-white text-sm font-semibold
         hover:bg-bg-input-hover disabled:opacity-40 disabled:cursor-not-allowed transition-colors border border-border-default;
}

.sd-table {
  @apply w-full text-sm text-text-secondary border-collapse;
}

.sd-table thead tr {
  @apply bg-bg-input/80 text-xs uppercase tracking-wider text-text-tertiary;
}

.sd-table th {
  @apply px-4 py-3 text-left font-semibold;
}

.sd-table tbody tr {
  @apply border-t border-border-subtle hover:bg-white/3 transition-colors;
}

.sd-table td {
  @apply px-4 py-2.5;
}
</style>
