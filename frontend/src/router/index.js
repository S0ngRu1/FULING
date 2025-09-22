import { createRouter, createWebHistory } from 'vue-router'
import CharacterListView from '../views/CharacterListView.vue'
import ChatView from '../views/ChatView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: CharacterListView
    },
    {
      path: '/chat/:characterId',
      name: 'chat',
      component: ChatView,
      props: true
    }
  ]
})

export default router
