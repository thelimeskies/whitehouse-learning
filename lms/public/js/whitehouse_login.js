(function () {
	"use strict";

	const LOGIN_PATH = "/login";
	const AUTH_SECTION_SELECTOR = [
		".for-login",
		".for-signup",
		".for-forgot",
		".for-login-with-email-link",
	].join(", ");

	function createFeature(text) {
		const item = document.createElement("li");
		const marker = document.createElement("span");
		const label = document.createElement("span");

		marker.className = "whitehouse-auth-feature-marker";
		marker.setAttribute("aria-hidden", "true");
		label.textContent = text;
		item.append(marker, label);
		return item;
	}

	function createStoryPanel() {
		const panel = document.createElement("aside");
		panel.className = "whitehouse-auth-story";
		panel.setAttribute("aria-label", "About Whitehouse Learning");

		const brand = document.createElement("div");
		brand.className = "whitehouse-auth-brand";

		const logo = document.createElement("img");
		logo.src = "/assets/lms/images/whitehouse-learning-mark.png";
		logo.alt = "";
		logo.width = 42;
		logo.height = 42;

		const brandName = document.createElement("span");
		brandName.textContent = "Whitehouse Learning";
		brand.append(logo, brandName);

		const content = document.createElement("div");
		content.className = "whitehouse-auth-story-content";

		const eyebrow = document.createElement("p");
		eyebrow.className = "whitehouse-auth-eyebrow";
		eyebrow.textContent = "Your professional learning space";

		const title = document.createElement("h1");
		title.textContent = "Turn ambition into measurable progress.";

		const description = document.createElement("p");
		description.className = "whitehouse-auth-description";
		description.textContent =
			"Build practical knowledge through focused courses, guided development, and achievements you can carry forward.";

		const features = document.createElement("ul");
		features.className = "whitehouse-auth-features";
		features.append(
			createFeature("Curated learning paths"),
			createFeature("Progress you can track"),
			createFeature("Certificates that count")
		);

		content.append(eyebrow, title, description, features);

		const accessNote = document.createElement("p");
		accessNote.className = "whitehouse-auth-access-note";
		accessNote.textContent = "Secure access for invited learners and administrators.";

		panel.append(brand, content, accessNote);
		return panel;
	}

	function enhanceLoginPage() {
		if (window.location.pathname.replace(/\/$/, "") !== LOGIN_PATH) return;
		if (document.body.dataset.whitehouseLoginReady === "true") return;

		const pageContent = document.querySelector(".page_content");
		const firstAuthSection = pageContent?.querySelector(AUTH_SECTION_SELECTOR);
		const sectionContainer = firstAuthSection?.parentElement;
		if (!pageContent || !sectionContainer) return;

		document.body.dataset.whitehouseLoginReady = "true";
		document.body.classList.add("whitehouse-login-page");

		const shell = document.createElement("div");
		shell.className = "whitehouse-auth-shell";

		const formPanel = document.createElement("div");
		formPanel.className = "whitehouse-auth-form-panel";

		const mobileBrand = document.createElement("div");
		mobileBrand.className = "whitehouse-auth-mobile-brand";
		mobileBrand.innerHTML =
			'<img src="/assets/lms/images/whitehouse-learning-mark.png" alt="" width="36" height="36"><span>Whitehouse Learning</span>';
		formPanel.append(mobileBrand);

		Array.from(sectionContainer.querySelectorAll(":scope > section")).forEach((section) => {
			if (section.matches(AUTH_SECTION_SELECTOR)) formPanel.append(section);
		});

		shell.append(createStoryPanel(), formPanel);
		sectionContainer.append(shell);
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", enhanceLoginPage, { once: true });
	} else {
		enhanceLoginPage();
	}
})();
