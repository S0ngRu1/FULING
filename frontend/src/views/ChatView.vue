<script setup>
import {ref, onMounted, watch, nextTick} from 'vue';
import {useRoute, useRouter} from 'vue-router';
import axios from 'axios';

const props = defineProps({
  characterId: String
});

const API_BASE_URL = 'http://localhost:5123';
const router = useRouter();

// --- 响应式状态 ---
const character = ref(null);
const messages = ref([]);
const input = ref('');
const isLoading = ref(false);
const isListening = ref(false);
const chatEndRef = ref(null);
let recognition;
let currentAudio = null; // 用于控制音频播放

// --- 专业TTS播放模块 ---
const playAudioFromText = async (text) => {
  if (typeof text !== 'string' || !text.trim() || !character.value?.voiceType) return;

  if (currentAudio) {
    currentAudio.pause();
    currentAudio.currentTime = 0;
  }

  try {
    const response = await axios.post(`${API_BASE_URL}/api/speech`, {
      text: text,
      voiceType: character.value.voiceType
    });

    const base64Audio = response.data.audioData;
    const audioSrc = `data:audio/mp3;base64,${base64Audio}`;

    currentAudio = new Audio(audioSrc);
    currentAudio.play();

  } catch (error) {
    console.error("生成或播放语音失败:", error);
  }
};

// --- 语音识别 (STT) 模块 ---
const setupSpeechRecognition = () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    console.warn("浏览器不支持语音识别。");
    return;
  }
  recognition = new SpeechRecognition();
  recognition.lang = 'zh-CN';
  recognition.interimResults = false;
  recognition.onstart = () => isListening.value = true;
  recognition.onend = () => isListening.value = false;
  recognition.onresult = (event) => {
    input.value = event.results[0][0].transcript;
    handleSendMessage();
  };
  recognition.onerror = (event) => {
    console.error("语音识别错误:", event.error);
    isListening.value = false;
  };
};

const startListening = () => {
  if (recognition && !isLoading.value) {
    try {
      recognition.start();
    } catch (e) {
      console.error("无法启动语音识别:", e);
    }
  }
};

// --- 核心聊天逻辑 ---
const handleSendMessage = async () => {
  const userInput = input.value.trim();
  if (!userInput || isLoading.value) return;

  messages.value.push({role: 'user', content: userInput});
  input.value = '';
  isLoading.value = true;

  const history = messages.value.slice(0, -1).map(msg => ({
    role: msg.role === 'user' ? 'user' : 'assistant',
    content: msg.content
  }));

  try {
    const response = await axios.post(`${API_BASE_URL}/api/chat`, {
      characterId: props.characterId,
      message: userInput,
      history,
    });

    const aiResponseText = response.data.response;
    const aiMessage = {role: 'assistant', content: aiResponseText};
    messages.value.push(aiMessage);

    playAudioFromText(aiResponseText);

  } catch (error) {
    console.error("发送消息失败:", error);
    const errorMsgContent = '抱歉，我的思维出现了一点混乱。';
    messages.value.push({role: 'assistant', content: errorMsgContent});
  } finally {
    isLoading.value = false;
  }
};

// --- Vue生命周期钩子 ---
watch(messages, () => nextTick(() => chatEndRef.value?.scrollIntoView({behavior: 'smooth'})), {deep: true});

onMounted(async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/characters`);
    const currentChar = response.data.find(c => c.id === props.characterId);
    if (currentChar) character.value = currentChar;
    else router.push('/');
  } catch (error) {
    console.error("获取角色信息失败:", error);
  }
  setupSpeechRecognition();
});
</script>

<template>
  <div v-if="character" class="flex h-full w-full">
    <!-- 左侧角色展示区  -->
    <div class="hidden lg:block w-96 xl:w-[420px] h-full shrink-0 group relative overflow-hidden">
      <div
        class="absolute inset-0 bg-cover bg-center transition-transform duration-500 ease-in-out group-hover:scale-100 scale-110"
        :style="{ backgroundImage: `url(${character.imageUrl})` }"></div>
      <div
        class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent"></div>
      <div class="relative z-10 flex flex-col justify-end h-full p-8 text-white">
        <div class="transition-opacity duration-300 opacity-0 group-hover:opacity-100 mb-4">
          <p class="text-white/80 line-clamp-6">{{ character.description }}</p>
        </div>
        <h1 class="text-4xl font-bold">{{ character.name }}</h1>
      </div>
    </div>

    <!-- 右侧聊天界面 -->
    <div class="flex flex-col flex-1 h-full bg-[#1F1F2C]">
      <header class="p-4 border-b border-white/10 flex items-center shrink-0">
        <img :src="character.imageUrl" class="w-12 h-12 rounded-full object-cover mr-4"/>
        <div>
          <h2 class="text-xl font-bold">{{ character.name }}</h2>
          <p class="text-sm text-white/60">{{ character.description }}</p>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-6 space-y-6">
        <div v-if="messages.length === 0" class="text-center text-white/50 mt-10">开始对话吧</div>
        <div v-for="(msg, index) in messages" :key="index"
             :class="['flex gap-3', msg.role === 'user' ? 'flex-row-reverse' : '']">
          <img
            :src="msg.role === 'user' ? 'https://placehold.co/40x40/FBBF24/000000?text=我' : character.imageUrl"
            class="w-10 h-10 rounded-full object-cover shrink-0"/>
          <div v-if="msg.role === 'user'" class="max-w-xl p-4 rounded-xl bg-yellow-500 text-black">
            <p style="white-space: pre-wrap;">{{ msg.content }}</p>
          </div>
          <div v-else class="relative group pt-8">
            <button @click="playAudioFromText(msg.content)"
                    class="absolute top-0 left-4 z-10 flex items-center gap-1.5 pl-2 pr-3 py-1 rounded-full bg-slate-600 text-white/70 opacity-0 group-hover:opacity-100 hover:text-white hover:bg-slate-500 transition-all duration-300">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none"
                   viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round"
                      d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"/>
              </svg>
              <span class="text-xs font-semibold">回放</span>
            </button>
            <div class="max-w-xl px-5 py-4 rounded-2xl bg-gray-800 text-white">
              <p style="white-space: pre-wrap;">{{ msg.content }}</p>
            </div>
          </div>
        </div>
        <div v-if="isLoading" class="flex gap-3">
          <img :src="character.imageUrl" class="w-10 h-10 rounded-full object-cover"/>
          <div class="max-w-xl p-3 rounded-xl bg-gray-700 flex items-center">
            <span
              class="h-2 w-2 bg-white rounded-full animate-bounce [animation-delay:-0.3s]"></span>
            <span
              class="h-2 w-2 bg-white rounded-full animate-bounce [animation-delay:-0.15s] mx-1"></span>
            <span class="h-2 w-2 bg-white rounded-full animate-bounce"></span>
          </div>
        </div>
        <div ref="chatEndRef"></div>
      </main>

      <footer class="p-4 border-t border-white/10 shrink-0">
        <form @submit.prevent="handleSendMessage"
              class="flex items-center bg-gray-800 rounded-xl p-2 gap-2">
          <button type="button" @click="startListening" :disabled="isLoading"
                  :class="['p-2.5 rounded-full transition-colors', isListening ? 'text-yellow-400 animate-pulse' : 'text-white/70 hover:text-yellow-400']">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24"
                 stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round"
                    d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
            </svg>
          </button>
          <input v-model="input" type="text"
                 :placeholder="isListening ? '正在聆听...' : '输入消息或点击麦克风...'"
                 class="w-full bg-transparent px-4 py-2 text-white placeholder-gray-400 focus:outline-none"
                 :disabled="isLoading" @keyup.enter="handleSendMessage"/>
          <button type="submit" :disabled="isLoading || !input.trim()"
                  class="bg-yellow-500 rounded-lg p-2.5 hover:bg-yellow-400 disabled:bg-gray-600">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-black" fill="none"
                 viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M5 12h14m-7-7 7-7"/>
            </svg>
          </button>
        </form>
      </footer>
    </div>
  </div>
  <div v-else class="flex justify-center items-center h-full">加载中...</div>
</template>

