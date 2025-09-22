<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

const props = defineProps({
  characterId: String
});

const API_BASE_URL = 'http://localhost:5000';
const router = useRouter();

const character = ref(null);
const messages = ref([]);
const input = ref('');
const isLoading = ref(false);
const chatEndRef = ref(null);
let recognition;

const speakText = (text) => {
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'zh-CN';
  window.speechSynthesis.speak(utterance);
};

const setupSpeechRecognition = () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) return;

  recognition = new SpeechRecognition();
  recognition.lang = 'zh-CN';
  recognition.interimResults = false;

  recognition.onresult = (event) => {
    input.value = event.results[0][0].transcript;
    handleSendMessage();
  };

  recognition.onerror = (event) => console.error("语音识别错误:", event.error);
};

const startListening = () => {
    if(recognition) recognition.start();
};

const handleSendMessage = async () => {
  const userInput = input.value.trim();
  if (!userInput || isLoading.value) return;

  messages.value.push({ role: 'user', content: userInput });
  input.value = '';
  isLoading.value = true;

  const history = messages.value.slice(0, -1).map(msg => ({ role: msg.role, content: msg.content }));

  try {
    const response = await axios.post(`${API_BASE_URL}/api/chat`, {
      characterId: props.characterId,
      message: userInput,
      history,
    });
    const aiMessage = { role: 'assistant', content: response.data.responseText };
    messages.value.push(aiMessage);
    speakText(response.data.responseText);
  } catch (error) {
    console.error("发送消息失败:", error);
    const errorMsg = { role: 'assistant', content: '抱歉，我好像断线了... 请稍后再试。' };
    messages.value.push(errorMsg);
    speakText(errorMsg.content);
  } finally {
    isLoading.value = false;
  }
};

watch(messages, () => {
  nextTick(() => {
    chatEndRef.value?.scrollIntoView({ behavior: 'smooth' });
  });
}, { deep: true });

onMounted(async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/characters`);
    const currentChar = response.data.find(c => c.id === props.characterId);
    if (currentChar) {
      character.value = currentChar;
    } else {
      router.push('/');
    }
  } catch (error) {
    console.error("获取角色信息失败:", error);
  }
  setupSpeechRecognition();
});

</script>

<template>
  <div v-if="character" class="flex flex-col h-full bg-[#1F1F2C]">
    <header class="p-4 border-b border-white/10 flex items-center shrink-0">
      <img :src="character.imageUrl" class="w-12 h-12 rounded-full object-cover mr-4" />
      <div>
        <h2 class="text-xl font-bold">{{ character.name }}</h2>
        <p class="text-sm text-white/60">{{ character.description }}</p>
      </div>
    </header>

    <main class="flex-1 overflow-y-auto p-6 space-y-6">
      <div v-if="messages.length === 0" class="text-center text-white/50 mt-10">开始对话吧</div>

      <div v-for="(msg, index) in messages" :key="index" :class="['flex gap-3', msg.role === 'user' ? 'flex-row-reverse' : '']">
        <img :src="msg.role === 'user' ? 'https://placehold.co/40x40/FBBF24/000000?text=我' : character.imageUrl" class="w-10 h-10 rounded-full object-cover shrink-0" />
        <div :class="['max-w-xl p-3 rounded-xl', msg.role === 'user' ? 'bg-yellow-500 text-black' : 'bg-gray-700']">
          <p style="white-space: pre-wrap;">{{ msg.content }}</p>
        </div>
      </div>

      <div v-if="isLoading" class="flex gap-3">
        <img :src="character.imageUrl" class="w-10 h-10 rounded-full object-cover" />
        <div class="max-w-xl p-3 rounded-xl bg-gray-700 flex items-center">
          <span class="h-2 w-2 bg-white rounded-full animate-bounce [animation-delay:-0.3s]"></span>
          <span class="h-2 w-2 bg-white rounded-full animate-bounce [animation-delay:-0.15s] mx-1"></span>
          <span class="h-2 w-2 bg-white rounded-full animate-bounce"></span>
        </div>
      </div>
      <div ref="chatEndRef"></div>
    </main>

    <footer class="p-4 border-t border-white/10 shrink-0">
      <form @submit.prevent="handleSendMessage" class="flex items-center bg-gray-800 rounded-xl p-2 gap-2">
        <button type="button" @click="startListening" class="bg-transparent text-white/70 hover:text-yellow-400 p-2.5 rounded-full">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
        </button>
        <input v-model="input" type="text" placeholder="输入消息或点击麦克风..." class="w-full bg-transparent px-4 py-2 text-white placeholder-gray-400 focus:outline-none" :disabled="isLoading" />
        <button type="submit" :disabled="isLoading || !input.trim()" class="bg-yellow-500 rounded-lg p-2.5 hover:bg-yellow-400 disabled:bg-gray-600">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-black" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14m-7-7 7-7" /></svg>
        </button>
      </form>
    </footer>
  </div>
  <div v-else class="flex justify-center items-center h-full">加载中...</div>
</template>

