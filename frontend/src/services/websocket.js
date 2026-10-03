export function connectMeetingSocket(meetingId, onMessage) {
  const wsBase = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000/ws'
  const socket = new WebSocket(`${wsBase}/meetings/${meetingId}/`)

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data)
    onMessage(data)
  }

  socket.onerror = (error) => {
    console.error('Erro no WebSocket:', error)
  }

  return socket
}