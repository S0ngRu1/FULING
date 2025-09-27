<script setup>
import { ref, watch } from 'vue';
import axios from 'axios';

const props = defineProps({
  character: Object,
  onContinue: Function,
  onNewChat: Function,
});

const API_BASE_URL = 'http://localhost:5123';
const conversations = ref([]);
const loading = ref(true);

// --- 控制删除确认框的状态 ---
const deleteModal = ref({
  show: false,
  conversationId: null, // 存储待删除的ID
  isDeleting: false, // 控制删除中的加载状态
});

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
    conversations.value = [];
  } finally {
    loading.value = false;
  }
};


// 第1步：点击删除图标时，打开确认框
const promptForDelete = (conversationId) => {
  deleteModal.value = { show: true, conversationId: conversationId, isDeleting: false };
};

// 第2步：在确认框中点击“确认”后，执行真正的删除
const confirmDelete = async () => {
  if (!deleteModal.value.conversationId) return;

  deleteModal.value.isDeleting = true; // 显示加载状态

  try {
    // *** Bug修复：API__BASE_URL -> API_BASE_URL ***
    await axios.delete(`${API_BASE_URL}/api/conversations/${deleteModal.value.conversationId}`);

    // 删除成功后，关闭模态框并刷新列表
    deleteModal.value = { show: false, conversationId: null, isDeleting: false };
    await fetchConversations(); // 重新获取列表

  } catch (error)
  {
    console.error("删除对话失败:", error);
    // 可以在这里添加错误提示
    deleteModal.value.isDeleting = false; // 隐藏加载状态
    alert('删除失败，请稍后再试。');
  }
};

const cancelDelete = () => {
  deleteModal.value.show = false;
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

          <button @click="promptForDelete(conv.id)" class="text-red-500 hover:text-red-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>

  <transition
      enter-active-class="transition-opacity duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
  >
    <div v-if="deleteModal.show" @click.self="cancelDelete" class="fixed inset-0 bg-black/70 flex justify-center items-center z-50 p-4">
        <div class="bg-gray-800 rounded-xl p-6 flex flex-col items-center gap-5 max-w-sm w-full">
            <h3 class="text-xl font-bold text-white">确认删除</h3>
            <p class="text-white/70 text-center">您确定要永久删除这段记忆吗？此操作无法撤销。</p>
            <div class="flex gap-4 w-full mt-2">
                <button @click="cancelDelete" class="w-full bg-white/10 hover:bg-white/20 text-white font-bold py-2 px-4 rounded-lg transition-colors">
                  取消
                </button>
                <button @click="confirmDelete" :disabled="deleteModal.isDeleting" class="w-full bg-red-600 hover:bg-red-500 text-white font-bold py-2 px-4 rounded-lg transition-colors disabled:bg-red-800 disabled:cursor-not-allowed flex justify-center items-center">
                  <svg v-if="deleteModal.isDeleting" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>{{ deleteModal.isDeleting ? '删除中...' : '确认删除' }}</span>
                </button>
            </div>
        </div>
    </div>
  </transition>

</template>
