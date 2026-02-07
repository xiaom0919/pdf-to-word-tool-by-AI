<script setup>
import { ref } from 'vue'
import axios from 'axios'

const props = defineProps({
  conversionResult: {
    type: Object,
    default: null
  },
  wordTranslationResult: {
    type: Object,
    default: null
  },
  pdfTranslationResult: {
    type: Object,
    default: null
  },
  file: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['translate-word'])

const isTranslatingWord = ref(false)
const targetLanguage = ref('中文')

const getApiKey = () => {
  return localStorage.getItem('zhipuai_api_key') || ''
}

const downloadFile = () => {
  if (props.conversionResult) {
    const { downloadUrl, filename } = props.conversionResult
    window.location.href = `${downloadUrl}?name=${encodeURIComponent(filename)}`
  }
}

const translateWordFile = async () => {
  if (!props.conversionResult) {
    return
  }

  const apiKey = getApiKey()
  if (!apiKey) {
    alert('请先配置 API Key')
    return
  }

  isTranslatingWord.value = true

  try {
    const formData = new FormData()
    formData.append('file', props.file)
    formData.append('target_lang', targetLanguage.value)
    formData.append('api_key', apiKey)

    const response = await axios.post('/api/translate-word', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.success) {
      emit('translate-word', response.data)
    }
  } catch (error) {
    alert('翻译 Word 文档失败: ' + (error.response?.data?.error || error.message))
  } finally {
    isTranslatingWord.value = false
  }
}

const downloadTranslatedWord = () => {
  if (props.wordTranslationResult) {
    const { downloadUrl, filename } = props.wordTranslationResult
    window.location.href = `${downloadUrl}?name=${encodeURIComponent(filename)}`
  }
}

const downloadTranslatedPdf = () => {
  if (props.pdfTranslationResult) {
    const { downloadUrl, filename } = props.pdfTranslationResult
    window.location.href = `${downloadUrl}?name=${encodeURIComponent(filename)}`
  }
}
</script>

<template>
  <div v-if="conversionResult" class="success-section">
    <div class="success-icon-wrapper">
      <div class="success-icon">✓</div>
      <div class="success-icon-bg"></div>
    </div>
    <div class="success-text">转换成功！</div>
    <div class="download-actions">
      <button @click="downloadFile" class="download-button primary">
        <span class="button-icon">📥</span>
        <span>下载原 Word 文件</span>
      </button>
      <button
        v-if="aiEnabled"
        @click="translateWordFile"
        :disabled="isTranslatingWord"
        class="download-button secondary"
      >
        <span v-if="isTranslatingWord" class="button-content">
          <span class="loading-spinner"></span>
          <span>翻译中...</span>
        </span>
        <span v-else class="button-content">
          <span class="button-icon">🌐</span>
          <span>翻译成{{ targetLanguage }}</span>
        </span>
      </button>
    </div>
  </div>

  <div v-if="wordTranslationResult" class="success-section translation-success">
    <div class="success-icon-wrapper">
      <div class="success-icon">🌐</div>
      <div class="success-icon-bg"></div>
    </div>
    <div class="success-text">翻译成功！</div>
    <button @click="downloadTranslatedWord" class="download-button primary">
      <span class="button-icon">📥</span>
      <span>下载翻译后的 Word 文件</span>
    </button>
  </div>

  <div v-if="pdfTranslationResult" class="success-section pdf-translation-success">
    <div class="success-icon-wrapper">
      <div class="success-icon">🚀</div>
      <div class="success-icon-bg"></div>
    </div>
    <div class="success-text">PDF 转换翻译成功！</div>
    <button @click="downloadTranslatedPdf" class="download-button primary">
      <span class="button-icon">📥</span>
      <span>下载翻译后的 Word 文件</span>
    </button>
  </div>
</template>

<style scoped>
.success-section {
  margin-top: 32px;
  padding: 32px;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 16px;
  text-align: center;
  animation: slideIn 0.5s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.success-icon-wrapper {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.success-icon {
  font-size: 48px;
  color: #22c55e;
  z-index: 1;
  animation: successPulse 2s ease-in-out infinite;
}

@keyframes successPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.success-icon-bg {
  position: absolute;
  width: 100%;
  height: 100%;
  background: rgba(34, 197, 94, 0.2);
  border-radius: 50%;
  filter: blur(20px);
  animation: successBgPulse 2s ease-in-out infinite;
}

@keyframes successBgPulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.2); opacity: 0.8; }
}

.success-text {
  font-size: 20px;
  font-weight: 600;
  color: #22c55e;
  margin-bottom: 24px;
}

.download-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.download-button {
  padding: 14px 28px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.download-button.primary {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: #ffffff;
  box-shadow: 0 4px 15px rgba(34, 197, 94, 0.4);
}

.download-button.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(34, 197, 94, 0.6);
}

.download-button.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.download-button.secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(102, 126, 234, 0.5);
}

.download-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.button-icon {
  font-size: 18px;
}

.button-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.translation-success {
  background: rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.3);
}

.translation-success .success-icon {
  color: #667eea;
}

.translation-success .success-icon-bg {
  background: rgba(102, 126, 234, 0.2);
}

.translation-success .success-text {
  color: #667eea;
}

.pdf-translation-success {
  background: rgba(240, 147, 251, 0.1);
  border-color: rgba(240, 147, 251, 0.3);
}

.pdf-translation-success .success-icon {
  color: #f093fb;
}

.pdf-translation-success .success-icon-bg {
  background: rgba(240, 147, 251, 0.2);
}

.pdf-translation-success .success-text {
  color: #f093fb;
}
</style>
