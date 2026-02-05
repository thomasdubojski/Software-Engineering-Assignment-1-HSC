const CACHE_NAME = "tastetracker-cache-v1";

const FILES_TO_CACHE = [
  "/",
  "/login",
  "/register",
  "/static/css/style.css",
  "/static/js/app.js"
]

// Install event
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(FILES_TO_CACHE);
    })
  );
});

// Fetch event
self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});