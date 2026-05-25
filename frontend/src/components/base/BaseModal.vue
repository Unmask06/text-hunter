<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-base"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-fast"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center p-space-6"
        @click.self="close"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-bg-backdrop backdrop-blur-sm" />

        <!-- Modal -->
        <div
          class="relative bg-bg-card border border-border-default rounded-2xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto animate-fade-in"
        >
          <!-- Header -->
          <div
            v-if="title || $slots.header"
            class="flex items-center justify-between px-space-6 py-space-5 border-b border-border-subtle"
          >
            <slot name="header">
              <h3 class="text-lg font-semibold text-text-primary">{{ title }}</h3>
            </slot>
            <button
              v-if="closable"
              class="p-1 rounded-md text-text-muted hover:text-text-secondary hover:bg-bg-input transition-colors"
              @click="close"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Body -->
          <div class="px-space-6 py-space-5">
            <slot />
          </div>

          <!-- Footer -->
          <div
            v-if="$slots.footer"
            class="flex items-center justify-end gap-space-3 px-space-6 py-space-4 border-t border-border-subtle"
          >
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
interface Props {
  modelValue: boolean;
  title?: string;
  closable?: boolean;
}

withDefaults(defineProps<Props>(), {
  title: "",
  closable: true,
});

const emit = defineEmits<{
  "update:modelValue": [value: boolean];
}>();

function close() {
  emit("update:modelValue", false);
}
</script>
