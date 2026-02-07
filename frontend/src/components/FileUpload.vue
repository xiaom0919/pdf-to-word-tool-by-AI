<script setup>
import { ref } from 'vue'
import axios from 'axios'

const props = defineProps({
  aiEnabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['file-selected', 'convert', 'extract-pdf-text', 'translate-pdf'])

const file = ref(null)
const isConverting = ref(false)
const errorMessage = ref('')
const targetLanguage = ref('中文')
const isTranslatingPdf = ref(false)

const getApiKey = () => {
  return localStorage.getItem('zhipuai_api_key') || ''
}

const handleFileChange = (event) => {
  file.value = event.target.files[0]
  errorMessage.value = ''
  emit('file-selected', file.value)
}

const convertPdf = async () => {
  if (!file.value) {
    errorMessage.value = '请选择一个 PDF 文件'
    return
  }

  if (!file.value.name.toLowerCase().endsWith('.pdf')) {
    errorMessage.value = '请选择 PDF 格式的文件'
    return
  }

  isConverting.value = true
  errorMessage.value = ''

  const formData = new FormData()
  formData.append('file', file.value)

  try {
    const response = await axios.post('/api/convert', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.success) {
      emit('convert', response.data)
    } else {
      errorMessage.value = response.data.error || '转换失败'
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.error || '转换过程中发生错误'
  } finally {
    isConverting.value = false
  }
}

const extractPdfText = () => {
  if (!file.value) {
    errorMessage.value = '请先选择 PDF 文件'
    return
  }

  if (!props.aiEnabled) {
    errorMessage.value = 'AI 功能未启用，请先配置 API Key（参考 README.md）'
    return
  }

  emit('extract-pdf-text', file.value)
}

const translatePdfDirectly = async () => {
  if (!file.value) {
    errorMessage.value = '请先选择 PDF 文件'
    return
  }

  const apiKey = getApiKey()
  if (!apiKey) {
    errorMessage.value = '请先配置 API Key'
    return
  }

  isTranslatingPdf.value = true
  errorMessage.value = ''

  try {
    const formData = new FormData()
    formData.append('file', file.value)
    formData.append('target_lang', targetLanguage.value)
    formData.append('api_key', apiKey)

    const response = await axios.post('/api/translate-pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.success) {
      emit('translate-pdf', response.data)
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.error || '转换翻译失败'
  } finally {
    isTranslatingPdf.value = false
  }
}
</script>

<template>
  <div class="upload-section">
    <div class="upload-card">
      <div class="upload-area" :class="{ 'drag-over': false, 'has-file': file }">
        <input
          type="file"
          id="file-input"
          accept=".pdf"
          @change="handleFileChange"
          class="file-input"
        />
        <label for="file-input" class="upload-label">
          <div class="upload-icon-wrapper">
            <div class="upload-icon">📄</div>
            <div class="upload-icon-bg"></div>
          </div>
          <div class="upload-text">
            <span v-if="file" class="file-name">{{ file.name }}</span>
            <span v-else class="upload-placeholder">
              <span class="upload-main-text">点击或拖拽上传</span>
              <span class="upload-sub-text">支持 PDF 格式文件</span>
            </span>
          </div>
        </label>
      </div>

      <div class="action-buttons">
        <button
          @click="convertPdf"
          :disabled="!file || isConverting"
          class="convert-button"
          :class="{ 'converting': isConverting }"
        >
          <span v-if="isConverting" class="button-content">
            <span class="loading-spinner"></span>
            <span>转换中...</span>
          </span>
          <span v-else class="button-content">
            <span class="button-icon">⚡</span>
            <span>开始转换</span>
          </span>
        </button>

        <button
          v-if="file && aiEnabled"
          @click="extractPdfText"
          class="ai-button"
        >
          <span class="button-content">
            <span class="button-icon">🤖</span>
            <span>AI 助手</span>
          </span>
        </button>
      </div>

      <div v-if="file && aiEnabled" class="language-selector-section">
        <div class="language-selector-wrapper">
          <label class="language-label">
            <span class="label-icon">🌐</span>
            <span>目标语言</span>
          </label>
          <select v-model="targetLanguage" class="language-select" :disabled="isTranslatingPdf">
            <option value="中文">中文</option>
            <option value="英文">英文</option>
            <option value="日文">日文</option>
            <option value="韩文">韩文</option>
            <option value="法文">法文</option>
            <option value="德文">德文</option>
            <option value="西班牙文">西班牙文</option>
            <option value="俄文">俄文</option>
            <option value="阿拉伯文">阿拉伯文</option>
          </select>
        </div>
        <button
          @click="translatePdfDirectly"
          :disabled="isTranslatingPdf"
          class="translate-pdf-button"
        >
          <span v-if="isTranslatingPdf" class="button-content">
            <span class="loading-spinner"></span>
            <span>转换翻译中...</span>
          </span>
          <span v-else class="button-content">
            <span class="button-icon">🚀</span>
            <span>PDF 转翻译 Word</span>
          </span>
        </button>
      </div>

      <div v-if="errorMessage" class="error-message">
        <span class="error-icon">⚠️</span>
        <span>{{ errorMessage }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.upload-section {
  max-width: 600px;
  margin: 0 auto;
  padding: 0 20px;
}

.upload-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.upload-area {
  position: relative;
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 60px 40px;
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.02);
}

.upload-area:hover {
  border-color: rgba(102, 126, 234, 0.5);
  background: rgba(102, 126, 234, 0.05);
}

.upload-area.has-file {
  border-color: rgba(102, 126, 234, 0.5);
  background: rgba(102, 126, 234, 0.05);
}

.file-input {
  display: none;
}

.upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  cursor: pointer;
}

.upload-icon-wrapper {
  position: relative;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-icon {
  font-size: 48px;
  z-index: 1;
  animation: iconFloat 3s ease-in-out infinite;
}

@keyframes iconFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.upload-icon-bg {
  position: absolute;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3));
  border-radius: 50%;
  filter: blur(20px);
  animation: iconPulse 2s ease-in-out infinite;
}

@keyframes iconPulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 0.8; }
}

.upload-text {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-name {
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
  word-break: break-all;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.upload-main-text {
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
}

.upload-sub-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

.action-buttons {
  display: flex;
  gap: 16px;
  margin-top: 32px;
}

.convert-button,
.ai-button {
  flex: 1;
  padding: 16px 32px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.convert-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.convert-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.convert-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.convert-button.converting {
  animation: buttonPulse 1.5s ease-in-out infinite;
}

@keyframes buttonPulse {
  0%, 100% { box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); }
  50% { box-shadow: 0 4px 25px rgba(102, 126, 234, 0.8); }
}

.ai-button {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: #ffffff;
  box-shadow: 0 4px 15px rgba(240, 147, 251, 0.4);
}

.ai-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(240, 147, 251, 0.6);
}

.button-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.button-icon {
  font-size: 20px;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.language-selector-section {
  margin-top: 24px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.language-selector-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.language-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  white-space: nowrap;
}

.label-icon {
  font-size: 18px;
}

.language-select {
  flex: 1;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #ffffff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  outline: none;
}

.language-select:hover {
  border-color: rgba(102, 126, 234, 0.5);
}

.language-select:focus {
  border-color: rgba(102, 126, 234, 0.8);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

.language-select option {
  background: #1a1a2e;
  color: #ffffff;
}

.translate-pdf-button {
  width: 100%;
  padding: 14px 24px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.translate-pdf-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.translate-pdf-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-message {
  margin-top: 24px;
  padding: 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: #fca5a5;
  font-size: 14px;
}

.error-icon {
  font-size: 20px;
}
</style>
