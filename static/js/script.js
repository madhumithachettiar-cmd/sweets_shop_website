const searchForm = document.getElementById("searchForm");
const searchInput = document.getElementById("searchInput");
const productGrid = document.getElementById("productGrid");
const cards = Array.from(document.querySelectorAll(".product-card"));
const groups = Array.from(document.querySelectorAll(".menu-group"));
const noResults = document.getElementById("noResults");
const navChips = Array.from(document.querySelectorAll(".nav-chip"));
const showcaseButtons = Array.from(document.querySelectorAll("[data-jump-btn]"));
const heroSlider = document.querySelector("[data-hero-slider]");

let currentCategory = "all";

function scrollToMenu() {
    document.getElementById("menu").scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}

function applyFilters() {
    const query = searchInput.value.trim().toLowerCase();
    let visibleCount = 0;

    cards.forEach((card) => {
        const name = card.dataset.name;
        const category = card.dataset.category;

        const matchesSearch = name.includes(query);
        const matchesCategory =
            currentCategory === "all" || category === currentCategory;

        const show = matchesSearch && matchesCategory;
        card.classList.toggle("hidden", !show);

        if (show) {
            visibleCount += 1;
        }
    });

    groups.forEach((group) => {
        const groupCategory = group.dataset.categoryGroup;
        const hasVisibleCard = cards.some(
            (card) =>
                card.dataset.category === groupCategory &&
                !card.classList.contains("hidden")
        );

        group.classList.toggle("hidden", !hasVisibleCard);
    });

    noResults.classList.toggle("hidden", visibleCount !== 0);
}

searchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    applyFilters();
    scrollToMenu();
});

searchInput.addEventListener("input", () => {
    applyFilters();

    if (searchInput.value.trim()) {
        scrollToMenu();
    }
});

navChips.forEach((chip) => {
    chip.addEventListener("click", () => {
        navChips.forEach((btn) => btn.classList.remove("active"));
        chip.classList.add("active");

        currentCategory = chip.dataset.filter;
        applyFilters();
        scrollToMenu();
    });
});

showcaseButtons.forEach((button) => {
    button.addEventListener("click", () => {
        const target = button.dataset.jumpBtn;

        navChips.forEach((btn) => btn.classList.remove("active"));

        const matchedChip = navChips.find((chip) => chip.dataset.filter === target);

        if (matchedChip) {
            matchedChip.classList.add("active");
        }

        currentCategory = target;
        applyFilters();
        scrollToMenu();
    });
});

if (heroSlider) {
    const track = heroSlider.querySelector(".hero-slider-track");
    const slides = Array.from(heroSlider.querySelectorAll(".hero-slide"));
    const dots = Array.from(heroSlider.querySelectorAll("[data-hero-dot]"));
    const prevButton = heroSlider.querySelector("[data-hero-prev]");
    const nextButton = heroSlider.querySelector("[data-hero-next]");
    let currentSlide = 0;
    let autoplayId = null;

    function renderHeroSlide(index) {
        currentSlide = (index + slides.length) % slides.length;
        track.style.transform = `translateX(-${currentSlide * 100}%)`;

        slides.forEach((slide, slideIndex) => {
            slide.classList.toggle("is-active", slideIndex === currentSlide);
        });

        dots.forEach((dot, dotIndex) => {
            dot.classList.toggle("is-active", dotIndex === currentSlide);
        });
    }

    function startHeroAutoplay() {
        if (slides.length < 2) {
            return;
        }

        stopHeroAutoplay();
        autoplayId = window.setInterval(() => {
            renderHeroSlide(currentSlide + 1);
        }, 4200);
    }

    function stopHeroAutoplay() {
        if (autoplayId) {
            window.clearInterval(autoplayId);
            autoplayId = null;
        }
    }

    prevButton?.addEventListener("click", () => {
        renderHeroSlide(currentSlide - 1);
        startHeroAutoplay();
    });

    nextButton?.addEventListener("click", () => {
        renderHeroSlide(currentSlide + 1);
        startHeroAutoplay();
    });

    dots.forEach((dot, index) => {
        dot.addEventListener("click", () => {
            renderHeroSlide(index);
            startHeroAutoplay();
        });
    });

    heroSlider.addEventListener("mouseenter", stopHeroAutoplay);
    heroSlider.addEventListener("mouseleave", startHeroAutoplay);

    renderHeroSlide(0);
    startHeroAutoplay();
}

applyFilters();
