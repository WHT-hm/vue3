<template>
  <div class="monaco-wrapper">
    <div v-if="loading" class="monaco-loading">
      <el-icon class="is-loading" :size="24"><Loading /></el-icon>
      <span>编辑器加载中...</span>
    </div>
    <div ref="editorContainer" class="monaco-container" :style="{ height: height }"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import * as monaco from 'monaco-editor'
import editorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker'
import jsonWorker from 'monaco-editor/esm/vs/language/json/json.worker?worker'
import cssWorker from 'monaco-editor/esm/vs/language/css/css.worker?worker'
import htmlWorker from 'monaco-editor/esm/vs/language/html/html.worker?worker'
import tsWorker from 'monaco-editor/esm/vs/language/typescript/ts.worker?worker'

// 配置 Monaco Worker（Vite 兼容方式）
self.MonacoEnvironment = {
  getWorker(_, label) {
    if (label === 'json') return new jsonWorker()
    if (label === 'css' || label === 'scss' || label === 'less') return new cssWorker()
    if (label === 'html' || label === 'handlebars' || label === 'razor') return new htmlWorker()
    if (label === 'typescript' || label === 'javascript') return new tsWorker()
    return new editorWorker()
  }
}

const props = defineProps({
  modelValue: { type: String, default: '' },
  language: { type: String, default: 'python' },
  theme: { type: String, default: 'vs-dark' },
  height: { type: String, default: '400px' },
  options: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['update:modelValue'])
const loading = ref(true)
const editorContainer = ref(null)
let editor = null
let isUpdating = false

onMounted(() => {
  nextTick(() => {
    if (!editorContainer.value) return

    editor = monaco.editor.create(editorContainer.value, {
      value: props.modelValue || '',
      language: props.language,
      theme: props.theme,
      automaticLayout: true,
      minimap: { enabled: true },
      fontSize: 14,
      lineNumbers: 'on',
      scrollBeyondLastLine: false,
      wordWrap: 'on',
      tabSize: 4,
      ...props.options,
    })

    editor.onDidChangeModelContent(() => {
      if (!isUpdating) {
        const value = editor.getValue()
        emit('update:modelValue', value)
      }
    })

    loading.value = false
  })
})

// 监听外部 modelValue 变化
watch(() => props.modelValue, (newVal) => {
  if (editor && !isUpdating) {
    isUpdating = true
    const currentValue = editor.getValue()
    if (newVal !== currentValue) {
      editor.setValue(newVal || '')
    }
    nextTick(() => { isUpdating = false })
  }
})

// 监听语言变化
watch(() => props.language, (newLang) => {
  if (editor) {
    const model = editor.getModel()
    if (model) {
      monaco.editor.setModelLanguage(model, newLang)
    }
  }
})

// 监听主题变化
watch(() => props.theme, (newTheme) => {
  if (editor) {
    monaco.editor.setTheme(newTheme)
  }
})

onBeforeUnmount(() => {
  if (editor) {
    editor.dispose()
    editor = null
  }
})
</script>

<style scoped>
.monaco-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
}

.monaco-container {
  width: 100%;
  min-height: 400px;
}

.monaco-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: #1e1e1e;
  color: #888;
  z-index: 10;
  font-size: 14px;
}
</style>
