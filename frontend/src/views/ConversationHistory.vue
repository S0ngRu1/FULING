<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';

const props = defineProps({
  character: Object,
  onContinue: Function,
  onNewChat: Function,
});

const API_BASE_URL = 'http://localhost:5123';
const conversations = ref([]);
const loading = ref(true);

const fetchConversations = async () => {
  if (!props.character) return;
  loading.value = true;
  try {
    const response = await axios.get(`${API_BASE_URL}/api/conversations/${props.character.id}`);
    conversations.value = response.data.map(conv => ({
        ...conv,
        updated_at: new Date(conv.updated_at).toLocaleString('zh-CN', { dateStyle: 'short', timeStyle: 'short' })
    }));
  } catch (error) {
    console.error("获取历史对话失败:", error);
    conversations.value = []; // 出错时清空列表
  } finally {
    loading.value = false;
  }
};

const deleteConversation = async (conversationId) => {
  if (!confirm("确定要删除这段记忆吗？")) return;
  try {
    await axios.delete(`${API__BASE_URL}/api/conversations/${conversationId}`);
    fetchConversations(); // 重新获取列表
  } catch (error) {
    console.error("删除对话失败:", error);
  }
};

watch(() => props.character, (newCharacter) => {
  if (newCharacter && newCharacter.id) {
    fetchConversations();
  }
}, { immediate: true });

</script>

<template>
  <div class="p-8 h-full flex flex-col">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-3xl font-bold">选择一段记忆</h1>
      <button @click="onNewChat" class="bg-yellow-400 text-black font-bold py-2 px-4 rounded-full hover:bg-yellow-300 transition-colors">
        开启新对话
      </button>
    </div>

    <div v-if="loading" class="text-center py-10">加载记忆中...</div>
    <div v-else-if="conversations.length === 0" class="text-center py-10 text-white/60">
      还没有和 {{ character.name }} 的共同记忆呢，快去开启新对话吧！
    </div>

    <div v-else class="flex-1 overflow-y-auto space-y-4">
      <div v-for="conv in conversations" :key="conv.id" class="bg-white/5 p-4 rounded-lg flex items-center justify-between group">
        <div>
          <p class="font-bold text-white/90 truncate pr-4" :title="conv.first_message">{{ conv.first_message || '一段对话' }}</p>
          <p class="text-sm text-white/50 mt-1">摘要: {{ conv.summary }}</p>
          <p class="text-xs text-white/40 mt-2">{{ conv.updated_at }}</p>
        </div>

        <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">

          <button @click="onContinue(conv.id, conv.summary)" class="text-yellow-400 hover:text-yellow-300 text-sm font-bold">继续</button>

          <button @click="deleteConversation(conv.id)" class="text-red-500 hover:text-red-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0_0_24_24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
        </div>
    </div>
  </div>
</template>
