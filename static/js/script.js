document.addEventListener('DOMContentLoaded', () => {
  const urlForm = document.getElementById('urlForm');
  const urlInput = document.getElementById('urlInput');
  const searchBtn = document.getElementById('searchBtn');
  const btnText = document.getElementById('btnText');
  const btnLoader = document.getElementById('btnLoader');
  const errorMessage = document.getElementById('errorMessage');
  const resultsContainer = document.getElementById('resultsContainer');
  const resultsList = document.getElementById('resultsList');

  urlForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const inputUrl = urlInput.value.trim();

    if (!inputUrl) {
      showError('Please enter a valid YouTube URL.');
      return;
    }

    clearError();
    setLoading(true);
    resultsContainer.style.display = 'none';
    resultsList.innerHTML = '';

    try {
      const response = await fetch('/process-url', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: inputUrl,
          title: 'highlight_clip'
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to process YouTube comments.');
      }

      if (!data.clips || data.clips.length === 0) {
        showError('No timestamp comments found for this video.');
        return;
      }

      renderClips(data.clips, inputUrl);
      resultsContainer.style.display = 'block';

    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  });

  function renderClips(clips, originalUrl) {
    const videoId = extractVideoId(originalUrl);

    clips.forEach((clip, index) => {
      const startSeconds = parseHmsToSeconds(clip.startTime) + 30;
      const embedUrl = videoId 
        ? `https://www.youtube.com/embed/${videoId}?start=${startSeconds}`
        : null;

      const card = document.createElement('div');
      card.className = 'result-card';

      card.innerHTML = `
        <div class="clip-header">
          <span class="clip-number">Clip #${index + 1}</span>
          <span class="timestamp-badge">${clip.startTime} - ${clip.endTime}</span>
        </div>
        <p class="clip-comment">"${escapeHtml(clip.comment)}"</p>
        
        ${embedUrl ? `
          <div class="video-wrapper">
            <iframe 
              src="${embedUrl}" 
              title="YouTube clip player" 
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
              allowfullscreen>
            </iframe>
          </div>
        ` : ''}
      `;

      resultsList.appendChild(card);
    });
  }

  function extractVideoId(url) {
    const match = url.match(/(?:v=|\/)([0-9A-Za-z_-]{11})/);
    return match ? match[1] : null;
  }

  function parseHmsToSeconds(hms) {
    const parts = hms.split(':').map(Number);
    if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
    if (parts.length === 2) return parts[0] * 60 + parts[1];
    return parts[0] || 0;
  }

  function setLoading(isLoading) {
    searchBtn.disabled = isLoading;
    btnText.textContent = isLoading ? 'Extracting...' : 'Search';
    btnLoader.style.display = isLoading ? 'inline-block' : 'none';
  }

  function showError(msg) {
    errorMessage.textContent = msg;
    errorMessage.style.display = 'block';
  }

  function clearError() {
    errorMessage.textContent = '';
    errorMessage.style.display = 'none';
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});