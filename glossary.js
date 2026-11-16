for (const glossary of document.querySelectorAll('[data-glossary]')) {
  const search = glossary.querySelector('input[type="search"]');
  const clear = glossary.querySelector('[data-glossary-clear]');
  const status = glossary.querySelector('[data-glossary-status]');
  const entries = Array.from(glossary.querySelectorAll('dl > div'));
  const labels = entries.map(entry => (entry.textContent + ' ' + (entry.dataset.keywords || '')).toLowerCase());

  function filterGlossary() {
    const terms = search.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    let matches = 0;
    for (const [index, entry] of entries.entries()) {
      entry.hidden = !terms.every(term => labels[index].includes(term));
      if (!entry.hidden) matches++;
    }
    clear.disabled = !search.value;
    status.textContent = matches
      ? matches + (matches === 1 ? ' term shown.' : ' terms shown.')
      : 'No matching terms. Try “odds”, “EMA”, or “settlement”.';
  }

  search.addEventListener('input', filterGlossary);
  clear.addEventListener('click', () => {
    search.value = '';
    filterGlossary();
    search.focus();
  });
  glossary.querySelector('[data-glossary-controls]').hidden = false;
  filterGlossary();
}
