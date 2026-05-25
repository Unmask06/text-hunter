<template>
  <div class="form-group">
    <label v-if="label" :for="inputId" class="block text-sm font-medium text-text-secondary mb-space-2">
      {{ label }}
      <span v-if="required" class="text-error">*</span>
    </label>
    <input
      :id="inputId"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :class="[
        'w-full px-space-4 py-space-3 bg-bg-input border border-border-default rounded-lg text-sm text-text-primary placeholder:text-text-muted',
        'transition-all duration-base',
        'hover:border-border-strong',
        'focus:border-accent-500 focus:ring-2 focus:ring-border-focus focus:outline-none',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        error && 'border-error focus:border-error focus:ring-error-border',
      ]"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
    <p v-if="helpText && !error" class="mt-space-2 text-xs text-text-muted leading-relaxed">
      {{ helpText }}
    </p>
    <p v-if="error" class="mt-space-2 text-xs text-error">
      {{ error }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

interface Props {
  modelValue: string;
  label?: string;
  type?: string;
  placeholder?: string;
  helpText?: string;
  error?: string;
  disabled?: boolean;
  required?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  type: "text",
  disabled: false,
  required: false,
});

defineEmits<{
  "update:modelValue": [value: string];
}>();

const inputId = computed(() => `input-${Math.random().toString(36).substr(2, 9)}`);
</script>
