if (!window.__JEWELLERY_APP_INITIALIZED) {
  window.__JEWELLERY_APP_INITIALIZED = true;

  const chatInput = document.getElementById("chatInput");
  const chatBtn = document.getElementById("chatBtn");
  const chatMessages = document.getElementById("chatMessages");
  const statusBanner = document.getElementById("statusBanner");

  const imageInput = document.getElementById("imageInput");
  const imageBtn = document.getElementById("imageBtn");
  const imageOutput = document.getElementById("imageOutput");

  const promptInput = document.getElementById("promptInput");
  const generateBtn = document.getElementById("generateBtn");
  const imageNote = document.getElementById("imageNote");
  const generatedImage = document.getElementById("generatedImage");

  function addMessage(role, text) {
    const bubble = document.createElement("div");
    bubble.className = `message ${role}`;
    bubble.textContent = text;
    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  async function checkBackend() {
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "ping" }),
      });
      if (res.ok) {
        statusBanner.textContent = "✅ Connected to backend.";
        statusBanner.className = "status-banner ok";
      } else {
        statusBanner.textContent = "⚠️ Backend reachable but returned an error. Check server logs.";
        statusBanner.className = "status-banner warn";
      }
    } catch {
      statusBanner.textContent =
        "❌ Backend not reachable. Run FastAPI and open http://localhost:8000 (not the raw HTML file).";
      statusBanner.className = "status-banner error";
    }
  }

  async function sendChat() {
    const message = chatInput.value.trim();
    if (!message) return;

    addMessage("user", message);
    chatInput.value = "";

    const loading = document.createElement("div");
    loading.className = "message bot";
    loading.textContent = "Thinking...";
    chatMessages.appendChild(loading);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
      if (!res.ok) throw new Error(`Request failed: ${res.status}`);

      const data = await res.json();
      loading.remove();
      addMessage("bot", data.reply);
    } catch (error) {
      loading.textContent = `Error: ${error.message}. Make sure backend is running on http://localhost:8000`;
    }
  }

  chatBtn.addEventListener("click", sendChat);
  chatInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendChat();
    }
  });

  imageBtn.addEventListener("click", async () => {
    const file = imageInput.files?.[0];
    if (!file) {
      imageOutput.textContent = "Please upload an image first.";
      return;
    }

    imageOutput.textContent = "Analyzing image...";
    try {
      const formData = new FormData();
      formData.append("image", file);

      const res = await fetch("/api/image-to-text", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error(`Request failed: ${res.status}`);

      const data = await res.json();
      imageOutput.textContent = data.description;
    } catch (error) {
      imageOutput.textContent = `Error: ${error.message}. Make sure backend is running on http://localhost:8000`;
    }
  });

  generateBtn.addEventListener("click", async () => {
    const prompt = promptInput.value.trim();
    if (!prompt) return;

    imageNote.textContent = "Generating image...";
    generatedImage.hidden = true;

    try {
      const res = await fetch("/api/text-to-image", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, size: "1024x1024" }),
      });
      if (!res.ok) throw new Error(`Request failed: ${res.status}`);

      const data = await res.json();
      if (data.note) {
        imageNote.textContent = data.note;
        return;
      }

      imageNote.textContent = "Done.";
      generatedImage.src = `data:image/png;base64,${data.image_base64}`;
      generatedImage.hidden = false;
    } catch (error) {
      imageNote.textContent = `Error: ${error.message}. Make sure backend is running on http://localhost:8000`;
    }
  });

  checkBackend();
}
