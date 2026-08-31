(() => {
  "use strict";

  const panels = Array.from(document.querySelectorAll(".language-panel"));
  const languageLinks = Array.from(document.querySelectorAll("[data-language-link]"));
  const localizedSkipLinks = Array.from(document.querySelectorAll("[data-language-skip]"));
  const supportedLanguages = languageLinks
    .map((link) => link.dataset.languageLink)
    .filter((language, index, languages) => language && languages.indexOf(language) === index);

  if (panels.length === 0 || languageLinks.length === 0) {
    return;
  }

  const normalized = (language) => String(language || "").replaceAll("_", "-").toLowerCase();
  const decodedHash = () => {
    const value = window.location.hash.slice(1);
    try {
      return decodeURIComponent(value);
    } catch {
      return value;
    }
  };
  const supportedByNormalizedTag = new Map(
    supportedLanguages.map((language) => [normalized(language), language]),
  );

  const languageFromTag = (tag) => {
    const candidate = normalized(tag);
    const exact = supportedByNormalizedTag.get(candidate);
    if (exact) {
      return exact;
    }

    const parts = candidate.split("-");
    const base = parts[0];
    if (base === "zh") {
      const traditional = parts.includes("hant") || ["hk", "mo", "tw"].some((part) => parts.includes(part));
      return supportedByNormalizedTag.get(traditional ? "zh-hant" : "zh-hans") || null;
    }
    if (base === "pt") {
      return supportedByNormalizedTag.get(parts.includes("br") ? "pt-br" : "pt-pt") || null;
    }

    return supportedByNormalizedTag.get(base) || null;
  };

  const languageFromHash = () => {
    const candidate = normalized(decodedHash());
    return supportedLanguages
      .slice()
      .sort((left, right) => right.length - left.length)
      .find((language) => {
        const tag = normalized(language);
        return candidate === tag || candidate.startsWith(`${tag}-`);
      }) || null;
  };

  const preferredLanguage = () => {
    const preferences = Array.isArray(navigator.languages) && navigator.languages.length > 0
      ? navigator.languages
      : [navigator.language];

    for (const preference of preferences) {
      const language = languageFromTag(preference);
      if (language) {
        return language;
      }
    }

    return "ko";
  };

  let initialized = false;

  const restoreHashPosition = () => {
    const hashLanguage = languageFromHash();
    if (hashLanguage && normalized(decodedHash()) === normalized(hashLanguage)) {
      window.requestAnimationFrame(() => {
        window.requestAnimationFrame(() => window.scrollTo({ top: 0, left: 0, behavior: "auto" }));
      });
      return;
    }

    if (languageFromHash()) {
      const target = document.getElementById(decodedHash());
      if (target) {
        window.requestAnimationFrame(() => {
          window.requestAnimationFrame(() => {
            if (target.hasAttribute("data-skip-target")) {
              target.focus({ preventScroll: true });
            }
            target.scrollIntoView({ block: "start" });
          });
        });
      }
    }
  };

  const showLanguage = () => {
    const hashLanguage = languageFromHash();
    const currentLanguage = languageFromTag(document.documentElement.lang);
    const language = hashLanguage || (initialized ? currentLanguage : null) || preferredLanguage();

    if (window.location.hash === "" || (!initialized && hashLanguage === null)) {
      window.history.replaceState(null, "", `#${language}`);
    }

    document.documentElement.lang = language;
    const activePanel = panels.find((panel) => panel.dataset.language === language);
    document.documentElement.dir = activePanel?.getAttribute("dir") || "ltr";
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

    let activeLanguageLink = null;
    for (const link of languageLinks) {
      const isCurrent = link.dataset.languageLink === language;
      if (isCurrent) {
        link.setAttribute("aria-current", "true");
        activeLanguageLink = link;
      } else {
        link.removeAttribute("aria-current");
      }
    }

    for (const link of localizedSkipLinks) {
      const isCurrent = link.dataset.languageSkip === language;
      link.hidden = !isCurrent;
      link.classList.toggle("is-active", isCurrent);
    }

    if (activeLanguageLink?.closest(".many-languages")) {
      window.requestAnimationFrame(() => {
        activeLanguageLink.scrollIntoView({ block: "nearest", inline: "nearest" });
      });
    }

    restoreHashPosition();

    initialized = true;
  };

  window.addEventListener("hashchange", showLanguage);
  window.addEventListener("load", restoreHashPosition, { once: true });
  showLanguage();
})();
