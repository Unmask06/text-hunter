<template>
  <span
    :class="[
      'inline-flex items-center px-space-3 py-space-1 rounded-full text-xs font-medium',
      variantClasses[variant],
    ]"
  >
    <span
      v-if="dot"
      :class="[
        'w-1.5 h-1.5 rounded-full mr-1.5',
        dotClasses[variant],
      ]"
    />
    <slot />
  </span>
</template>

<script setup lang="ts">
interface Props {
  variant?: "success" | "warning" | "error" | "info" | "neutral";
  dot?: boolean;
}

withDefaults(defineProps<Props>(), {
  variant: "neutral",
  dot: false,
});

const variantClasses = {
  success: "bg-success-bg text-success border border-success-border",
  warning: "bg-warning-bg text-warning border border-warning-border",
  error: "bg-error-bg text-error border border-error-border",
  info: "bg-info-bg text-info border border-info-border",
  neutral: "bg-bg-input text-text-tertiary border border-border-default",
};

const dotClasses = {
  success: "bg-success",
  warning: "bg-warning",
  error: "bg-error",
  info: "bg-info",
  neutral: "bg-text-muted",
};
</script>
