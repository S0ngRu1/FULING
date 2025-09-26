<script setup>
import {ref, onMounted, watch, nextTick} from 'vue';
import {useRoute, useRouter} from 'vue-router';
import axios from 'axios';
import ConversationHistory from './ConversationHistory.vue';

const props = defineProps({characterId: String});
const API_BASE_URL = 'http://localhost:5123';
const router = useRoute();
const vueRouter = useRouter();
const userAvatarUrl = '/assets/user_avatar.png';

const character = ref(null);
const messages = ref([]);
const input = ref('');
const isLoading = ref(false);
const isListening = ref(false);
const chatEndRef = ref(null);
const conversationId = ref(null);
const showHistory = ref(true);

let recognition;
let currentAudio = null;

const replayAudio = (message) => {
  if (!message.audioSrc) return;
  if (currentAudio) {
    currentAudio.pause();
    currentAudio.currentTime = 0;
  }
  currentAudio = new Audio(message.audioSrc);
  currentAudio.play();
};

const setupSpeechRecognition = () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) return;
  recognition = new SpeechRecognition();
  recognition.lang = 'zh-CN';
  recognition.onstart = () => isListening.value = true;
  recognition.onend = () => isListening.value = false;
  recognition.onresult = (event) => {
    if (!isLoading.value) {
      input.value = event.results[0][0].transcript;
      handleSendMessage();
    }
  };
  recognition.onerror = (event) => {
    isListening.value = false;
    console.error("语音识别错误:", event.error);
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

// --- 核心修复在这里 ---
const handleSendMessage = async () => {
  if (isLoading.value) return;
  const userInput = input.value.trim();
  if (!userInput) return;

  messages.value.push({role: 'user', content: userInput});
  input.value = '';
  isLoading.value = true;

  const history = messages.value.slice(0, -1).map(msg => ({
    role: msg.role === 'user' ? 'user' : 'assistant',
    content: msg.content
  }));

  try {
    // 步骤 1: 调用 /api/chat 获取文本、情绪和对话ID
    const chatResponse = await axios.post(`${API_BASE_URL}/api/chat`, {
      characterId: props.characterId,
      message: userInput,
      history,
      conversationId: conversationId.value
    });

    // 从响应中提取所需数据
    conversationId.value = chatResponse.data.conversationId; // 更新对话ID
    const aiResponseText = chatResponse.data.text;
    const emotion = chatResponse.data.emotion; // **获取情绪，为语音接口做准备**

    // 健壮性检查：确保收到了有效的文本
    if (!aiResponseText) {
      throw new Error("从 /api/chat 返回的文本为空。");
    }

    // 步骤 2: 调用 /api/speech 获取音频数据
    const speechResponse = await axios.post(`${API_BASE_URL}/api/speech`, {
      text: aiResponseText,
      voiceType: character.value.voiceType, // 从角色信息中获取 voiceType
      emotion: emotion                      // 将情绪传递给语音接口
    });

    const base64Audio = speechResponse.data.audioData;
    const audioSrc = `data:audio/mp3;base64,${base64Audio}`;

    // 步骤 3: 预加载音频
    const audio = new Audio(audioSrc);
    await new Promise((resolve, reject) => {
      audio.oncanplaythrough = resolve;
      audio.onerror = reject;
    });

    // 步骤 4: 将文本和音频源一起推送到消息列表
    messages.value.push({role: 'assistant', content: aiResponseText, audioSrc: audioSrc});

    // 步骤 5: 播放音频
    if (currentAudio) currentAudio.pause();
    currentAudio = audio;
    currentAudio.play();

  } catch (error) {
    console.error("发送消息或生成语音时发生错误:", error);
    messages.value.push({role: 'assistant', content: '抱歉，我的思维出现了一点混乱。'});
  } finally {
    isLoading.value = false;
  }
};

const endConversation = async () => {
  if (!conversationId.value || messages.value.length === 0) {
    alert("还没有开始对话，无法结束。");
    return;
  }
  try {
    await axios.post(`${API_BASE_URL}/api/conversations/${conversationId.value}/summarize`, {
      // 注意：后端的 summarize_conversation 函数需要的是 history 列表
      history: messages.value.map(msg => ({role: msg.role, content: msg.content}))
    });
    alert("对话已结束，记忆已保存。");
    messages.value = [];
    conversationId.value = null;
    showHistory.value = true;
  } catch (error) {
    console.error("结束对话失败:", error);
    alert("保存记忆时出错，请稍后再试。");
  }
};

const startNewChat = () => {
  messages.value = [];
  conversationId.value = null;
  showHistory.value = false;
};

const continueChat = (id) => {
  alert(`继续对话 ${id}。\n(在完整应用中，这里会加载历史记录)`);
  conversationId.value = id;
  messages.value = [];
  showHistory.value = false;
};

onMounted(async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/characters`);
    const currentChar = response.data.find(c => c.id === props.characterId);
    if (currentChar) {
      character.value = currentChar;
    } else {
      vueRouter.push('/');
    }
  } catch (error) {
    console.error("获取角色信息失败:", error);
  }
  setupSpeechRecognition();
});
</script>
<template>
    <div v-if="character" class="flex h-full w-full">
        <!-- 左侧角色展示区 -->
        <div class="hidden lg:block w-96 xl:w-[420px] h-full shrink-0 group relative overflow-hidden">
            <div class="absolute inset-0 bg-cover bg-center transition-transform duration-500 ease-in-out group-hover:scale-100 scale-110" :style="{ backgroundImage: `url(${character.imageUrl})` }"></div>
            <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent"></div>
            <div class="relative z-10 flex flex-col justify-end h-full p-8 text-white">
                <div class="transition-opacity duration-300 opacity-0 group-hover:opacity-100 mb-4">
                    <p class="text-white/80 line-clamp-6">{{ character.description }}</p>
                </div>
                <h1 class="text-4xl font-bold">{{ character.name }}</h1>
            </div>
        </div>

        <!-- 右侧内容区: 历史记录 或 聊天界面 -->
        <div class="flex flex-col flex-1 h-full">
            <ConversationHistory
                v-if="showHistory"
                :character="character"
                :onContinue="continueChat"
                :onNewChat="startNewChat"
            />
            <div v-else class="flex flex-col flex-1 h-full bg-[#1F1F2C]">
                 <header class="p-4 border-b border-white/10 flex items-center justify-between shrink-0">
                    <div class="flex items-center">
                        <img :src="character.imageUrl" class="w-12 h-12 rounded-full object-cover mr-4" />
                        <div>
                        <h2 class="text-xl font-bold">{{ character.name }}</h2>
                        <p class="text-sm text-white/60">{{ character.description }}</p>
                        </div>
                    </div>
                    <button @click="endConversation" class="bg-red-600 hover:bg-red-500 text-white font-bold py-2 px-4 rounded-full transition-colors">
                        结束对话
                    </button>
                </header>

                <main class="flex-1 overflow-y-auto p-6 space-y-6">
                    <!-- ... (消息渲染逻辑不变) ... -->
                     <div v-if="messages.length === 0" class="text-center text-white/50 mt-10">开始对话吧</div>
                    <div v-for="(msg, index) in messages" :key="index" :class="['flex gap-3', msg.role === 'user' ? 'flex-row-reverse' : '']">
                        <img :src="msg.role === 'user' ? userAvatarUrl : character.imageUrl" class="w-10 h-10 rounded-full object-cover shrink-0" />
                        <div v-if="msg.role === 'user'" class="max-w-xl p-4 rounded-xl bg-yellow-500 text-black">
                            <p style="white-space: pre-wrap;">{{ msg.content }}</p>
                        </div>
                        <div v-else class="relative group max-w-xl">
                            <div class="px-5 py-4 rounded-2xl bg-gray-800 text-white">
                                <p style="white-space: pre-wrap;">{{ msg.content }}</p>
                            </div>
                            <button v-if="msg.audioSrc" @click="replayAudio(msg)"
                                    class="absolute -top-4 left-4 z-10 flex items-center gap-1.5 pl-2 pr-3 py-1 rounded-full bg-slate-600 text-white/70 opacity-0 group-hover:opacity-100 hover:text-white hover:bg-slate-500 transition-all duration-300">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                                </svg>
                                <span class="text-xs font-semibold">回放</span>
                            </button>
                        </div>
                    </div>
                    <div v-if="isLoading" class="flex gap-3">
                        <img :src="character.imageUrl" class="w-10 h-10 rounded-full object-cover" />
                        <div class="max-w-xl p-4 rounded-xl bg-gray-700 flex items-center text-sm text-white/80">
                            对方正在说话，请耐心等待...
                        </div>
                    </div>
                    <div ref="chatEndRef"></div>
                </main>

                <footer class="p-4 border-t border-white/10 shrink-0">
                    <!-- ... (表单逻辑不变) ... -->
                    <form @submit.prevent="handleSendMessage" class="flex items-center bg-gray-800 rounded-xl p-2 gap-2">
                        <button type="button" @click="startListening" :disabled="isLoading"
                                :class="['p-2.5 rounded-full transition-colors', isListening ? 'text-yellow-400 animate-pulse' : 'text-white/70 hover:text-yellow-400']">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                            </svg>
                        </button>
                        <input v-model="input" type="text"
                            :placeholder="isListening ? '正在聆听...' : '输入消息或点击麦克风...'"
                            class="w-full bg-transparent px-4 py-2 text-white placeholder-gray-400 focus:outline-none"
                            :disabled="isLoading" @keyup.enter="handleSendMessage" />
                        <button type="submit" :disabled="isLoading || !input.trim()" class="bg-yellow-500 rounded-lg p-2.5 hover:bg-yellow-400 disabled:bg-gray-600">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-black" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14m-7-7 7-7" /></svg>
                        </button>
                    </form>
                </footer>
            </div>
        </div>
    </div>
    <div v-else class="flex justify-center items-center h-full">加载中...</div>
</template>

