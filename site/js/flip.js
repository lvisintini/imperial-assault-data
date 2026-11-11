// A card that turns over (views.js flipCard): its button shows the other side, a card's back or a hero's wounded
// side, with a turn (style.css; none for those who'd rather not have motion). The side facing away is inert, so its
// link can't be clicked or tabbed to.
export function initFlip(root) {
  root.addEventListener('click', event => {
    const button = event.target.closest('[data-flip-toggle]');
    if (!button) return;
    const card = button.closest('[data-flip]');
    const flipped = card.classList.toggle('flipped');
    card.querySelector('.flip-front').inert = flipped;
    card.querySelector('.flip-back').inert = !flipped;
    button.setAttribute('aria-pressed', String(flipped));
    button.querySelector('[data-flip-label]').textContent = button.dataset[flipped ? 'back' : 'front'];
  });
}
