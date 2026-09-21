const display = document.getElementById('expression');
const keys = document.querySelectorAll('.key[data-value]');
const clearBtn = document.querySelector('[data-action="clear"]');
const delBtn = document.querySelector('[data-action="del"]');
const form = document.getElementById('calc-form');

keys.forEach((key) => {
  key.addEventListener('click', () => {
    display.value += key.dataset.value;
    display.focus();
  });
});

clearBtn.addEventListener('click', () => {
  display.value = '';
  display.focus();
});

delBtn.addEventListener('click', () => {
  display.value = display.value.slice(0, -1);
  display.focus();
});

// Allow typing directly + Enter key to submit
display.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    form.submit();
  }
});

// Auto-focus the display on load
window.addEventListener('load', () => display.focus());