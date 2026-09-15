(() => {
  "use strict";
  for (const button of document.querySelectorAll("[data-copy-prompt]")) {
    button.hidden = false;
    button.addEventListener("click", async () => {
      const source = document.getElementById(button.dataset.copyPrompt);
      const status = document.getElementById(button.dataset.copyStatus);
      if (!source || !status) return;
      try {
        await navigator.clipboard.writeText(source.textContent);
        status.textContent = button.dataset.copySuccess;
      } catch {
        const disclosure = source.closest("details");
        if (disclosure) disclosure.open = true;
        source.focus();
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(source);
        selection?.removeAllRanges();
        selection?.addRange(range);
        status.textContent = button.dataset.copyFailure;
      }
    });
  }
})();
