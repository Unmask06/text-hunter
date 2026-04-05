<script setup>
/**
 * RegexConfig.vue - Pattern configuration panel with Pattern Generator and Presets modes
 */
import { computed, ref, watch, onMounted } from "vue";
import { guessRegex } from "../services/api.ts";
import {
    getAllSavedPatterns,
    addSavedPattern,
    updateSavedPattern,
    deleteSavedPattern,
} from "../services/db.ts";

const props = defineProps({
    disabled: {
        type: Boolean,
        default: false,
    },
});

const emit = defineEmits(["extract", "update:config"]);

// Mode toggle: 'helper' | 'presets'
const mode = ref("helper");

// Shared field — active pattern when using presets
const keywordRegex = ref("");
const fileIdentifierRegex = ref("");

// Pattern Generator (helper) mode
const examples = ref(["", "", ""]);
const suggestedPattern = ref("");
const patternExplanation = ref("");
const testResults = ref({});
const isGenerating = ref(false);
const generateError = ref("");
const isEditingPattern = ref(false); // inline edit for suggestedPattern

// Presets mode
const savedPatterns = ref([]);
const savePatternName = ref("");
const isSaving = ref(false);
const editingId = ref(null);   // rename saved pattern
const editingName = ref("");
const isEditingActivePattern = ref(false); // inline edit for loaded preset

const BUILT_IN_PRESETS = [
    {
        name: "ISA Instrument Tag",
        pattern: "[A-Z]{2,4}-\\d{3,4}[A-Z]?",
        description: "e.g., FIC-101, PT-2305, TT-101A",
    },
    {
        name: "P&ID Line Number",
        pattern: '\\d{1,4}"-[A-Z]{1,4}-\\d{3,4}',
        description: 'e.g., 10"-FG-001, 6"-P-1234',
    },
    {
        name: "Equipment Tag",
        pattern: "[A-Z]{1,3}-\\d{2,4}[A-Z]?",
        description: "e.g., E-101, V-201, T-301A",
    },
    {
        name: "Valve Tag",
        pattern: "[A-Z]{2,4}V-\\d{3,4}[A-Z]?",
        description: "e.g., MOV-101, SDV-202, PSV-301",
    },
    {
        name: "Revision Mark",
        pattern: "Rev\\.?\\s*[A-Z0-9]+",
        description: "e.g., Rev. A, Rev.0, Rev B",
    },
];

const config = computed(() => ({
    keywordRegex:
        mode.value === "helper" ? suggestedPattern.value : keywordRegex.value,
    fileIdentifierRegex: fileIdentifierRegex.value || null,
}));

watch(config, (newConfig) => emit("update:config", newConfig), { deep: true });

const isValid = computed(() => {
    if (mode.value === "helper") return suggestedPattern.value.length > 0;
    return keywordRegex.value.trim().length > 0;
});

const filledExamples = computed(() =>
    examples.value.filter((ex) => ex.trim().length > 0),
);

const activePatternPreview = computed(() => config.value.keywordRegex || "");

onMounted(async () => {
    await seedBuiltInPresets();
    await loadSavedPatterns();
});

async function seedBuiltInPresets() {
    const all = await getAllSavedPatterns();
    const existingNames = new Set(all.map((p) => p.name));
    for (const preset of BUILT_IN_PRESETS) {
        if (!existingNames.has(preset.name)) {
            await addSavedPattern({
                name: preset.name,
                pattern: preset.pattern,
                isBuiltIn: true,
                createdAt: new Date().toISOString(),
            });
        }
    }
}

async function loadSavedPatterns() {
    const all = await getAllSavedPatterns();
    // Built-ins first, then user patterns by recency
    savedPatterns.value = [
        ...all.filter((p) => p.isBuiltIn),
        ...all.filter((p) => !p.isBuiltIn),
    ];
}

async function handleGeneratePattern() {
    if (filledExamples.value.length < 2) {
        generateError.value = "Please enter at least 2 examples";
        return;
    }
    isGenerating.value = true;
    generateError.value = "";
    isEditingPattern.value = false;
    try {
        const result = await guessRegex(filledExamples.value);
        suggestedPattern.value = result.pattern;
        patternExplanation.value = result.explanation;
        testResults.value = result.test_results;
    } catch (error) {
        console.error("Failed to generate pattern:", error);
        generateError.value =
            error.response?.data?.detail || "Failed to generate pattern";
    } finally {
        isGenerating.value = false;
    }
}

function handleExtract() {
    if (!isValid.value) return;
    emit("extract", config.value);
}

function addExample() {
    examples.value.push("");
}

function removeExample(index) {
    if (examples.value.length > 2) {
        examples.value.splice(index, 1);
    }
}

function loadPreset(preset) {
    keywordRegex.value = preset.pattern;
    fileIdentifierRegex.value = preset.fileIdentifierRegex || "";
    savePatternName.value = preset.name;
    isEditingActivePattern.value = false;
}

async function handleSavePattern() {
    const patternToSave = activePatternPreview.value;
    const name = savePatternName.value.trim();
    if (!patternToSave || !name) return;
    isSaving.value = true;
    try {
        const existing = savedPatterns.value.find((p) => p.name === name);
        if (existing?.id) {
            await updateSavedPattern(existing.id, {
                pattern: patternToSave,
                fileIdentifierRegex: config.value.fileIdentifierRegex || undefined,
                isBuiltIn: false, // user-modified, no longer built-in
            });
        } else {
            await addSavedPattern({
                name,
                pattern: patternToSave,
                fileIdentifierRegex: config.value.fileIdentifierRegex || undefined,
                createdAt: new Date().toISOString(),
            });
        }
        savePatternName.value = "";
        await loadSavedPatterns();
    } finally {
        isSaving.value = false;
    }
}

async function handleDeletePattern(id) {
    await deleteSavedPattern(id);
    await loadSavedPatterns();
}

function startRename(pattern) {
    editingId.value = pattern.id;
    editingName.value = pattern.name;
}

async function confirmRename(pattern) {
    if (!editingName.value.trim()) return;
    await updateSavedPattern(pattern.id, { name: editingName.value.trim() });
    editingId.value = null;
    await loadSavedPatterns();
}

function cancelRename() {
    editingId.value = null;
    editingName.value = "";
}
</script>

<template>
    <div class="config-card p-6 space-y-6">
        <h2 class="text-lg font-semibold text-primary-100">
            Pattern Configuration
        </h2>

        <!-- Tab Toggle -->
        <div class="toggle-group">
            <button
                :class="['toggle-btn', { active: mode === 'helper' }]"
                @click="mode = 'helper'"
            >
                Pattern Generator
            </button>
            <button
                :class="['toggle-btn', { active: mode === 'presets' }]"
                @click="mode = 'presets'"
            >
                Presets
            </button>
        </div>

        <!-- Pattern Generator Tab -->
        <div v-if="mode === 'helper'" class="space-y-4 animate-fade-in">
            <div>
                <label class="input-label">Example Values</label>
                <p class="helper-text mb-3">
                    Enter at least 2 examples of the text you want to find (more examples = better results)
                </p>
                <div class="space-y-2">
                    <div
                        v-for="(example, index) in examples"
                        :key="index"
                        class="flex gap-2"
                    >
                        <input
                            v-model="examples[index]"
                            type="text"
                            class="input-field flex-1"
                            :placeholder="`Example ${index + 1}: e.g., 10&quot;-FG-001`"
                            :disabled="disabled || isGenerating"
                        />
                        <button
                            v-if="examples.length > 2"
                            @click="removeExample(index)"
                            class="remove-btn"
                            :disabled="disabled || isGenerating"
                        >
                            ×
                        </button>
                    </div>
                    <button
                        @click="addExample"
                        class="add-btn"
                        :disabled="disabled || isGenerating"
                    >
                        +
                    </button>
                </div>
            </div>

            <button
                class="btn-accent w-full"
                :disabled="disabled || isGenerating || filledExamples.length < 2"
                @click="handleGeneratePattern"
            >
                {{ isGenerating ? "Generating..." : "Generate Pattern" }}
            </button>

            <div v-if="generateError" class="text-error-500 text-sm">
                {{ generateError }}
            </div>

            <!-- Generated Pattern Result -->
            <div v-if="suggestedPattern" class="suggested-card">
                <div>
                    <label class="badge-label">Generated Pattern</label>
                    <div class="flex items-center gap-2">
                        <template v-if="isEditingPattern">
                            <input
                                v-model="suggestedPattern"
                                type="text"
                                class="input-field flex-1 py-2 text-sm"
                                @keyup.enter="isEditingPattern = false"
                                @keyup.escape="isEditingPattern = false"
                                autofocus
                            />
                            <button class="action-btn confirm-btn" @click="isEditingPattern = false" title="Done">✓</button>
                        </template>
                        <template v-else>
                            <code class="pattern-display flex-1">{{ suggestedPattern }}</code>
                            <button
                                class="pencil-btn"
                                :disabled="disabled"
                                @click="isEditingPattern = true"
                                title="Edit pattern"
                            >
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                                </svg>
                            </button>
                        </template>
                    </div>
                </div>

                <div>
                    <label class="badge-label">Explanation</label>
                    <p class="text-primary-300 text-sm">{{ patternExplanation }}</p>
                </div>

                <div>
                    <label class="badge-label">Test Results</label>
                    <div class="flex flex-wrap gap-2">
                        <span
                            v-for="(matched, example) in testResults"
                            :key="example"
                            :class="['result-badge', matched ? 'badge-success' : 'badge-error']"
                        >
                            {{ example }}: {{ matched ? "✓" : "✗" }}
                        </span>
                    </div>
                </div>

                <!-- Save to Presets -->
                <div class="border-t border-white/5 pt-3">
                    <label class="badge-label">Save to Presets</label>
                    <div class="flex gap-2">
                        <input
                            v-model="savePatternName"
                            type="text"
                            class="input-field flex-1"
                            placeholder="Give it a name, e.g. Line Number"
                            :disabled="disabled || isSaving"
                            @keyup.enter="handleSavePattern"
                        />
                        <button
                            class="btn-save"
                            :disabled="disabled || isSaving || !savePatternName.trim()"
                            @click="handleSavePattern"
                        >
                            {{ isSaving ? "..." : "Save" }}
                        </button>
                    </div>
                </div>
            </div>

            <!-- File Identifier Pattern -->
            <div>
                <label class="input-label">
                    File Identifier Pattern
                    <span class="text-primary-500">(optional)</span>
                </label>
                <input
                    v-model="fileIdentifierRegex"
                    type="text"
                    class="input-field font-mono"
                    placeholder="e.g., ^(\d{4})_([^_]+)"
                    :disabled="disabled"
                />
                <p class="helper-text">Extract metadata from filenames (groups become columns)</p>
            </div>
        </div>

        <!-- Presets Tab -->
        <div v-else class="space-y-5 animate-fade-in">

            <!-- Active Pattern (shown after loading a preset) -->
            <div v-if="keywordRegex" class="active-pattern-section">
                <label class="badge-label">Active Pattern</label>
                <div class="flex items-center gap-2">
                    <template v-if="isEditingActivePattern">
                        <input
                            v-model="keywordRegex"
                            type="text"
                            class="input-field flex-1 py-2 text-sm"
                            @keyup.enter="isEditingActivePattern = false"
                            @keyup.escape="isEditingActivePattern = false"
                            autofocus
                        />
                        <button class="action-btn confirm-btn" @click="isEditingActivePattern = false" title="Done">✓</button>
                    </template>
                    <template v-else>
                        <code class="pattern-display flex-1">{{ keywordRegex }}</code>
                        <button
                            class="pencil-btn"
                            :disabled="disabled"
                            @click="isEditingActivePattern = true"
                            title="Edit pattern"
                        >
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                            </svg>
                        </button>
                    </template>
                </div>
                <!-- File Identifier Pattern for loaded preset -->
                <div class="mt-3">
                    <label class="input-label text-xs">
                        File Identifier Pattern
                        <span class="text-primary-500">(optional)</span>
                    </label>
                    <input
                        v-model="fileIdentifierRegex"
                        type="text"
                        class="input-field font-mono"
                        placeholder="e.g., ^(\d{4})_([^_]+)"
                        :disabled="disabled"
                    />
                </div>
            </div>

            <!-- Save Current Pattern -->
            <div class="save-section">
                <label class="badge-label">Save as Preset</label>
                <div v-if="activePatternPreview" class="mb-2">
                    <code class="pattern-display text-xs">{{ activePatternPreview }}</code>
                </div>
                <p v-else class="helper-text mb-2">
                    Generate a pattern in the Pattern Generator tab first
                </p>
                <div class="flex gap-2">
                    <input
                        v-model="savePatternName"
                        type="text"
                        class="input-field flex-1"
                        placeholder="e.g., P&ID Line Number"
                        :disabled="disabled || isSaving || !activePatternPreview"
                        @keyup.enter="handleSavePattern"
                    />
                    <button
                        class="btn-save"
                        :disabled="disabled || isSaving || !savePatternName.trim() || !activePatternPreview"
                        @click="handleSavePattern"
                    >
                        {{ isSaving ? "Saving..." : "Save" }}
                    </button>
                </div>
            </div>

            <!-- All Presets (built-in first, then user-saved) -->
            <div>
                <label class="badge-label">All Presets</label>
                <div v-if="savedPatterns.length === 0" class="empty-state">
                    No presets available.
                </div>
                <div v-else class="space-y-2">
                    <div
                        v-for="pattern in savedPatterns"
                        :key="pattern.id"
                        class="saved-pattern-row"
                    >
                        <!-- Rename mode -->
                        <template v-if="editingId === pattern.id">
                            <input
                                v-model="editingName"
                                type="text"
                                class="input-field flex-1 py-1.5 text-sm"
                                @keyup.enter="confirmRename(pattern)"
                                @keyup.escape="cancelRename"
                                autofocus
                            />
                            <button class="action-btn confirm-btn" @click="confirmRename(pattern)">✓</button>
                            <button class="action-btn cancel-btn" @click="cancelRename">✕</button>
                        </template>
                        <!-- View mode -->
                        <template v-else>
                            <button
                                class="saved-pattern-main"
                                :disabled="disabled"
                                @click="loadPreset(pattern)"
                            >
                                <div class="flex items-center gap-2">
                                    <span class="preset-name">{{ pattern.name }}</span>
                                    <span v-if="pattern.isBuiltIn" class="builtin-badge">built-in</span>
                                </div>
                                <code class="preset-pattern">{{ pattern.pattern }}</code>
                            </button>
                            <button
                                class="action-btn pencil-action-btn"
                                :disabled="disabled"
                                @click="startRename(pattern)"
                                title="Rename"
                            >
                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                                </svg>
                            </button>
                            <button
                                class="action-btn delete-btn"
                                :disabled="disabled"
                                @click="handleDeletePattern(pattern.id)"
                                title="Delete"
                            >
                                ×
                            </button>
                        </template>
                    </div>
                </div>
            </div>
        </div>

        <!-- Extract Button -->
        <button
            class="btn-primary w-full"
            :disabled="disabled || !isValid"
            @click="handleExtract"
        >
            <span class="flex items-center justify-center gap-2">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
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
    @apply flex bg-slate-800 rounded-lg p-1;
}

.toggle-btn {
    @apply flex-1 px-3 py-2 rounded-md font-medium transition-all duration-200 text-slate-400 text-sm;
}

.toggle-btn.active {
    @apply bg-indigo-600 text-white shadow-lg;
}

.input-label {
    @apply block text-sm font-medium text-slate-300 mb-2;
}

.input-field {
    @apply w-full px-4 py-3 rounded-lg bg-slate-800 border border-white/10 text-slate-100;
    @apply transition-all duration-200 focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/20;
    @apply placeholder:text-slate-500 disabled:opacity-50;
}

.input-field.font-mono {
    @apply font-mono;
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

/* Pencil inline-edit button */
.pencil-btn {
    @apply p-2 rounded-lg text-slate-500 hover:text-cyan-400 hover:bg-slate-700/60 transition-colors shrink-0 disabled:opacity-50;
}

/* Presets tab */
.active-pattern-section {
    @apply bg-indigo-500/10 border border-indigo-500/20 rounded-xl p-4;
}

.save-section {
    @apply bg-slate-800/60 rounded-xl p-4 border border-white/5;
}

.btn-save {
    @apply px-4 py-3 rounded-lg font-semibold text-white text-sm shrink-0;
    @apply bg-emerald-600 hover:bg-emerald-500 border border-white/10;
    @apply transition-colors disabled:opacity-50;
}

.preset-grid {
    @apply grid grid-cols-1 gap-2;
}

.preset-card {
    @apply flex flex-col gap-0.5 text-left px-3 py-2.5 rounded-lg border border-white/5;
    @apply bg-slate-800/60 hover:bg-slate-700/60 hover:border-indigo-500/40;
    @apply transition-all duration-150 disabled:opacity-50 cursor-pointer;
}

.preset-name {
    @apply text-sm font-medium text-slate-200;
}

.preset-pattern {
    @apply text-xs text-cyan-400 font-mono truncate;
}

.preset-desc {
    @apply text-xs text-slate-500;
}

.empty-state {
    @apply text-center text-slate-500 text-sm py-6 rounded-lg border border-dashed border-white/10;
}

.saved-pattern-row {
    @apply flex items-center gap-1 rounded-lg border border-white/5 bg-slate-800/40 overflow-hidden;
}

.saved-pattern-main {
    @apply flex flex-col gap-0.5 text-left px-3 py-2.5 flex-1 min-w-0;
    @apply hover:bg-slate-700/40 transition-colors disabled:opacity-50 cursor-pointer;
}

.action-btn {
    @apply px-2.5 py-2 text-sm font-medium shrink-0 transition-colors disabled:opacity-50;
}

.pencil-action-btn {
    @apply text-slate-500 hover:text-cyan-400 hover:bg-slate-700/60 rounded;
}

.builtin-badge {
    @apply text-[10px] px-1.5 py-0.5 rounded font-medium bg-indigo-500/15 text-indigo-400 border border-indigo-500/20;
}

.delete-btn {
    @apply text-red-500 hover:text-red-400 hover:bg-red-500/10 mr-1 rounded;
}

.confirm-btn {
    @apply text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10 rounded;
}

.cancel-btn {
    @apply text-slate-400 hover:text-slate-200 hover:bg-slate-700/50 mr-1 rounded;
}
</style>
