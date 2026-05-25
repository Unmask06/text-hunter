<template>
  <div
    :class="[
      'bg-bg-card border border-border-default rounded-xl transition-all duration-base',
      variantClasses[variant],
    ]"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
interface Props {
  variant?: "default" | "elevated" | "interactive";
}

withDefaults(defineProps<Props>(), {
  variant: "default",
});

const variantClasses = {
  default: "",
  elevated: "shadow-md hover:shadow-lg hover:border-border-strong",
  interactive: "cursor-pointer hover:bg-bg-card-hover hover:border-border-strong",
};
</script>
