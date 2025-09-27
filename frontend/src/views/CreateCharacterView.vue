<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5123';
const router = useRouter();

// 表单数据
const name = ref('');
const description = ref('');
const voiceType = ref('');
const imageFile = ref(null);
const imagePreview = ref(null);

// 音色列表和自定义下拉框状态
const voices = ref([]);
const isDropdownOpen = ref(false);
const dropdownRef = ref(null); // 用于检测外部点击

// 提交状态
const isSubmitting = ref(false);
const errorMessage = ref('');

// --- 自定义下拉框逻辑 ---
const selectedVoiceName = computed(() => {
  const selected = voices.value.find(v => v.voice_type === voiceType.value);
  return selected ? selected.voice_name : '请选择一个音色';
});

const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value;
};

const selectVoice = (voice) => {
  voiceType.value = voice.voice_type;
  isDropdownOpen.value = false;
};

const handleClickOutside = (event) => {
    if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
        isDropdownOpen.value = false;
    }
};

// --- API 和文件处理 ---
const fetchVoices = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/voices`);
    voices.value = response.data;
    if (voices.value.length > 0) {
      voiceType.value = voices.value[0].voice_type;
    }
  } catch (error) {
    console.error("获取音色列表失败:", error);
    if (error.response && error.response.data && error.response.data.error) {
        errorMessage.value = `加载音色列表失败: ${error.response.data.error.message}`;
    } else {
        errorMessage.value = "无法连接到后端服务，请确认服务已启动并检查网络连接。";
    }
  }
};

const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    imageFile.value = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.value = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};

const handleSubmit = async () => {
  if (!name.value || !description.value || !voiceType.value || !imageFile.value) {
    errorMessage.value = "所有字段均为必填项。";
    return;
  }

  isSubmitting.value = true;
  errorMessage.value = '';

  const formData = new FormData();
  formData.append('name', name.value);
  formData.append('description', description.value);
  formData.append('voiceType', voiceType.value);
  formData.append('image', imageFile.value);

  try {
    await axios.post(`${API_BASE_URL}/api/characters`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    alert('角色创建成功！');
    router.push('/');
  } catch (error) {
    console.error("创建角色失败:", error);
    errorMessage.value = error.response?.data?.error?.message || "创建失败，请检查后端服务。";
  } finally {
    isSubmitting.value = false;
  }
};

// --- 生命周期钩子 ---
onMounted(() => {
    fetchVoices();
    document.addEventListener('mousedown', handleClickOutside);
});

onUnmounted(() => {
    document.removeEventListener('mousedown', handleClickOutside);
});
</script>

<template>
  <div class="p-8 max-w-2xl mx-auto">
    <header class="mb-8">
      <h1 class="text-3xl font-bold">创建你的专属角色</h1>
      <p class="text-white/60 mt-2">赋予生命，开启独一无二的对话体验。</p>
    </header>

    <form @submit.prevent="handleSubmit" class="space-y-6">
      <div>
        <label for="name" class="block text-sm font-medium text-white/80 mb-2">角色名称</label>
        <input v-model="name" type="text" id="name" class="w-full bg-white/10 rounded-md border-white/20 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-yellow-400" placeholder="例如：辰熙">
      </div>

      <div>
        <label for="description" class="block text-sm font-medium text-white/80 mb-2">角色描述</label>
        <textarea v-model="description" id="description" rows="4" class="w-full bg-white/10 rounded-md border-white/20 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-yellow-400" placeholder="描述角色的性格、背景故事、外貌等..."></textarea>
      </div>

      <!-- 自定义下拉框 -->
      <div>
        <label for="voiceType" class="block text-sm font-medium text-white/80 mb-2">选择音色</label>
        <div class="relative" ref="dropdownRef">
            <button @click="toggleDropdown" type="button" class="w-full flex justify-between items-center text-left bg-white/10 rounded-md border-white/20 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-yellow-400">
                <span class="truncate">{{ selectedVoiceName }}</span>
                <svg xmlns="http://www.w3.org/2000/svg" :class="['h-5 w-5 transition-transform duration-200 text-white/50', isDropdownOpen ? 'rotate-180' : '']" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
                </svg>
            </button>
            <ul v-if="isDropdownOpen" class="absolute z-10 mt-1 w-full bg-gray-800 rounded-md shadow-lg max-h-60 overflow-y-auto custom-scrollbar border border-white/20">
                <li v-for="voice in voices" :key="voice.voice_type" @click="selectVoice(voice)" class="px-4 py-2 text-white/80 hover:bg-yellow-400/10 hover:text-white cursor-pointer">
                    {{ voice.voice_name }}
                </li>
            </ul>
        </div>
      </div>

      <div>
        <label for="image" class="block text-sm font-medium text-white/80 mb-2">上传形象</label>
        <div class="mt-2 flex items-center gap-4">
            <div class="w-24 h-32 rounded-l bg-white/10 flex items-center justify-center overflow-hidden">
                <img v-if="imagePreview" :src="imagePreview" alt="角色预览" class="w-full h-full object-cover">
                <span v-else class="text-white/40 text-xs">预览</span>
            </div>
            <input @change="handleFileChange" type="file" id="image" accept="image/png, image/jpeg" class="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-yellow-50 file:text-yellow-700 hover:file:bg-yellow-100"/>
        </div>
      </div>

      <div v-if="errorMessage" class="text-red-400 text-sm p-4 bg-red-500/10 rounded-md">
          {{ errorMessage }}
      </div>

      <div>
        <button type="submit" :disabled="isSubmitting" class="w-full bg-yellow-400 text-black font-bold py-3 px-8 rounded-full hover:bg-yellow-300 transition-colors disabled:bg-gray-500">
          {{ isSubmitting ? '正在创建...' : '完成创建' }}
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
/* 自定义滚动条样式 */
.custom-scrollbar::-webkit-scrollbar {
    width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.4);
}
</style>

