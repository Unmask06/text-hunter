<script setup lang="ts">
import { ref, onMounted } from "vue";
import { checkLicense, type LicenseStatus } from "@/services/license.ts";

const status = ref<LicenseStatus | null>(null);
const isLoading = ref(true);
const error = ref("");
const isOffline = ref(false);

const emit = defineEmits<{
  validated: [valid: boolean];
}>();

onMounted(async () => {
  try {
    const result = await checkLicense();
    status.value = result;

    if (!result.valid) {
      error.value = result.message;
      emit("validated", false);
    } else {
      // Valid license - emit success and continue
      isOffline.value = result.offline ?? false;
      setTimeout(() => {
        emit("validated", true);
      }, 500); // Small delay to show success state
    }
  } catch (e) {
    const errorMessage = e instanceof Error ? e.message : "Unknown error";
    error.value = `Failed to connect to license server: ${errorMessage}`;
    emit("validated", false);
  } finally {
    isLoading.value = false;
  }
});
</script>

<template>
  <div v-if="isLoading" class="license-overlay">
    <div class="license-modal">
      <div class="spinner"></div>
      <p class="mt-4 text-slate-300">Validating license...</p>
      <p class="mt-2 text-xs text-slate-500">Checking GitHub releases</p>
    </div>
  </div>

  <div v-else-if="error" class="license-overlay">
    <div class="license-modal error">
      <svg class="w-12 h-12 text-red-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <h3 class="text-xl font-semibold text-white mt-4">License Validation Failed</h3>
      <p class="text-slate-400 mt-2 text-sm">{{ error }}</p>

      <div class="mt-6 space-y-3">
        <a
          href="https://github.com/Unmask06/text-hunter/releases"
          target="_blank"
          class="block px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors text-center"
        >
          Download Latest Version
        </a>
        <button
          @click="$emit('validated', false)"
          class="block w-full px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm font-medium transition-colors"
        >
          Close Application
        </button>
      </div>

      <p class="mt-4 text-xs text-slate-500">
        TextHunter requires a valid version from GitHub releases.
      </p>
    </div>
  </div>

  <div v-else-if="status?.valid" class="license-overlay success">
    <div class="license-modal">
      <svg class="w-12 h-12 text-emerald-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
      </svg>
      <h3 class="text-lg font-semibold text-white mt-3">
        {{ isOffline ? 'Offline Mode' : 'License Validated' }}
      </h3>
      <p class="text-slate-400 mt-1 text-sm">{{ status.message }}</p>
      <p v-if="status?.details" class="text-xs text-slate-500 mt-2">
        v{{ status.details.local_version }}
        <span v-if="status.details.latest_version">
          | Latest: v{{ status.details.latest_version }}
        </span>
      </p>
    </div>
  </div>

  <!-- Hidden container that reveals app content when valid -->
  <div v-if="status?.valid" class="contents">
    <slot></slot>
  </div>
</template>

<style scoped>
.license-overlay {
  position: fixed;
  inset: 0;
  background-color: rgb(2 6 23 / 0.95);
  backdrop-filter: blur(8px);
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
}

.license-overlay.success {
  background-color: rgb(2 6 23 / 0.9);
}

.license-modal {
  background-color: rgb(15 23 42);
  border-radius: 1rem;
  padding: 2rem;
  max-width: 28rem;
  width: 100%;
  margin: 1rem;
  border: 1px solid rgb(255 255 255 / 0.1);
  text-align: center;
  box-shadow: 0 25px 50px -12px rgb(0 0 0 / 0.25);
}

.license-modal.error {
  border-color: rgb(239 68 68 / 0.3);
  box-shadow: 0 25px 50px -12px rgb(127 29 29 / 0.2);
}

.spinner {
  animation: spin 1s linear infinite;
  border-radius: 9999px;
  height: 3rem;
  width: 3rem;
  border-bottom-width: 2px;
  border-color: rgb(99 102 241);
  margin-left: auto;
  margin-right: auto;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
