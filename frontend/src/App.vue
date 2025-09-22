<script setup>
import { useRoute, RouterLink, RouterView } from 'vue-router'
import { computed } from 'vue';

const route = useRoute();

const navItems = [
  { name: "发现", path: "/", icon: (p) => `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="${p.isActive ? '#E5B84A' : 'currentColor'}"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>` },
  { name: "创建", path: "#", icon: (p) => `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="${p.isActive ? '#E5B84A' : 'currentColor'}" stroke-width="2"><path d="M12 5v14m-7-7h14" /></svg>` },
];

</script>

<template>
  <div class="h-screen w-screen bg-[#0D0D1A] text-white font-sans flex overflow-hidden">
    <!-- 左侧导航栏 -->
    <nav class="w-64 h-full bg-[#1A1A2E] p-4 flex-col shrink-0 hidden sm:flex">
      <div class="text-2xl font-bold text-yellow-400 mb-10">赋灵</div>
      <div class="flex flex-col space-y-4">
        <RouterLink v-for="item in navItems" :key="item.name" :to="item.path"
          :class="['flex items-center space-x-3 p-2 rounded-lg transition-colors', route.path === item.path ? 'bg-yellow-400/10 text-yellow-300' : 'hover:bg-white/10']">
          <span v-html="item.icon({ isActive: route.path === item.path })"></span>
          <span>{{ item.name }}</span>
        </RouterLink>
      </div>
    </nav>

    <!-- 主内容区 -->
    <main class="flex-1 h-full overflow-y-auto">
      <RouterView />
    </main>
  </div>
</template>
