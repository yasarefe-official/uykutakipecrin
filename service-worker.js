console.log('Service Worker yüklendi.');

self.addEventListener('push', (event) => {
  console.log('[Service Worker] Push Alındı.');
  console.log(`[Service Worker] Push verisi: "${event.data.text()}"`);

  const title = '⏰ Uyku Zamanı!';
  const options = {
    body: event.data.text(),
    icon: 'https://img.icons8.com/color/96/000000/sleeping-in-bed.png',
    badge: 'https://img.icons8.com/color/48/000000/clock.png',
    vibrate: [200, 100, 200, 100, 200, 100, 200],
    tag: 'sleep-notification'
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', (event) => {
  console.log('[Service Worker] Bildirime tıklandı.');
  event.notification.close();
  event.waitUntil(
    clients.openWindow('https://uykutakipecrin.onrender.com')
  );
});
