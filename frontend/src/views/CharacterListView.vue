<script setup>
import { ref, onMounted } from 'vue';
import { RouterLink } from 'vue-router';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';
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
    <header class="mb-8">
      <h1 class="text-3xl font-bold">发现角色</h1>
    </header>

    <div v-if="loading" class="text-center text-xl">加载角色中...</div>

    <main v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
      <RouterLink v-for="char in characters" :key="char.id" :to="`/chat/${char.id}`" class="group block bg-white/5 rounded-xl hover:bg-white/10 transition-all duration-300 transform hover:-translate-y-1 border border-transparent hover:border-yellow-400/50 overflow-hidden">
        <div class="aspect-w-3 aspect-h-4 w-full">
          <img :src="char.imageUrl" :alt="char.name" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
        </div>
        <div class="p-4">
          <h3 class="font-bold text-lg text-white truncate">{{ char.name }}</h3>
          <p class="text-sm text-white/60 line-clamp-2 mt-1">{{ char.description }}</p>
        </div>
      </RouterLink>
    </main>
  </div>
</template>
