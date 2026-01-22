<script setup>
/**
 * RegexConfig.vue - Regex configuration panel with manual and helper modes
 */
import { computed, ref, watch } from 'vue';
import { guessRegex } from '../services/api.js';

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['extract', 'update:config']);

// Mode toggle
const mode = ref('manual'); // 'manual' or 'helper'

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
</script>

<template>
  <div class="glass-card p-6 space-y-6">
    <h2 class="text-lg font-semibold text-primary-100">Regex Configuration</h2>

    <!-- Mode Toggle -->
    <div class="toggle-group">
      <button :class="['toggle-btn', { active: mode === 'manual' }]" @click="mode = 'manual'">
        Manual Regex
      </button>
      <button :class="['toggle-btn', { active: mode === 'helper' }]" @click="mode = 'helper'">
        Regex Helper
      </button>
    </div>

    <!-- Manual Mode -->
    <div v-if="mode === 'manual'" class="space-y-4 fade-in">
      <div>
        <label class="block text-sm font-medium text-primary-300 mb-2">
          Keyword Regex <span class="text-accent-500">*</span>
        </label>
        <input v-model="keywordRegex" type="text" class="input-field w-full" placeholder='e.g., \d+"-[A-Z]+-\d+'
          :disabled="disabled" />
        <p class="text-xs text-primary-500 mt-1">
          Pattern to find in PDF text content
        </p>
      </div>

      <div>
        <label class="block text-sm font-medium text-primary-300 mb-2">
          File Identifier Regex <span class="text-primary-500">(optional)</span>
        </label>
        <input v-model="fileIdentifierRegex" type="text" class="input-field w-full" placeholder='e.g., ^(\d{4})_([^_]+)'
          :disabled="disabled" />
        <p class="text-xs text-primary-500 mt-1">
          Extract metadata from filenames (groups become columns)
        </p>
      </div>
    </div>

    <!-- Helper Mode -->
    <div v-else class="space-y-4 fade-in">
      <div>
        <label class="block text-sm font-medium text-primary-300 mb-2">
          Example Strings
        </label>
        <p class="text-xs text-primary-500 mb-3">
          Enter 2-3 examples of the text you want to match
        </p>

        <div class="space-y-2">
          <input v-for="(_, index) in examples" :key="index" v-model="examples[index]" type="text"
            class="input-field w-full" :placeholder="`Example ${index + 1}: e.g., 10&quot;-FG-001`"
            :disabled="disabled || isGenerating" />
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
      <div v-if="suggestedPattern" class="bg-surface-800 rounded-lg p-4 space-y-3">
        <div>
          <label class="block text-xs font-medium text-primary-400 mb-1">
            Suggested Pattern
          </label>
          <code class="block text-accent-400 font-mono text-sm bg-surface-900 p-2 rounded">
            {{ suggestedPattern }}
          </code>
        </div>

        <div>
          <label class="block text-xs font-medium text-primary-400 mb-1">
            Explanation
          </label>
          <p class="text-primary-300 text-sm">{{ patternExplanation }}</p>
        </div>

        <div>
          <label class="block text-xs font-medium text-primary-400 mb-1">
            Test Results
          </label>
          <div class="flex flex-wrap gap-2">
            <span v-for="(matched, example) in testResults" :key="example" :class="[
              'text-xs px-2 py-1 rounded',
              matched ? 'bg-success-500/20 text-success-500' : 'bg-error-500/20 text-error-500'
            ]">
              {{ example }}: {{ matched ? '✓' : '✗' }}
            </span>
          </div>
        </div>

        <button class="text-sm text-accent-400 hover:text-accent-300 underline" @click="useSuggestedPattern">
          Use this pattern in Manual mode
        </button>
      </div>

      <!-- File Identifier in Helper Mode -->
      <div>
        <label class="block text-sm font-medium text-primary-300 mb-2">
          File Identifier Regex <span class="text-primary-500">(optional)</span>
        </label>
        <input v-model="fileIdentifierRegex" type="text" class="input-field w-full" placeholder='e.g., ^(\d{4})_([^_]+)'
          :disabled="disabled" />
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
