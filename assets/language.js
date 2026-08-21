(() => {
  "use strict";

  const supportedLanguages = ["ko", "en", "ja"];
  const panels = Array.from(document.querySelectorAll(".language-panel"));
  const languageLinks = Array.from(document.querySelectorAll("[data-language-link]"));

  if (panels.length === 0 || languageLinks.length === 0) {
    return;
  }

  const languageFromHash = () => {
    const candidate = window.location.hash.slice(1).toLowerCase();
    const match = candidate.match(/^(ko|en|ja)(?:-|$)/);
    return match ? match[1] : null;
  };

  const preferredLanguage = () => {
    const preferences = Array.isArray(navigator.languages) && navigator.languages.length > 0
      ? navigator.languages
      : [navigator.language];

    for (const preference of preferences) {
      const language = String(preference || "").toLowerCase().split("-")[0];
      if (supportedLanguages.includes(language)) {
        return language;
      }
    }

    return "ko";
  };

  let initialized = false;

  const restoreHashPosition = () => {
    if (/^#(ko|en|ja)$/.test(window.location.hash)) {
      window.requestAnimationFrame(() => {
        window.requestAnimationFrame(() => window.scrollTo({ top: 0, left: 0, behavior: "auto" }));
      });
      return;
    }

    if (languageFromHash()) {
      const target = document.getElementById(window.location.hash.slice(1));
      if (target) {
        window.requestAnimationFrame(() => {
          window.requestAnimationFrame(() => target.scrollIntoView({ block: "start" }));
        });
      }
    }
  };

  const showLanguage = () => {
    const hashLanguage = languageFromHash();
    const currentLanguage = supportedLanguages.includes(document.documentElement.lang)
      ? document.documentElement.lang
      : null;
    const language = hashLanguage || (initialized ? currentLanguage : null) || preferredLanguage();

    if (window.location.hash === "" || (!initialized && hashLanguage === null)) {
      window.history.replaceState(null, "", `#${language}`);
    }

    document.documentElement.lang = language;
    for (const link of document.querySelectorAll("[data-language-path]")) {
      link.setAttribute("href", `${link.dataset.languagePath}#${language}`);
    }

    for (const panel of panels) {
      const isCurrent = panel.dataset.language === language;
      panel.hidden = !isCurrent;
      panel.classList.toggle("is-active", isCurrent);
      if (isCurrent && panel.dataset.documentTitle) {
        document.title = panel.dataset.documentTitle;
      }
    }

    for (const link of languageLinks) {
      const isCurrent = link.dataset.languageLink === language;
      if (isCurrent) {
        link.setAttribute("aria-current", "true");
      } else {
        link.removeAttribute("aria-current");
      }
    }

    restoreHashPosition();

    initialized = true;
  };

  window.addEventListener("hashchange", showLanguage);
  window.addEventListener("load", restoreHashPosition, { once: true });
  showLanguage();
})();
