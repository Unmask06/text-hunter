<script setup lang="ts">
import { checkLicense, type LicenseStatus } from "@/services/license.ts";
import { onBeforeUnmount, onMounted, ref } from "vue";

// Web mode: render immediately without any loading screen.
const status = ref<LicenseStatus | null>({ valid: true, message: "" });
const isLoading = ref(false);
const error = ref("");
const isOffline = ref(false);
const retryCount = ref(0);
const maxRetries = 10;
const retryDelay = 500; // ms
const showSuccessModal = ref(false);
let successModalTimer: ReturnType<typeof setTimeout> | null = null;

const emit = defineEmits<{
  validated: [valid: boolean];
}>();

onBeforeUnmount(() => {
  if (successModalTimer !== null) clearTimeout(successModalTimer);
});

/**
 * Wait for sidecar to be ready with retries.
 * The Python sidecar takes time to start up.
 */
async function waitForSidecar(): Promise<LicenseStatus> {
  while (retryCount.value < maxRetries) {
    try {
      const result = await checkLicense();
      return result;
    } catch (e) {
      retryCount.value++;
      if (retryCount.value >= maxRetries) {
        throw e;
      }
      await new Promise((resolve) => setTimeout(resolve, retryDelay));
    }
  }
  throw new Error("Max retries reached");
}

onMounted(async () => {
  // Web mode: app is already visible (status set synchronously above).
  // Do a background version check — no blocking UI.
  emit("validated", true);
  try {
    const result = await waitForSidecar();
    status.value = result;
  } catch {
    // API unreachable — app already rendered, nothing to do
  }
});
</script>

<template>
  <!-- Loading Overlay -->
  <div
    v-if="isLoading"
    class="fixed inset-0 z-50 flex items-center justify-center bg-bg-overlay backdrop-blur-md"
  >
    <div class="bg-bg-card border border-border-default rounded-2xl p-space-10 text-center shadow-xl max-w-sm mx-space-6">
      <div
        class="w-12 h-12 rounded-full border-b-2 border-accent-500 animate-spin mx-auto"
      />
      <p class="mt-space-4 text-text-secondary">Checking version...</p>
      <p class="mt-space-2 text-xs text-text-muted">
        Connecting to backend ({{ retryCount + 1 }}/{{ maxRetries }})...
      </p>
    </div>
  </div>

  <!-- Error Overlay -->
  <div
    v-else-if="error"
    class="fixed inset-0 z-50 flex items-center justify-center bg-bg-overlay backdrop-blur-md"
  >
    <div class="bg-bg-card border border-error-border rounded-2xl p-space-10 text-center shadow-xl max-w-sm mx-space-6">
      <svg
        class="w-12 h-12 text-error mx-auto"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <h3 class="text-xl font-semibold text-text-primary mt-space-4">
        Update Required
      </h3>
      <p class="text-text-secondary mt-space-2 text-sm">{{ error }}</p>

      <button
        @click="$emit('validated', false)"
        class="mt-space-6 block w-full px-space-4 py-space-3 bg-bg-input hover:bg-bg-input-hover text-text-primary rounded-lg text-sm font-medium transition-colors border border-border-default"
      >
        Close Application
      </button>

      <p class="mt-space-4 text-xs text-text-muted">
        Please download the latest version to continue.
      </p>
    </div>
  </div>

  <!-- Success Overlay -->
  <div
    v-else-if="status?.valid && showSuccessModal"
    class="fixed inset-0 z-50 flex items-center justify-center bg-bg-overlay/90 backdrop-blur-md"
  >
    <div class="bg-bg-card border border-border-default rounded-2xl p-space-10 text-center shadow-xl max-w-sm mx-space-6">
      <svg
        class="w-12 h-12 text-success mx-auto"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M5 13l4 4L19 7"
        />
      </svg>
      <h3 class="text-lg font-semibold text-text-primary mt-space-3">
        {{ isOffline ? "Offline Mode" : "License Validated" }}
      </h3>
      <p class="text-text-secondary mt-space-1 text-sm">{{ status.message }}</p>
      <p v-if="status?.details" class="text-xs text-text-muted mt-space-2">
        v{{ status.details.local_version }}
        <span v-if="status.details.latest_version">
          | Latest: v{{ status.details.latest_version }}
        </span>
      </p>
    </div>
  </div>

  <!-- App content - always shown when license is valid -->
  <div
    v-if="status?.valid"
    :style="{ opacity: showSuccessModal ? 0 : 1, transition: 'opacity 0.3s' }"
  >
    <slot></slot>
  </div>
</template>

<style scoped>
@reference "@/style.css";

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
