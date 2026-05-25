<template>
  <button
    class="relative p-2.5 rounded-xl bg-bg-input border border-border-default text-text-tertiary hover:text-text-secondary hover:bg-bg-input-hover hover:border-border-strong transition-all duration-base"
    :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
    @click="toggle"
  >
    <Transition
      mode="out-in"
      enter-active-class="transition-all duration-fast"
      enter-from-class="opacity-0 rotate-90 scale-50"
      enter-to-class="opacity-100 rotate-0 scale-100"
      leave-active-class="transition-all duration-fast"
      leave-from-class="opacity-100 rotate-0 scale-100"
      leave-to-class="opacity-0 -rotate-90 scale-50"
    >
      <!-- Sun icon (show when dark mode — clicking switches to light) -->
      <svg
        v-if="isDark"
        key="sun"
        class="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
        />
      </svg>
      <!-- Moon icon (show when light mode — clicking switches to dark) -->
      <svg
        v-else
        key="moon"
        class="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
        />
      </svg>
    </Transition>
  </button>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";

const isDark = ref(true);

function toggle() {
  isDark.value = !isDark.value;
  const theme = isDark.value ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("theme", theme);
}

onMounted(() => {
  const saved = localStorage.getItem("theme");
  if (saved) {
    isDark.value = saved === "dark";
    document.documentElement.setAttribute("data-theme", saved);
  } else {
    // Default to dark
    document.documentElement.setAttribute("data-theme", "dark");
  }
});
</script>
