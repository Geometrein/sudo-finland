document.addEventListener('DOMContentLoaded', function() {
    fetch('data/data.yaml')
        .then(response => response.text())
        .then(yaml => jsyaml.load(yaml))
        .then(data => {
            createCards(data.companies);
            createStackFilters(data.companies);
        })
        .catch(error => console.error('Error loading YAML data:', error));
});

function createCards(companies) {
    const cardsContainer = document.getElementById('cards');
    companies.forEach((company, index) => {
        const card = document.createElement('div');
        card.className = `card card-${(index % 5) + 1}`;
        const stackHTML = company.stack.map(framework => `<img alt="" class="image" src="https://img.shields.io/badge/${encodeURIComponent(framework)}-rgba(0, 0, 0, 0)?style=for-the-badge&logo=${encodeURIComponent(framework)}&logoColor=#">`).join(' ');
        card.innerHTML = `
            <h2 class="card__title">${company.name}</h2>
            <p class="card__description">${company.description}</p>
            <div class="card__stack"><p>${stackHTML}</p></div>
            <p class="card__website">
                <a class="card__link" href="${company.website}" target="_blank">Website <i class="fas fa-arrow-right"></i></a>
            </p>
        `;
        cardsContainer.appendChild(card);
    });
}

function createStackFilters(companies) {
    const stackMap = new Map();
    companies.forEach(company => {
        company.stack.forEach(stack => {
            if (stackMap.has(stack)) {
                stackMap.set(stack, stackMap.get(stack) + 1);
            } else {
                stackMap.set(stack, 1);
            }
        });
    });

    const stackFilters = document.getElementById('stackFilters');
    stackMap.forEach((count, stack) => {
        if (count >= 15) {
            const label = document.createElement('label');
            const checkbox = document.createElement('input');
            const span = document.createElement('span');
            checkbox.type = 'checkbox';
            checkbox.name = 'stackFilter';
            checkbox.value = stack;
            checkbox.onclick = filterCards;
            label.appendChild(checkbox);
            label.appendChild(span);
            label.appendChild(document.createTextNode(stack));
            label.className = 'checkbox-container';
            span.className = 'checkmark';
            stackFilters.appendChild(label);
            stackFilters.appendChild(document.createElement('br'));
        }
    });
}

function filterCards() {
    const selectedStacks = Array.from(document.querySelectorAll('input[name="stackFilter"]:checked')).map(input => input.value);
    const cards = document.querySelectorAll('.card');

    cards.forEach(card => {
        const stack = Array.from(card.querySelectorAll('.image')).map(img => decodeURIComponent(img.src.split('badge/')[1].split('-')[0]));
        const isMatch = selectedStacks.every(selStack => stack.includes(selStack));
        card.style.display = isMatch ? '' : 'none';
    });
}

function searchCards() {
    const input = document.getElementById('searchInput').value.toLowerCase();
    const cards = document.querySelectorAll('.card');

    cards.forEach(card => {
        const title = card.querySelector('.card__title').textContent.toLowerCase();
        card.style.display = title.includes(input) ? '' : 'none';
    });
}