const motionSwitch = document.querySelector('#motion-switch');
const motionNote = document.querySelector('#motion-note');
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');
const motionKey = 'pulse-preview-background-paused';
let backgroundPaused = false;

try {
  backgroundPaused = localStorage.getItem(motionKey) === 'true';
} catch {
  // Motion can still be paused for this page.
}

function updateMotion() {
  document.documentElement.classList.toggle('background-paused', backgroundPaused);
  motionSwitch.checked = backgroundPaused || reduceMotion.matches;
  motionSwitch.disabled = reduceMotion.matches;
  motionNote.textContent = reduceMotion.matches ? 'Your device is set to reduce motion.' : '';
}

motionSwitch.addEventListener('change', () => {
  backgroundPaused = motionSwitch.checked;
  try {
    localStorage.setItem(motionKey, String(backgroundPaused));
  } catch {
    // The setting remains usable for the current page.
  }
  updateMotion();
});
reduceMotion.addEventListener('change', updateMotion);
document.querySelector('#motion-options').hidden = false;
updateMotion();
