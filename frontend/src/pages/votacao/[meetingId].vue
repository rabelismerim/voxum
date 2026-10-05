<template>
  <div class="px-4 w-full md:w-94% max-w-200 mx-auto py-6">
    <div class="bg--base border border--content/12 p-6 rounded-xl shadow-sm">
      <span class="text-xs text--primary font-semibold uppercase">Votação em Andamento</span>
      <h2 class="text-2xl font-bold text--content mt-1">Aprovação do Plano de Recuperação</h2>
      <p class="text-sm text--secondary mt-2">ID da Reunião: {{ $route.params.meetingId }}</p>
    </div>
  </div>
</template>
