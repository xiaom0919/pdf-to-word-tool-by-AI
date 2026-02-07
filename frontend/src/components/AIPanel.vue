<script setup>
import { ref, nextTick, watch, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  pdfText: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close'])

const aiTab = ref('summary')
const aiLoading = ref(false)
const aiResult = ref('')
const targetLanguage = ref('中文')

const chatMessages = ref([])
const chatInput = ref('')
const chatContainer = ref(null)

const showApiKeyInput = ref(false)
const apiKey = ref('')
const apiKeyError = ref('')
const testingApiKey = ref(false)
const testResult = ref(null)

onMounted(() => {
  const savedApiKey = localStorage.getItem('zhipuai_api_key')
  if (savedApiKey) {
    apiKey.value = savedApiKey
  } else {
    showApiKeyInput.value = true
  }
})

const testApiKeyConnection = async () => {
  if (!apiKey.value.trim()) {
    apiKeyError.value = '请输入 API Key'
    return
  }
  
  testingApiKey.value = true
  testResult.value = null
  
  try {
    const response = await axios.post('/api/ai/test-key', {
      api_key: apiKey.value.trim()
    })
    
    if (response.data.success) {
      testResult.value = {
        success: true,
        message: '配置成功！API Key 有效'
      }
    } else {
      testResult.value = {
        success: false,
        message: 'API Key 似乎无效'
      }
    }
  } catch (error) {
    testResult.value = {
      success: false,
      message: 'API Key 似乎无效'
    }
  } finally {
    testingApiKey.value = false
  }
}

const saveApiKey = () => {
  if (!apiKey.value.trim()) {
    apiKeyError.value = '请输入 API Key'
    return
  }
  
  localStorage.setItem('zhipuai_api_key', apiKey.value.trim())
  showApiKeyInput.value = false
  apiKeyError.value = ''
  testResult.value = null
}

const clearApiKey = () => {
  localStorage.removeItem('zhipuai_api_key')
  apiKey.value = ''
  showApiKeyInput.value = true
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const generateSummary = async () => {
  if (!props.pdfText) return

  aiLoading.value = true
  aiResult.value = ''

  try {
    const response = await axios.post('/api/ai/summary', {
      text: props.pdfText,
      api_key: apiKey.value
    })

    if (response.data.success) {
      aiResult.value = response.data.summary
    }
  } catch (error) {
    aiResult.value = '摘要生成失败: ' + (error.response?.data?.error || error.message)
  } finally {
    aiLoading.value = false
  }
}

const translateText = async () => {
  if (!props.pdfText) return

  aiLoading.value = true
  aiResult.value = ''

  try {
    const response = await axios.post('/api/ai/translate', {
      text: props.pdfText,
      target_lang: targetLanguage.value,
      api_key: apiKey.value
    })

    if (response.data.success) {
      aiResult.value = response.data.translation
    }
  } catch (error) {
    aiResult.value = '翻译失败: ' + (error.response?.data?.error || error.message)
  } finally {
    aiLoading.value = false
  }
}

const sendMessage = async () => {
  const message = chatInput.value.trim()
  if (!message || !props.pdfText) return

  chatMessages.value.push({
    id: Date.now(),
    role: 'user',
    content: message,
    timestamp: new Date().toLocaleTimeString()
  })

  chatInput.value = ''
  aiLoading.value = true

  await scrollToBottom()

  const assistantMessageId = Date.now() + 1
  chatMessages.value.push({
    id: assistantMessageId,
    role: 'assistant',
    content: '',
    timestamp: new Date().toLocaleTimeString()
  })

  await scrollToBottom()

  try {
    const response = await fetch('/api/ai/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        question: message,
        context: props.pdfText,
        api_key: apiKey.value
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            
            if (data.error) {
              const assistantMessage = chatMessages.value.find(m => m.id === assistantMessageId)
              if (assistantMessage) {
                assistantMessage.role = 'error'
                assistantMessage.content = data.error
              }
              break
            }
            
            if (data.content) {
              const assistantMessage = chatMessages.value.find(m => m.id === assistantMessageId)
              if (assistantMessage) {
                assistantMessage.content += data.content
                await scrollToBottom()
              }
            }
            
            if (data.done) {
              break
            }
          } catch (e) {
            console.error('Failed to parse SSE data:', e)
          }
        }
      }
    }
  } catch (error) {
    const assistantMessage = chatMessages.value.find(m => m.id === assistantMessageId)
    if (assistantMessage) {
      assistantMessage.role = 'error'
      assistantMessage.content = '问答失败: ' + error.message
    }
  } finally {
    aiLoading.value = false
    await scrollToBottom()
  }
}

const handleKeyPress = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

watch(() => props.show, (newVal) => {
  if (newVal && aiTab.value === 'chat') {
    scrollToBottom()
  }
})
</script>

<template>
  <Transition name="panel">
    <div v-if="show" class="ai-panel">
      <div class="ai-header">
        <h2 class="ai-title">
          <span class="ai-title-icon">🤖</span>
          AI 智能助手
        </h2>
        <button @click="emit('close')" class="close-button">
          <span class="close-icon">✕</span>
        </button>
      </div>

      <div class="ai-tabs">
        <button
          @click="aiTab = 'summary'"
          :class="{ 'active': aiTab === 'summary' }"
          class="ai-tab"
        >
          <span class="tab-icon">📝</span>
          <span>文档摘要</span>
        </button>
        <button
          @click="aiTab = 'translate'"
          :class="{ 'active': aiTab === 'translate' }"
          class="ai-tab"
        >
          <span class="tab-icon">🌐</span>
          <span>翻译</span>
        </button>
        <button
          @click="aiTab = 'chat'"
          :class="{ 'active': aiTab === 'chat' }"
          class="ai-tab"
        >
          <span class="tab-icon">💬</span>
          <span>问答</span>
        </button>
      </div>

      <div v-if="showApiKeyInput" class="api-key-section">
        <div class="api-key-content">
          <div class="api-key-header">
            <span class="api-key-icon">🔑</span>
            <h3 class="api-key-title">输入 API Key</h3>
          </div>
          <p class="api-key-desc">请输入您的智谱 AI API Key 以使用 AI 功能</p>
          <div class="api-key-input-container">
            <input
              v-model="apiKey"
              type="password"
              placeholder="请输入 API Key"
              class="api-key-input"
              @keyup.enter="testApiKeyConnection"
            />
            <button @click="testApiKeyConnection" :disabled="testingApiKey" class="test-button">
              <span v-if="testingApiKey" class="loading-spinner"></span>
              <span v-else>测试</span>
            </button>
            <button @click="saveApiKey" :disabled="!testResult || !testResult.success" class="api-key-button">
              <span class="api-key-button-icon">✓</span>
            </button>
          </div>
          <p v-if="apiKeyError" class="api-key-error">{{ apiKeyError }}</p>
          <div v-if="testResult" :class="['test-result', testResult.success ? 'success' : 'error']">
            <span class="test-result-icon">{{ testResult.success ? '✓' : '✕' }}</span>
            <span class="test-result-message">{{ testResult.message }}</span>
          </div>
          <div class="api-key-hint">
            <p class="hint-text">💡 获取 API Key：</p>
            <a href="https://open.bigmodel.cn/usercenter/apikeys" target="_blank" class="hint-link">https://open.bigmodel.cn/usercenter/apikeys</a>
          </div>
        </div>
      </div>

      <div v-else class="ai-content">
        <div class="api-key-status">
          <span class="status-icon">✓</span>
          <span class="status-text">API Key 已配置</span>
          <button @click="clearApiKey" class="clear-key-button">清除</button>
        </div>

        <div v-if="aiTab === 'summary'" class="ai-section">
          <div class="ai-section-header">
            <h3 class="ai-section-title">文档摘要</h3>
            <p class="ai-desc">为您的 PDF 文档生成智能摘要</p>
          </div>
          <button
            @click="generateSummary"
            :disabled="aiLoading"
            class="ai-action-button"
          >
            <span v-if="aiLoading" class="button-content">
              <span class="loading-spinner"></span>
              <span>生成中...</span>
            </span>
            <span v-else class="button-content">
              <span class="button-icon">✨</span>
              <span>生成摘要</span>
            </span>
          </button>
          <div v-if="aiResult" class="ai-result">
            <div class="result-header">
              <h3 class="result-title">摘要结果</h3>
            </div>
            <div class="result-content">{{ aiResult }}</div>
          </div>
        </div>

        <div v-if="aiTab === 'translate'" class="ai-section">
          <div class="ai-section-header">
            <h3 class="ai-section-title">文档翻译</h3>
            <p class="ai-desc">将文档内容翻译成目标语言</p>
          </div>
          <div class="language-selector">
            <label class="language-label">
              <span class="label-icon">🌐</span>
              <span>目标语言</span>
            </label>
            <select v-model="targetLanguage" class="language-select" :disabled="aiLoading">
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
            @click="translateText"
            :disabled="aiLoading"
            class="ai-action-button"
          >
            <span v-if="aiLoading" class="button-content">
              <span class="loading-spinner"></span>
              <span>翻译中...</span>
            </span>
            <span v-else class="button-content">
              <span class="button-icon">🌐</span>
              <span>翻译成{{ targetLanguage }}</span>
            </span>
          </button>
          <div v-if="aiResult" class="ai-result">
            <div class="result-header">
              <h3 class="result-title">翻译结果</h3>
            </div>
            <div class="result-content">{{ aiResult }}</div>
          </div>
        </div>

        <div v-if="aiTab === 'chat'" class="chat-section">
          <div class="chat-header">
            <h3 class="chat-title">智能问答</h3>
            <p class="chat-desc">基于文档内容进行智能问答</p>
          </div>
          
          <div class="chat-messages" ref="chatContainer">
            <div v-if="chatMessages.length === 0" class="chat-empty">
              <div class="empty-icon">💬</div>
              <p class="empty-text">开始提问吧！</p>
              <p class="empty-hint">您可以询问关于文档内容的任何问题</p>
            </div>
            
            <div
              v-for="message in chatMessages"
              :key="message.id"
              :class="['chat-message', `message-${message.role}`]"
            >
              <div class="message-avatar">
                <span v-if="message.role === 'user'" class="avatar-icon">👤</span>
                <span v-else-if="message.role === 'assistant'" class="avatar-icon">🤖</span>
                <span v-else class="avatar-icon">⚠️</span>
              </div>
              <div class="message-content">
                <div v-if="message.content" class="message-text">{{ message.content }}</div>
                <div v-else class="typing-indicator">
                  <span class="typing-dot"></span>
                  <span class="typing-dot"></span>
                  <span class="typing-dot"></span>
                </div>
                <div v-if="message.content" class="message-time">{{ message.timestamp }}</div>
              </div>
            </div>
          </div>
          
          <div class="chat-input-container">
            <textarea
              v-model="chatInput"
              @keydown="handleKeyPress"
              placeholder="输入您的问题... (Enter 发送，Shift+Enter 换行)"
              class="chat-input"
              rows="1"
              :disabled="aiLoading"
            ></textarea>
            <button
              @click="sendMessage"
              :disabled="!chatInput.trim() || aiLoading"
              class="send-button"
            >
              <span v-if="aiLoading" class="loading-spinner"></span>
              <span v-else class="send-icon">➤</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.panel-enter-active,
.panel-leave-active {
  transition: all 0.3s ease;
}

.panel-enter-from,
.panel-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.ai-panel {
  position: fixed;
  top: 0;
  right: 0;
  width: 500px;
  height: 100%;
  background: rgba(26, 26, 46, 0.95);
  backdrop-filter: blur(20px);
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: -8px 0 32px rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.ai-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.ai-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
}

.ai-title-icon {
  font-size: 24px;
}

.close-button {
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.close-button:hover {
  background: rgba(239, 68, 68, 0.2);
}

.close-icon {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.8);
}

.ai-tabs {
  display: flex;
  padding: 16px 24px;
  gap: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.ai-tab {
  flex: 1;
  padding: 12px 16px;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.6);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
}

.ai-tab:hover {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.8);
}

.ai-tab.active {
  background: rgba(102, 126, 234, 0.2);
  color: #667eea;
}

.tab-icon {
  font-size: 16px;
}

.api-key-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.api-key-content {
  width: 100%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  text-align: center;
}

.api-key-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.api-key-icon {
  font-size: 48px;
}

.api-key-title {
  font-size: 24px;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
}

.api-key-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
  line-height: 1.6;
}

.api-key-input-container {
  display: flex;
  gap: 8px;
}

.api-key-input {
  flex: 1;
  padding: 14px 18px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  color: #ffffff;
  font-size: 14px;
  outline: none;
  transition: all 0.3s ease;
}

.api-key-input:focus {
  border-color: rgba(102, 126, 234, 0.8);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

.api-key-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.test-button {
  width: 80px;
  height: 50px;
  border: none;
  background: rgba(102, 126, 234, 0.2);
  border: 1px solid rgba(102, 126, 234, 0.5);
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  color: #667eea;
  font-size: 14px;
  font-weight: 500;
}

.test-button:hover:not(:disabled) {
  background: rgba(102, 126, 234, 0.3);
  border-color: rgba(102, 126, 234, 0.8);
  transform: translateY(-2px);
}

.test-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.api-key-button {
  width: 50px;
  height: 50px;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.api-key-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.api-key-button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
  box-shadow: none;
}

.api-key-button-icon {
  font-size: 24px;
  color: #ffffff;
}

.api-key-error {
  color: #fca5a5;
  font-size: 14px;
  margin: 0;
}

.test-result {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.test-result.success {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
  color: #22c55e;
}

.test-result.error {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
}

.test-result-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.test-result-message {
  flex: 1;
}

.api-key-hint {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.hint-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.hint-link {
  font-size: 13px;
  color: #667eea;
  text-decoration: none;
  word-break: break-all;
}

.hint-link:hover {
  text-decoration: underline;
}

.api-key-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 8px;
  margin-bottom: 20px;
}

.status-icon {
  font-size: 16px;
  color: #22c55e;
}

.status-text {
  flex: 1;
  font-size: 14px;
  color: #22c55e;
  font-weight: 500;
}

.clear-key-button {
  padding: 6px 12px;
  border: none;
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.clear-key-button:hover {
  background: rgba(239, 68, 68, 0.2);
}

.ai-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.ai-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.ai-section-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ai-section-title {
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
}

.ai-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.language-selector {
  display: flex;
  align-items: center;
  gap: 16px;
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

.ai-action-button {
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

.ai-action-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.ai-action-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.button-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.button-icon {
  font-size: 18px;
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

.ai-result {
  margin-top: 20px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.result-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.result-title {
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
}

.result-content {
  font-size: 14px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.8);
  white-space: pre-wrap;
  word-wrap: break-word;
}

.chat-section {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 16px;
}

.chat-header {
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.chat-title {
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
  margin: 0 0 8px 0;
}

.chat-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  scroll-behavior: smooth;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.5);
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.7);
}

.chat-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: rgba(255, 255, 255, 0.5);
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-text {
  font-size: 18px;
  font-weight: 500;
  margin: 0 0 8px 0;
}

.empty-hint {
  font-size: 14px;
  margin: 0;
}

.chat-message {
  display: flex;
  gap: 12px;
  animation: messageSlideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  max-width: 100%;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.message-avatar {
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  transition: transform 0.3s ease;
}

.message-avatar:hover {
  transform: scale(1.1);
}

.message-user .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.message-assistant .message-avatar {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  box-shadow: 0 4px 12px rgba(240, 147, 251, 0.4);
}

.message-error .message-avatar {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}

.message-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message-text {
  padding: 14px 18px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.7;
  word-wrap: break-word;
  position: relative;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message-user .message-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  border-bottom-right-radius: 4px;
  margin-left: auto;
  max-width: 80%;
}

.message-assistant .message-text {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.95);
  border-bottom-left-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  max-width: 90%;
}

.message-error .message-text {
  background: rgba(239, 68, 68, 0.15);
  color: #fca5a5;
  border-bottom-left-radius: 4px;
  border: 1px solid rgba(239, 68, 68, 0.3);
  max-width: 90%;
}

.message-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 4px;
}

.message-user .message-time {
  text-align: right;
}

.typing-indicator {
  display: flex;
  gap: 6px;
  padding: 14px 18px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  border-bottom-left-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.typing-dot {
  width: 10px;
  height: 10px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 50%;
  animation: typingBounce 1.4s ease-in-out infinite;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.typing-dot:nth-child(1) {
  animation-delay: 0s;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typingBounce {
  0%, 60%, 100% {
    transform: translateY(0) scale(1);
  }
  30% {
    transform: translateY(-12px) scale(1.2);
  }
}

.chat-input-container {
  display: flex;
  gap: 12px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.chat-input-container:focus-within {
  border-color: rgba(102, 126, 234, 0.5);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.chat-input {
  flex: 1;
  background: transparent;
  border: none;
  color: #ffffff;
  font-size: 15px;
  resize: none;
  outline: none;
  font-family: inherit;
  line-height: 1.6;
  min-height: 48px;
  max-height: 150px;
  padding: 4px 0;
}

.chat-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
  font-style: italic;
}

.chat-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-button {
  width: 48px;
  height: 48px;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.send-button:hover:not(:disabled) {
  transform: scale(1.08) translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.send-button:active:not(:disabled) {
  transform: scale(0.95);
}

.send-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  box-shadow: none;
}

.send-icon {
  font-size: 22px;
  color: #ffffff;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.send-button .loading-spinner {
  width: 22px;
  height: 22px;
  border-width: 2.5px;
}

@media (max-width: 768px) {
  .ai-panel {
    width: 100%;
  }
  
  .chat-header {
    padding: 16px;
  }
  
  .chat-title {
    font-size: 16px;
  }
  
  .chat-desc {
    font-size: 13px;
  }
  
  .chat-messages {
    padding: 16px;
    gap: 16px;
  }
  
  .message-avatar {
    width: 36px;
    height: 36px;
    font-size: 18px;
  }
  
  .message-text {
    padding: 12px 14px;
    font-size: 13px;
  }
  
  .message-user .message-text {
    max-width: 85%;
  }
  
  .chat-input-container {
    padding: 16px;
    gap: 10px;
  }
  
  .chat-input {
    font-size: 14px;
    min-height: 44px;
  }
  
  .send-button {
    width: 44px;
    height: 44px;
  }
  
  .send-icon {
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .ai-panel {
    width: 100%;
  }
  
  .chat-header {
    padding: 12px;
  }
  
  .chat-title {
    font-size: 15px;
  }
  
  .chat-desc {
    font-size: 12px;
  }
  
  .chat-messages {
    padding: 12px;
    gap: 12px;
  }
  
  .message-avatar {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }
  
  .message-text {
    padding: 10px 12px;
    font-size: 13px;
    line-height: 1.5;
  }
  
  .message-user .message-text {
    max-width: 90%;
  }
  
  .chat-input-container {
    padding: 12px;
    gap: 8px;
  }
  
  .chat-input {
    font-size: 14px;
    min-height: 40px;
  }
  
  .send-button {
    width: 40px;
    height: 40px;
  }
  
  .send-icon {
    font-size: 18px;
  }
  
  .typing-dot {
    width: 8px;
    height: 8px;
  }
}
</style>
