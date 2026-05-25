<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="[
      'inline-flex items-center justify-center gap-space-2 font-semibold text-sm rounded-lg transition-all duration-fast whitespace-nowrap',
      'focus-visible:ring-2 focus-visible:ring-accent-500 focus-visible:ring-offset-2 focus-visible:ring-offset-bg-page',
      'disabled:opacity-40 disabled:cursor-not-allowed',
      sizeClasses[size],
      variantClasses[variant],
    ]"
    @click="$emit('click', $event)"
  >
    <svg
      v-if="loading"
      class="w-4 h-4 animate-spin"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
    </svg>
    <slot v-else name="icon" />
    <slot />
  </button>
</template>

<script setup lang="ts">
interface Props {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  type?: "button" | "submit" | "reset";
  disabled?: boolean;
  loading?: boolean;
}

withDefaults(defineProps<Props>(), {
  variant: "primary",
  size: "md",
  type: "button",
  disabled: false,
  loading: false,
});

defineEmits<{
  click: [event: MouseEvent];
}>();

const variantClasses = {
  primary:
    "bg-accent-600 text-white border border-transparent shadow-accent hover:bg-accent-500 hover:shadow-lg hover:-translate-y-px active:translate-y-0",
  secondary:
    "bg-bg-input text-text-primary border border-border-default hover:bg-bg-input-hover hover:border-border-strong",
  ghost:
    "bg-transparent text-text-tertiary border border-transparent hover:bg-bg-input hover:text-text-secondary",
  danger:
    "bg-error-bg text-error border border-error-border hover:border-error",
};

const sizeClasses = {
  sm: "px-space-3 py-space-1.5 text-xs rounded-md",
  md: "px-space-5 py-space-3 text-sm rounded-lg",
  lg: "px-space-6 py-space-3.5 text-base rounded-xl",
};
</script>
