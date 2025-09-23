<script setup>
import { ref, onMounted } from 'vue';
import { RouterLink } from 'vue-router';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5123';
const characters = ref([]);
const loading = ref(true);

onMounted(async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/characters`);
    characters.value = response.data;
  } catch (error) {
    console.error("获取角色列表失败:", error);
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="p-4 sm:p-8 h-full">
    <!-- 使用 max-w-7xl 和 mx-auto 来让内容占据屏幕一多半并居中 -->
    <div class="max-w-7xl mx-auto">
      <header class="mb-8">
        <h1 class="text-3xl font-bold">发现角色</h1>
      </header>

      <div v-if="loading" class="text-center text-xl">加载角色中...</div>

      <!-- 网格布局现在固定为3列，响应式处理更小的屏幕 -->
      <main v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
        <RouterLink
          v-for="char in characters"
          :key="char.id"
          :to="`/chat/${char.id}`"
          class="group block bg-white/5 rounded-xl hover:bg-white/10 transition-all duration-300 transform hover:-translate-y-1 border border-transparent hover:border-yellow-400/50 overflow-hidden"
        >
          <!-- aspect-h-4/aspect-w-3 强制设定图片容器的宽高比为4:3，确保所有卡片大小一致 -->
          <div class="aspect-w-3 aspect-h-4 w-full">
            <!-- object-cover 会缩放并裁剪图片以填充容器，确保图片显示大小一致 -->
            <img
              :src="char.imageUrl"
              :alt="char.name"
              class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
          </div>
          <div class="p-4">
            <h3 class="font-bold text-lg text-white truncate">{{ char.name }}</h3>
            <p class="text-sm text-white/60 line-clamp-2 mt-1">{{ char.description }}</p>
          </div>
        </RouterLink>
      </main>
    </div>
  </div>
</template>

