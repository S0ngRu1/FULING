<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';
const router = useRouter();

const name = ref('');
const description = ref('');
const voiceType = ref('');
const imageFile = ref(null);
const imagePreview = ref(null);
const voices = ref([]);

const isSubmitting = ref(false);
const errorMessage = ref('');

const fetchVoices = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/voices`);
    voices.value = response.data.filter(v => v.voice_name.includes('小') || v.voice_name.includes('姐') || v.voice_name.includes('男') || v.voice_name.includes('女'));
    if (voices.value.length > 0) {
      voiceType.value = voices.value[0].voice_type;
    }
  } catch (error) {
    console.error("获取音色列表失败:", error);
    errorMessage.value = "无法加载音色列表，请稍后再试。";
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

onMounted(fetchVoices);
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

      <div>
        <label for="voiceType" class="block text-sm font-medium text-white/80 mb-2">选择音色</label>
        <select v-model="voiceType" id="voiceType" class="w-full bg-white/10 rounded-md border-white/20 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-yellow-400 appearance-none">
          <option v-for="voice in voices" :key="voice.voice_type" :value="voice.voice_type">{{ voice.voice_name }}</option>
        </select>
      </div>

      <div>
        <label for="image" class="block text-sm font-medium text-white/80 mb-2">上传形象</label>
        <div class="mt-2 flex items-center gap-4">
            <div class="w-24 h-24 rounded-full bg-white/10 flex items-center justify-center overflow-hidden">
                <img v-if="imagePreview" :src="imagePreview" alt="角色预览" class="w-full h-full object-cover">
                <span v-else class="text-white/40 text-xs">预览</span>
            </div>
            <input @change="handleFileChange" type="file" id="image" accept="image/png, image/jpeg" class="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-yellow-50 file:text-yellow-700 hover:file:bg-yellow-100"/>
        </div>
      </div>

      <div v-if="errorMessage" class="text-red-400 text-sm">
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
