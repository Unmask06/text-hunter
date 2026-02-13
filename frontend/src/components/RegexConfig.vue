<script setup>
/**
 * RegexConfig.vue - Regex configuration panel with manual and helper modes
 */
import { computed, ref, watch } from 'vue';
import { guessRegex } from '../services/api.ts';

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['extract', 'update:config']);

// Mode toggle
const mode = ref('helper'); // 'helper' (AI) or 'manual'

// Manual mode inputs
const keywordRegex = ref('');
const fileIdentifierRegex = ref('');

// Helper mode inputs
const examples = ref(['', '', '']);
const suggestedPattern = ref('');
const patternExplanation = ref('');
const testResults = ref({});
const isGenerating = ref(false);
const generateError = ref('');

// Computed config object
const config = computed(() => ({
  keywordRegex: mode.value === 'helper' && suggestedPattern.value
    ? suggestedPattern.value
    : keywordRegex.value,
  fileIdentifierRegex: fileIdentifierRegex.value || null,
}));

// Emit config changes
watch(config, (newConfig) => {
  emit('update:config', newConfig);
}, { deep: true });

// Validation
const isValid = computed(() => {
  if (mode.value === 'manual') {
    return keywordRegex.value.trim().length > 0;
  } else {
    return suggestedPattern.value.length > 0;
  }
});

const filledExamples = computed(() =>
  examples.value.filter(ex => ex.trim().length > 0)
);

async function handleGenerateRegex() {
  if (filledExamples.value.length < 2) {
    generateError.value = 'Please enter at least 2 examples';
    return;
  }

  isGenerating.value = true;
  generateError.value = '';

  try {
    const result = await guessRegex(filledExamples.value);
    suggestedPattern.value = result.pattern;
    patternExplanation.value = result.explanation;
    testResults.value = result.test_results;
  } catch (error) {
    console.error('Failed to generate regex:', error);
    generateError.value = error.response?.data?.detail || 'Failed to generate pattern';
  } finally {
    isGenerating.value = false;
  }
}

function handleExtract() {
  if (!isValid.value) return;
  emit('extract', config.value);
}

function useSuggestedPattern() {
  keywordRegex.value = suggestedPattern.value;
  mode.value = 'manual';
}

function addExample() {
  examples.value.push('');
}

function removeExample(index) {
  if (examples.value.length > 2) {
    examples.value.splice(index, 1);
  }
}
</script>

<template>
  <div class="config-card p-6 space-y-6">
    <h2 class="text-lg font-semibold text-primary-100">Regex Configuration</h2>

    <!-- Mode Toggle -->
    <div class="toggle-group">
      <button :class="['toggle-btn', { active: mode === 'helper' }]" @click="mode = 'helper'">
        AI Pattern Generator
      </button>
      <button :class="['toggle-btn', { active: mode === 'manual' }]" @click="mode = 'manual'">
        Advanced Manual Regex
      </button>
    </div>

    <!-- Helper Mode (AI Pattern Generator) -->
    <div v-if="mode === 'helper'" class="space-y-4 animate-fade-in">
      <div>
        <label class="input-label">
          Example Strings
        </label>
        <p class="helper-text mb-3">
          Enter at least 2 examples of the text you want to match (add more for better results)
        </p>

        <div class="space-y-2">
          <div v-for="(example, index) in examples" :key="index" class="flex gap-2">
            <input v-model="examples[index]" type="text" class="input-field flex-1"
              :placeholder="`Example ${index + 1}: e.g., 10&quot;-FG-001`" :disabled="disabled || isGenerating" />
            <button v-if="examples.length > 2" @click="removeExample(index)" class="remove-btn"
              :disabled="disabled || isGenerating">×</button>
          </div>
          <button @click="addExample" class="add-btn" :disabled="disabled || isGenerating">+</button>
        </div>
      </div>

      <button class="btn-accent w-full" :disabled="disabled || isGenerating || filledExamples.length < 2"
        @click="handleGenerateRegex">
        {{ isGenerating ? 'Generating...' : 'Generate Pattern' }}
      </button>

      <div v-if="generateError" class="text-error-500 text-sm">
        {{ generateError }}
      </div>

      <!-- Suggested Pattern Result -->
      <div v-if="suggestedPattern" class="suggested-card">
        <div>
          <label class="badge-label">
            Suggested Pattern
          </label>
          <code class="pattern-display">
            {{ suggestedPattern }}
          </code>
        </div>

        <div>
          <label class="badge-label">
            Explanation
          </label>
          <p class="text-primary-300 text-sm">{{ patternExplanation }}</p>
        </div>

        <div>
          <label class="badge-label">
            Test Results
          </label>
          <div class="flex flex-wrap gap-2">
            <span v-for="(matched, example) in testResults" :key="example" :class="[
              'result-badge',
              matched ? 'badge-success' : 'badge-error'
            ]">
              {{ example }}: {{ matched ? '✓' : '✗' }}
            </span>
          </div>
        </div>

        <button class="use-pattern-link" @click="useSuggestedPattern">
          Use this pattern in Manual mode
        </button>
      </div>

      <!-- File Identifier in Helper Mode -->
      <div>
        <label class="input-label">
          File Identifier Regex <span class="text-primary-500">(optional)</span>
        </label>
        <input v-model="fileIdentifierRegex" type="text" class="input-field" placeholder='e.g., ^(\d{4})_([^_]+)'
          :disabled="disabled" />
      </div>
    </div>

    <!-- Manual Mode (Advanced) -->
    <div v-else class="space-y-4 animate-fade-in">
      <div>
        <label class="input-label">
          Keyword Regex <span class="text-accent-500">*</span>
        </label>
        <input v-model="keywordRegex" type="text" class="input-field" placeholder='e.g., \d+"-[A-Z]+-\d+'
          :disabled="disabled" />
        <p class="helper-text">
          Pattern to find in PDF text content
        </p>
      </div>

      <div>
        <label class="input-label">
          File Identifier Regex <span class="text-primary-500">(optional)</span>
        </label>
        <input v-model="fileIdentifierRegex" type="text" class="input-field" placeholder='e.g., ^(\d{4})_([^_]+)'
          :disabled="disabled" />
        <p class="helper-text">
          Extract metadata from filenames (groups become columns)
        </p>
      </div>
    </div>

    <!-- Extract Button -->
    <button class="btn-primary w-full" :disabled="disabled || !isValid" @click="handleExtract">
      <span class="flex items-center justify-center gap-2">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        Extract Matches
      </span>
    </button>
  </div>
</template>

<style scoped>
@reference "@/style.css";

.config-card {
  @apply bg-slate-900/80 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl;
}

.toggle-group {
  @apply inline-flex bg-slate-800 rounded-lg p-1;
}

.toggle-btn {
  @apply px-4 py-2 rounded-md font-medium transition-all duration-200 text-slate-400;
}

.toggle-btn.active {
  @apply bg-indigo-600 text-white shadow-lg;
}

.input-label {
  @apply block text-sm font-medium text-slate-300 mb-2;
}

.input-field {
  @apply w-full px-4 py-3 rounded-lg bg-slate-800 border border-white/10 text-slate-100 font-mono;
  @apply transition-all duration-200 focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/20;
  @apply placeholder:text-slate-500 disabled:opacity-50;
}

.helper-text {
  @apply text-xs text-slate-500 mt-1;
}

.btn-primary {
  @apply px-6 py-3 rounded-lg font-semibold text-white cursor-pointer;
  @apply bg-linear-to-br from-indigo-500 to-indigo-600 border border-white/10 shadow-lg;
  @apply transition-all duration-200 transform hover:-translate-y-0.5 hover:shadow-indigo-500/20 active:translate-y-0 disabled:opacity-50;
}

.btn-accent {
  @apply px-6 py-3 rounded-lg font-semibold text-white;
  @apply bg-linear-to-br from-cyan-500 to-cyan-600 border border-white/10 shadow-lg;
  @apply transition-all duration-200 transform hover:-translate-y-0.5 hover:shadow-cyan-500/20 disabled:opacity-50;
}

.remove-btn {
  @apply px-2 py-1 text-red-400 hover:text-red-300 bg-red-500/10 hover:bg-red-500/20 rounded border border-red-500/20 transition-colors disabled:opacity-50;
}

.add-btn {
  @apply px-3 py-1 text-cyan-400 hover:text-cyan-300 bg-cyan-500/10 hover:bg-cyan-500/20 rounded border border-cyan-500/20 transition-colors disabled:opacity-50;
}

.suggested-card {
  @apply bg-slate-800 rounded-xl p-4 space-y-4 border border-white/5;
}

.badge-label {
  @apply block text-[10px] uppercase tracking-wider font-bold text-slate-500 mb-1.5;
}

.pattern-display {
  @apply block text-cyan-400 font-mono text-sm bg-slate-950 p-3 rounded-lg border border-white/5;
}

.result-badge {
  @apply text-xs px-2.5 py-1 rounded-full font-medium;
}

.badge-success {
  @apply bg-emerald-500/10 text-emerald-400 border border-emerald-500/20;
}

.badge-error {
  @apply bg-red-500/10 text-red-400 border border-red-500/20;
}

.use-pattern-link {
  @apply text-sm text-cyan-400 hover:text-cyan-300 underline underline-offset-4 transition-colors;
}
</style>
