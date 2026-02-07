<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const particles = ref([])
const mouseX = ref(0)
const mouseY = ref(0)
const animationFrameId = ref(null)

const createParticles = () => {
  const particleCount = 50
  const newParticles = []
  
  for (let i = 0; i < particleCount; i++) {
    newParticles.push({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 4 + 2,
      speedX: (Math.random() - 0.5) * 0.3,
      speedY: (Math.random() - 0.5) * 0.3,
      opacity: Math.random() * 0.5 + 0.2,
      hue: Math.random() * 60 + 240
    })
  }
  
  particles.value = newParticles
}

const updateParticles = () => {
  particles.value.forEach(particle => {
    particle.x += particle.speedX
    particle.y += particle.speedY
    
    if (particle.x < 0) particle.x = 100
    if (particle.x > 100) particle.x = 0
    if (particle.y < 0) particle.y = 100
    if (particle.y > 100) particle.y = 0
    
    const dx = particle.x - mouseX.value
    const dy = particle.y - mouseY.value
    const distance = Math.sqrt(dx * dx + dy * dy)
    
    if (distance < 20) {
      particle.x += dx * 0.02
      particle.y += dy * 0.02
    }
  })
  
  animationFrameId.value = requestAnimationFrame(updateParticles)
}

const handleMouseMove = (event) => {
  const rect = event.currentTarget.getBoundingClientRect()
  mouseX.value = ((event.clientX - rect.left) / rect.width) * 100
  mouseY.value = ((event.clientY - rect.top) / rect.height) * 100
}

onMounted(() => {
  createParticles()
  updateParticles()
})

onUnmounted(() => {
  if (animationFrameId.value) {
    cancelAnimationFrame(animationFrameId.value)
  }
})
</script>

<template>
  <div class="dynamic-background" @mousemove="handleMouseMove">
    <div class="gradient-orb orb-1"></div>
    <div class="gradient-orb orb-2"></div>
    <div class="gradient-orb orb-3"></div>
    <div class="gradient-orb orb-4"></div>
    <div class="gradient-orb orb-5"></div>
    
    <div class="floating-shape shape-1"></div>
    <div class="floating-shape shape-2"></div>
    <div class="floating-shape shape-3"></div>
    <div class="floating-shape shape-4"></div>
    
    <div class="grid-pattern"></div>
    <div class="noise-overlay"></div>
    
    <svg class="particles-container" viewBox="0 0 100 100" preserveAspectRatio="none">
      <circle
        v-for="particle in particles"
        :key="particle.id"
        :cx="particle.x"
        :cy="particle.y"
        :r="particle.size"
        :fill="`hsla(${particle.hue}, 70%, 60%, ${particle.opacity})`"
        class="particle"
      />
    </svg>
  </div>
</template>

<style scoped>
.dynamic-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.6;
  animation: floatOrb 20s ease-in-out infinite;
}

.orb-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.8) 0%, transparent 70%);
  top: -200px;
  left: -200px;
  animation-delay: 0s;
  animation-duration: 25s;
}

.orb-2 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(118, 75, 162, 0.7) 0%, transparent 70%);
  top: 20%;
  right: -150px;
  animation-delay: -5s;
  animation-duration: 30s;
}

.orb-3 {
  width: 450px;
  height: 450px;
  background: radial-gradient(circle, rgba(240, 98, 146, 0.6) 0%, transparent 70%);
  bottom: -100px;
  left: 30%;
  animation-delay: -10s;
  animation-duration: 28s;
}

.orb-4 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(66, 165, 245, 0.7) 0%, transparent 70%);
  top: 40%;
  left: 10%;
  animation-delay: -15s;
  animation-duration: 22s;
}

.orb-5 {
  width: 350px;
  height: 350px;
  background: radial-gradient(circle, rgba(171, 71, 188, 0.6) 0%, transparent 70%);
  bottom: 20%;
  right: 20%;
  animation-delay: -8s;
  animation-duration: 26s;
}

@keyframes floatOrb {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(100px, 50px) scale(1.1); }
  50% { transform: translate(-50px, 100px) scale(0.9); }
  75% { transform: translate(50px, -50px) scale(1.05); }
}

.floating-shape {
  position: absolute;
  opacity: 0.1;
  animation: floatShape 15s ease-in-out infinite;
}

.shape-1 {
  width: 300px;
  height: 300px;
  border: 3px solid rgba(102, 126, 234, 0.3);
  border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
  animation-duration: 20s;
}

.shape-2 {
  width: 250px;
  height: 250px;
  border: 2px solid rgba(118, 75, 162, 0.3);
  border-radius: 70% 30% 30% 70% / 70% 70% 30% 30%;
  top: 60%;
  right: 15%;
  animation-delay: -5s;
  animation-duration: 18s;
}

.shape-3 {
  width: 200px;
  height: 200px;
  border: 2px solid rgba(240, 98, 146, 0.3);
  border-radius: 50%;
  bottom: 20%;
  left: 20%;
  animation-delay: -10s;
  animation-duration: 22s;
}

.shape-4 {
  width: 180px;
  height: 180px;
  border: 2px solid rgba(66, 165, 245, 0.3);
  transform: rotate(45deg);
  top: 30%;
  right: 30%;
  animation-delay: -7s;
  animation-duration: 25s;
}

@keyframes floatShape {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  25% { transform: translate(30px, -30px) rotate(90deg); }
  50% { transform: translate(-20px, 20px) rotate(180deg); }
  75% { transform: translate(40px, 10px) rotate(270deg); }
}

.grid-pattern {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(rgba(102, 126, 234, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(102, 126, 234, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: gridMove 20s linear infinite;
}

@keyframes gridMove {
  0% { transform: translate(0, 0); }
  100% { transform: translate(50px, 50px); }
}

.noise-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0.03;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  pointer-events: none;
}

.particles-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.particle {
  transition: fill 0.3s ease;
}
</style>
