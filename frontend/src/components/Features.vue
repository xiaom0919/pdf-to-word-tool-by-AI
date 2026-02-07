<script setup>
const features = [
  {
    icon: '⚡',
    title: '快速转换',
    desc: '基于 pdf2docx 库，转换速度快'
  },
  {
    icon: '🎨',
    title: '格式保留',
    desc: '智能识别文档结构，保留原始格式'
  },
  {
    icon: '🤖',
    title: 'AI 助手',
    desc: '支持文档摘要、翻译和智能问答'
  },
  {
    icon: '🔒',
    title: '安全可靠',
    desc: '本地处理，保护您的文档隐私'
  },
  {
    icon: '📱',
    title: '响应式设计',
    desc: '完美适配各种设备屏幕'
  },
  {
    icon: '🌐',
    title: '多语言支持',
    desc: '支持多种语言的翻译功能'
  }
]
</script>

<template>
  <div class="features">
    <div
      v-for="(feature, index) in features"
      :key="index"
      class="feature-item"
      :style="{ animationDelay: `${index * 0.1}s` }"
    >
      <div class="feature-icon-wrapper">
        <div class="feature-icon">{{ feature.icon }}</div>
        <div class="feature-icon-bg"></div>
      </div>
      <div class="feature-title">{{ feature.title }}</div>
      <div class="feature-desc">{{ feature.desc }}</div>
    </div>
  </div>
</template>

<style scoped>
.features {
  max-width: 1000px;
  margin: 4rem auto 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  position: relative;
  z-index: 1;
}

.feature-item {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  padding: 2.5rem;
  border-radius: 20px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  animation: fadeInUp 0.8s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.feature-item:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
  border-color: rgba(102, 126, 234, 0.3);
}

.feature-icon-wrapper {
  position: relative;
  display: inline-block;
  margin-bottom: 1.5rem;
}

.feature-icon {
  font-size: 3.5rem;
  position: relative;
  z-index: 1;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.feature-icon-bg {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
  border-radius: 50%;
  z-index: 0;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; }
  50% { transform: translate(-50%, -50%) scale(1.1); opacity: 0.8; }
}

.feature-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 0.75rem;
}

.feature-desc {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.95rem;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .features {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .feature-item {
    padding: 2rem;
  }
}
</style>
