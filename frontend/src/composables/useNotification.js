import { ref } from 'vue'

const notifications = ref([])

function removeNotification(id) {
  notifications.value = notifications.value.filter(notification => notification.id !== id)
}

export function notify({ message, type = 'info', timeout = 3000, id }) {
  const createdAt = Date.now()
  const notificationId = id ?? `${createdAt}-${Math.random()}`
  notifications.value.push({ id: notificationId, message, type, timeout, createdAt })

  if (timeout > 0) {
    setTimeout(() => {
      removeNotification(notificationId)
    }, timeout)
  }
}

export function throwError({ id, message }) {
  notify({ id, message, type: 'error' })
}

export default function useNotification() {
  return {
    notifications,
    notify,
    removeNotification,
  }
}