<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import DynamicBackground from './components/DynamicBackground.vue'
import FileUpload from './components/FileUpload.vue'
import ConversionResult from './components/ConversionResult.vue'
import AIPanel from './components/AIPanel.vue'
import Features from './components/Features.vue'

const file = ref(null)
const isConverting = ref(false)
const conversionResult = ref(null)
const errorMessage = ref('')

const aiEnabled = ref(false)
const aiStatus = ref(null)
const showAIPanel = ref(false)

const pdfText = ref('')
const aiLoading = ref(false)

const wordTranslationResult = ref(null)
const pdfTranslationResult = ref(null)

const getApiKey = () => {
  return localStorage.getItem('zhipuai_api_key') || ''
}

const checkAIStatus = () => {
  const apiKey = getApiKey()
  aiEnabled.value = apiKey && apiKey !== 'your_api_key_here'
  aiStatus.value = {
    enabled: aiEnabled.value,
    features: {
      summary: true,
      translate: true,
      chat: true
    }
  }
}

const extractPdfText = async (selectedFile) => {
  if (!selectedFile) {
    errorMessage.value = '请先选择 PDF 文件'
    return
  }

  const apiKey = getApiKey()
  if (!apiKey) {
    errorMessage.value = '请先在 AI 智能助手中配置 API Key'
    return
  }

  aiLoading.value = true

  try {
    const formData = new FormData()
    formData.append('file', selectedFile)

    const response = await axios.post('/api/extract-text', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.success) {
      pdfText.value = response.data.text
      showAIPanel.value = true
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.error || '提取文本失败'
  } finally {
    aiLoading.value = false
  }
}

const handleFileSelected = (selectedFile) => {
  file.value = selectedFile
  errorMessage.value = ''
  conversionResult.value = null
  wordTranslationResult.value = null
  pdfTranslationResult.value = null
}

const handleConvert = (result) => {
  conversionResult.value = result
}

const handleExtractPdfText = (selectedFile) => {
  extractPdfText(selectedFile)
}

const handleTranslatePdf = (result) => {
  pdfTranslationResult.value = result
}

const handleTranslateWord = (result) => {
  wordTranslationResult.value = result
}

const handleCloseAIPanel = () => {
  showAIPanel.value = false
}

onMounted(() => {
  checkAIStatus()
})
</script>

<template>
  <div class="container">
    <DynamicBackground />
    
    <div class="header">
      <div class="header-content">
        <h1 class="title">
          <span class="title-icon">📄</span>
          PDF 转 Word 工具
        </h1>
        <p class="subtitle">简单快速 · 智能转换 · 格式保留</p>
        <button @click="showAIPanel = true" class="ai-assistant-button">
          <span class="ai-assistant-icon">🤖</span>
          <span class="ai-assistant-text">AI 智能助手</span>
        </button>
      </div>
    </div>

    <FileUpload
      @file-selected="handleFileSelected"
      @convert="handleConvert"
      @extract-pdf-text="handleExtractPdfText"
      @translate-pdf="handleTranslatePdf"
    />

    <div class="result-section">
      <ConversionResult
        :conversion-result="conversionResult"
        :word-translation-result="wordTranslationResult"
        :pdf-translation-result="pdfTranslationResult"
        :file="file"
        @translate-word="handleTranslateWord"
      />
    </div>

    <AIPanel
      :show="showAIPanel"
      :pdf-text="pdfText"
      @close="handleCloseAIPanel"
    />

    <Features />

    <div class="footer">
      <p>© 2024 PDF 转 Word 工具 · 基于 pdf2docx 和 AI 技术</p>
    </div>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  min-height: 100vh;
  color: #ffffff;
}

.container {
  position: relative;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  z-index: 1;
}

.header {
  text-align: center;
  padding: 3rem 1rem 2rem;
  position: relative;
  z-index: 1;
}

.header-content {
  animation: fadeInDown 1s ease;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.title {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.title-icon {
  font-size: 3.5rem;
  -webkit-text-fill-color: initial;
  animation: titleIconFloat 3s ease-in-out infinite;
}

@keyframes titleIconFloat {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-10px) rotate(5deg); }
}

.subtitle {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 400;
  letter-spacing: 0.5px;
}

.ai-assistant-button {
  margin-top: 1.5rem;
  padding: 12px 24px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  border: 1px solid rgba(102, 126, 234, 0.5);
  border-radius: 12px;
  color: #667eea;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.ai-assistant-button:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
  border-color: rgba(102, 126, 234, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.ai-assistant-icon {
  font-size: 1.2rem;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

.ai-assistant-text {
  font-size: 0.95rem;
}

.result-section {
  max-width: 600px;
  margin: 0 auto;
  padding: 0 20px;
  position: relative;
  z-index: 1;
}

.footer {
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 4rem;
  padding: 2rem;
  font-size: 0.9rem;
  position: relative;
  z-index: 1;
}

@media (max-width: 768px) {
  .title {
    font-size: 2.5rem;
  }

  .title-icon {
    font-size: 3rem;
  }

  .subtitle {
    font-size: 1.1rem;
  }
}

@media (max-width: 480px) {
  .title {
    font-size: 2rem;
  }

  .title-icon {
    font-size: 2.5rem;
  }
}
</style>
