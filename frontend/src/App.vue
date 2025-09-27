<script setup>
import { useRoute, RouterLink, RouterView } from 'vue-router'

const route = useRoute();

const navItems = [
  { name: "发现角色", path: "/", icon: (p) => `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="${p.isActive ? '#E5B84A' : 'currentColor'}"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>` },
  { name: "创建角色", path: "/create", icon: (p) => `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="${p.isActive ? '#E5B84A' : 'currentColor'}" stroke-width="2"><path d="M12 5v14m-7-7h14" /></svg>` },
];
</script>

<template>
  <div class="h-screen w-screen bg-[#0D0D1A] text-white font-sans flex flex-col overflow-hidden">
    <!-- 全局置顶标题栏 -->
    <header class="w-full h-16 bg-[#1A1A2E] flex items-center px-8 shrink-0 z-20 border-b border-white/10">
      <h1 class="text-xl font-bold text-yellow-400 tracking-wider">赋灵 - AI角色扮演语音聊天</h1>
    </header>

    <!-- 主体内容区 -->
    <div class="flex flex-1 overflow-hidden">
      <!-- 左侧导航栏 -->
      <nav class="w-64 h-full bg-[#1A1A2E] p-4 flex-col shrink-0 hidden sm:flex">
        <div class="flex flex-col space-y-4 mt-4">
          <RouterLink v-for="item in navItems" :key="item.name" :to="item.path"
            :class="['flex items-center space-x-3 p-3 rounded-lg transition-colors', (route.path === item.path || (item.path === '/history' && route.path.startsWith('/history'))) ? 'bg-yellow-400/10 text-yellow-300' : 'hover:bg-white/10']">
            <span v-html="item.icon({ isActive: route.path === item.path || (item.path === '/history' && route.path.startsWith('/history')) })"></span>
            <span>{{ item.name }}</span>
          </RouterLink>
        </div>
      </nav>

      <!-- 动态内容区 (渲染具体页面) -->
      <main class="flex-1 h-full overflow-y-auto">
        <RouterView />
      </main>
    </div>
  </div>
</template>
