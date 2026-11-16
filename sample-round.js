const sampleStates = {
  up: {
    call: 'UP', up: 62, explanation: 'In this example, the UP quote moved higher.',
    trend: 'Example of BTC moving higher', bars: [27, 34, 30, 45, 50, 43, 59, 62, 55, 74, 80, 76, 88]
  },
  down: {
    call: 'DOWN', up: 38, explanation: 'In this example, the DOWN quote moved higher.',
    trend: 'Example of BTC moving lower', bars: [88, 83, 74, 76, 60, 63, 56, 43, 49, 36, 35, 24, 28]
  },
  neutral: {
    call: 'NO READ', up: 50, explanation: 'In this example, the quotes show no clear direction.',
    trend: 'Example of BTC moving sideways', bars: [53, 60, 49, 53, 45, 50, 55, 63, 58, 44, 49, 59, 53]
  }
};

const sampleControls = document.querySelector('#sample-controls');
const sampleCall = document.querySelector('#sample-call');
const sampleClock = document.querySelector('#sample-clock');
const sampleClockButton = document.querySelector('#sample-play');
const sampleClockStatus = document.querySelector('#sample-clock-status');
const samplePlot = document.querySelector('.sample-plot');
const samplePlotCaption = document.querySelector('#sample-plot-caption');
const sampleSeconds = 138;
let remaining = sampleSeconds;
let endsAt = 0;
let interval = 0;

function renderClock() {
  const minutes = Math.floor(remaining / 60);
  sampleClock.textContent = minutes + ':' + String(remaining % 60).padStart(2, '0');
}

function pauseClock(status) {
  clearInterval(interval);
  interval = 0;
  sampleClockButton.textContent = remaining ? 'Play countdown' : 'Replay countdown';
  sampleClockStatus.textContent = status;
}

function tickClock() {
  remaining = Math.max(0, Math.ceil((endsAt - Date.now()) / 1000));
  renderClock();
  if (!remaining) pauseClock('Example countdown finished.');
}

sampleClockButton.addEventListener('click', () => {
  if (interval) {
    tickClock();
    if (interval) pauseClock('Example countdown paused.');
    return;
  }
  if (!remaining) remaining = sampleSeconds;
  endsAt = Date.now() + remaining * 1000;
  interval = setInterval(tickClock, 250);
  sampleClockButton.textContent = 'Pause countdown';
  sampleClockStatus.textContent = 'Example countdown playing.';
  renderClock();
});

document.querySelector('#sample-reset').addEventListener('click', () => {
  remaining = sampleSeconds;
  pauseClock('Example countdown reset.');
  renderClock();
});

sampleControls.addEventListener('change', event => {
  const selected = sampleStates[event.target.value];
  if (!selected) return;
  sampleCall.className = 'read direction-' + event.target.value;
  sampleCall.textContent = selected.call;
  document.querySelector('#sample-reason').textContent = selected.explanation;
  document.querySelector('#sample-up').textContent = selected.up + '¢ UP';
  document.querySelector('#sample-down').textContent = (100 - selected.up) + '¢ DOWN';
  samplePlot.setAttribute('aria-label', selected.trend);
  samplePlotCaption.textContent = selected.trend + ' during a sample round. Illustrative data.';
  for (const [index, bar] of Array.from(samplePlot.children).entries()) {
    bar.style.setProperty('--size', selected.bars[index] + '%');
    bar.classList.toggle('sample-lower', index > 0 && selected.bars[index] < selected.bars[index - 1]);
  }
  samplePlot.classList.add('sample-driven');
});

sampleControls.hidden = false;
document.querySelector('#sample-clock-tools').hidden = false;
