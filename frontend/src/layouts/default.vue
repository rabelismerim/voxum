<template>
  <div class="min-h-screen bg-white text-black flex flex-col font-sans">
    <header class="bg-white border-b border-gray-300 px-6 py-4 flex justify-between items-center shadow-md text-black">
      <div class="flex items-center space-x-3">
        <RouterLink to="/" class="text-2xl font-bold text-black tracking-wide">VOXUM</RouterLink>
        <span class="text-xs text-black px-2.5 py-0.5 font-medium">Assembleias</span>
      </div>
      <nav class="flex items-center space-x-4 text-sm text-black">
        <RouterLink to="/assembleias" class="hover:text-primary transition-colors" active-class="text-primary font-semibold">Assembleias</RouterLink>
        <button class="bg-transparent text-red-600 hover:text-red-700 transition-colors" @click="logout">Sair</button>
      </nav>
    </header>
    <main class="flex-1 p-6 max-w-7xl w-full mx-auto text-black">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
const router = useRouter()
const { logout: clearUserSession } = useUser

async function logout() {
  await clearUserSession()
  await router.push('/')
}
</script>